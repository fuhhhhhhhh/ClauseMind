"""Review service: orchestrate agent execution and persist logs."""

import json
import time
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.agents.contract_profile_agent import ContractProfileAgent
from app.agents.llm_client import LLMClient
from app.core.exceptions import AppError
from app.models.contract import Contract
from app.models.parse_job import DocumentParseResult, ParseJob
from app.models.review_task import AgentExecutionLog, ReviewTask


class ReviewService:
    """Service for running review agents and managing task/execution state."""

    def __init__(self, db: Session, llm_client: LLMClient | None = None) -> None:
        self.db = db
        self.llm_client = llm_client or LLMClient()

    # ── helpers ──────────────────────────────────────────────────────────────

    def _get_contract(self, contract_id: int, user_id: int) -> Contract:
        contract = self.db.query(Contract).filter(Contract.id == contract_id).first()
        if not contract:
            raise AppError("合同不存在", code=404, status_code=404)
        if contract.user_id != user_id:
            raise AppError("无权访问该合同", code=403, status_code=403)
        return contract

    def _get_normalized_json(self, contract_id: int) -> dict:
        """Fetch the latest normalized_json for a contract."""
        job = (
            self.db.query(ParseJob)
            .filter(ParseJob.contract_id == contract_id)
            .order_by(ParseJob.created_at.desc())
            .first()
        )
        if not job:
            raise AppError("该合同尚未解析", code=400, status_code=400)

        result = (
            self.db.query(DocumentParseResult)
            .filter(DocumentParseResult.parse_job_id == job.id)
            .first()
        )
        if not result or not result.normalized_json:
            raise AppError("该合同尚未标准化，请先执行标准化", code=400, status_code=400)

        return json.loads(result.normalized_json)

    def _get_task(self, task_id: int, user_id: int) -> ReviewTask:
        task = self.db.query(ReviewTask).filter(ReviewTask.id == task_id).first()
        if not task:
            raise AppError("审查任务不存在", code=404, status_code=404)
        if task.user_id != user_id:
            raise AppError("无权访问该审查任务", code=403, status_code=403)
        return task

    # ── public API ───────────────────────────────────────────────────────────

    async def run_profile_review(
        self, contract_id: int, user_id: int
    ) -> dict:
        """Run ContractProfileAgent and persist results."""
        contract = self._get_contract(contract_id, user_id)
        normalized = self._get_normalized_json(contract_id)

        # Create review task
        task = ReviewTask(
            contract_id=contract_id,
            user_id=user_id,
            status="RUNNING",
            current_step="ContractProfileAgent",
            started_at=datetime.now(timezone.utc),
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        # Prepare input
        input_data = {
            "contract_document": normalized,
            "contract_type": contract.contract_type,
        }
        input_json = json.dumps(input_data, ensure_ascii=False)

        # Create execution log
        log = AgentExecutionLog(
            task_id=task.id,
            contract_id=contract_id,
            agent_name="ContractProfileAgent",
            input_json=input_json,
            status="RUNNING",
            started_at=datetime.now(timezone.utc),
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)

        # Execute agent
        start_ts = time.monotonic()
        try:
            agent = ContractProfileAgent(llm_client=self.llm_client)
            output = await agent.run(input_data)
            duration_ms = int((time.monotonic() - start_ts) * 1000)

            log.output_json = json.dumps(output, ensure_ascii=False)
            log.status = "SUCCESS"
            log.duration_ms = duration_ms
            log.finished_at = datetime.now(timezone.utc)

            task.status = "SUCCESS"
            task.finished_at = datetime.now(timezone.utc)

            self.db.commit()

            return {
                "task": task,
                "log": log,
                "profile": output,
            }

        except Exception as exc:
            duration_ms = int((time.monotonic() - start_ts) * 1000)
            error_msg = str(exc)

            log.status = "FAILED"
            log.error_message = error_msg
            log.duration_ms = duration_ms
            log.finished_at = datetime.now(timezone.utc)

            task.status = "FAILED"
            task.error_message = error_msg
            task.finished_at = datetime.now(timezone.utc)

            self.db.commit()
            raise

    # ── query helpers ────────────────────────────────────────────────────────

    def get_task(self, task_id: int, user_id: int) -> ReviewTask:
        return self._get_task(task_id, user_id)

    def get_agent_logs(self, task_id: int, user_id: int) -> list[AgentExecutionLog]:
        self._get_task(task_id, user_id)  # check auth
        return (
            self.db.query(AgentExecutionLog)
            .filter(AgentExecutionLog.task_id == task_id)
            .order_by(AgentExecutionLog.id)
            .all()
        )

    def get_profile_result(self, task_id: int, user_id: int) -> dict | None:
        self._get_task(task_id, user_id)
        log = (
            self.db.query(AgentExecutionLog)
            .filter(
                AgentExecutionLog.task_id == task_id,
                AgentExecutionLog.agent_name == "ContractProfileAgent",
                AgentExecutionLog.status == "SUCCESS",
            )
            .first()
        )
        if log and log.output_json:
            return json.loads(log.output_json)
        return None
