"""Review service: orchestrate agent execution and persist logs/results."""

import json
import time
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.agents.clause_extraction_agent import ClauseExtractionAgent
from app.agents.consistency_check_agent import ConsistencyCheckAgent
from app.agents.contract_profile_agent import ContractProfileAgent
from app.agents.llm_client import LLMClient
from app.agents.report_generation_agent import ReportGenerationAgent
from app.agents.risk_detection_agent import RiskDetectionAgent
from app.agents.suggestion_agent import SuggestionAgent
from app.core.exceptions import AppError
from app.models.contract import Contract
from app.models.parse_job import DocumentParseResult, ParseJob
from app.models.review_results import (
    ContractClause,
    ModifySuggestion,
    ReviewReport,
    RiskItem,
)
from app.models.review_task import AgentExecutionLog, ReviewTask

DISCLAIMER = (
    "本报告由 AI 系统自动生成，仅用于合同阅读辅助和风险提示，"
    "不构成正式法律意见。重要合同请咨询专业律师或法律顾问。"
)

AGENT_ORDER = [
    "ContractProfileAgent",
    "ClauseExtractionAgent",
    "RiskDetectionAgent",
    "SuggestionAgent",
    "ConsistencyCheckAgent",
    "ReportGenerationAgent",
]


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

    def _create_log(
        self, task_id: int, contract_id: int, agent_name: str, input_data: dict
    ) -> AgentExecutionLog:
        log = AgentExecutionLog(
            task_id=task_id,
            contract_id=contract_id,
            agent_name=agent_name,
            input_json=json.dumps(input_data, ensure_ascii=False),
            status="RUNNING",
            started_at=datetime.now(timezone.utc),
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def _finish_log_success(
        self, log: AgentExecutionLog, output: dict, start_ts: float
    ) -> None:
        log.output_json = json.dumps(output, ensure_ascii=False)
        log.status = "SUCCESS"
        log.duration_ms = int((time.monotonic() - start_ts) * 1000)
        log.finished_at = datetime.now(timezone.utc)
        self.db.commit()

    def _finish_log_failure(
        self, log: AgentExecutionLog, error_msg: str, start_ts: float
    ) -> None:
        log.status = "FAILED"
        log.error_message = error_msg
        log.duration_ms = int((time.monotonic() - start_ts) * 1000)
        log.finished_at = datetime.now(timezone.utc)
        self.db.commit()

    # ── profile-only (Phase 6) ───────────────────────────────────────────────

    async def run_profile_review(self, contract_id: int, user_id: int) -> dict:
        contract = self._get_contract(contract_id, user_id)
        normalized = self._get_normalized_json(contract_id)

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

        input_data = {
            "contract_document": normalized,
            "contract_type": contract.contract_type,
        }
        log = self._create_log(task.id, contract_id, "ContractProfileAgent", input_data)

        start_ts = time.monotonic()
        try:
            agent = ContractProfileAgent(llm_client=self.llm_client)
            output = await agent.run(input_data)
            self._finish_log_success(log, output, start_ts)
            task.status = "SUCCESS"
            task.finished_at = datetime.now(timezone.utc)
            self.db.commit()
            return {"task": task, "log": log, "profile": output}
        except Exception as exc:
            error_msg = str(exc)
            self._finish_log_failure(log, error_msg, start_ts)
            task.status = "FAILED"
            task.error_message = error_msg
            task.finished_at = datetime.now(timezone.utc)
            self.db.commit()
            raise

    # ── full review (Phase 7) ────────────────────────────────────────────────

    async def run_full_review(self, contract_id: int, user_id: int) -> dict:
        """Run the complete 6-agent review pipeline."""
        contract = self._get_contract(contract_id, user_id)
        normalized = self._get_normalized_json(contract_id)

        # Create task
        task = ReviewTask(
            contract_id=contract_id,
            user_id=user_id,
            status="RUNNING",
            current_step=AGENT_ORDER[0],
            started_at=datetime.now(timezone.utc),
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        results: dict = {}
        profile = None

        for i, agent_name in enumerate(AGENT_ORDER):
            task.current_step = agent_name
            self.db.commit()

            input_data = self._build_agent_input(agent_name, normalized, contract, results)
            log = self._create_log(task.id, contract_id, agent_name, input_data)

            start_ts = time.monotonic()
            try:
                agent = self._make_agent(agent_name)
                output = await agent.run(input_data)
                self._finish_log_success(log, output, start_ts)
                results[agent_name] = output
                if agent_name == "ContractProfileAgent":
                    profile = output
            except Exception as exc:
                error_msg = str(exc)
                self._finish_log_failure(log, error_msg, start_ts)
                task.status = "FAILED"
                task.error_message = f"{agent_name} 失败: {error_msg}"
                task.finished_at = datetime.now(timezone.utc)
                self.db.commit()
                raise AppError(
                    f"审查失败 ({agent_name}): {error_msg}", code=500, status_code=500
                )

        # All agents succeeded — persist results
        self._persist_clauses(task.id, contract_id, results)
        self._persist_risks(task.id, contract_id, results)
        self._persist_suggestions(task.id, contract_id, results)
        self._persist_report(task.id, contract_id, results)

        task.status = "SUCCESS"
        task.finished_at = datetime.now(timezone.utc)
        self.db.commit()

        return {"task": task, "profile": profile}

    def _build_agent_input(
        self, agent_name: str, normalized: dict, contract: Contract, results: dict
    ) -> dict:
        """Build input data for each agent based on what's been produced so far."""
        profile = results.get("ContractProfileAgent", {})
        clauses = results.get("ClauseExtractionAgent", {})
        risks = results.get("RiskDetectionAgent", {})
        suggestions = results.get("SuggestionAgent", {})

        if agent_name == "ContractProfileAgent":
            return {
                "contract_document": normalized,
                "contract_type": contract.contract_type,
            }
        elif agent_name == "ClauseExtractionAgent":
            return {
                "contract_document": normalized,
                "contract_profile": profile,
            }
        elif agent_name == "RiskDetectionAgent":
            return {"contract_profile": profile, "clauses": clauses}
        elif agent_name == "SuggestionAgent":
            return {"risks": risks, "clauses": clauses}
        elif agent_name == "ConsistencyCheckAgent":
            return {
                "contract_document": normalized,
                "profile": profile,
                "clauses": clauses,
                "risks": risks,
                "suggestions": suggestions,
            }
        elif agent_name == "ReportGenerationAgent":
            return {
                "profile": profile,
                "clauses": clauses,
                "risks": risks,
                "suggestions": suggestions,
                "check": results.get("ConsistencyCheckAgent", {}),
            }
        return {}

    def _make_agent(self, agent_name: str):
        agents = {
            "ContractProfileAgent": ContractProfileAgent,
            "ClauseExtractionAgent": ClauseExtractionAgent,
            "RiskDetectionAgent": RiskDetectionAgent,
            "SuggestionAgent": SuggestionAgent,
            "ConsistencyCheckAgent": ConsistencyCheckAgent,
            "ReportGenerationAgent": ReportGenerationAgent,
        }
        cls = agents.get(agent_name)
        if not cls:
            raise AppError(f"未知 Agent: {agent_name}", code=500, status_code=500)
        return cls(llm_client=self.llm_client)

    # ── persistence ──────────────────────────────────────────────────────────

    def _persist_clauses(self, task_id: int, contract_id: int, results: dict) -> None:
        clauses_data = results.get("ClauseExtractionAgent", {}).get("clauses", [])
        for i, c in enumerate(clauses_data):
            self.db.add(
                ContractClause(
                    task_id=task_id,
                    contract_id=contract_id,
                    clause_id=c.get("clause_id", f"C{i+1}"),
                    section_id=c.get("source_section_id"),
                    title=c.get("title", c.get("clause_type", "")),
                    text=c.get("content", c.get("text", "")),
                    clause_type=c.get("clause_type"),
                    page_number=c.get("page"),
                    source_text=c.get("content"),
                )
            )

    def _persist_risks(self, task_id: int, contract_id: int, results: dict) -> None:
        risks_data = results.get("RiskDetectionAgent", {}).get("risks", [])
        for r in risks_data:
            self.db.add(
                RiskItem(
                    task_id=task_id,
                    contract_id=contract_id,
                    risk_id=r.get("risk_id", ""),
                    clause_id=r.get("related_clause_id"),
                    risk_level=r.get("risk_level", "中风险"),
                    risk_type=r.get("risk_type", ""),
                    description=r.get("reason", r.get("impact", "")),
                    reason=r.get("reason", ""),
                    suggestion=r.get("impact", ""),
                    need_human_review=r.get("need_human_review", True),
                )
            )

    def _persist_suggestions(self, task_id: int, contract_id: int, results: dict) -> None:
        sug_data = results.get("SuggestionAgent", {}).get("suggestions", [])
        for s in sug_data:
            self.db.add(
                ModifySuggestion(
                    task_id=task_id,
                    contract_id=contract_id,
                    suggestion_id=s.get("suggestion_id", ""),
                    risk_id=s.get("risk_id"),
                    clause_id=None,
                    original_text=s.get("original_text", ""),
                    suggested_text=s.get("suggested_text", ""),
                    reason=s.get("reason", ""),
                )
            )

    def _persist_report(self, task_id: int, contract_id: int, results: dict) -> None:
        report_data = results.get("ReportGenerationAgent", {})
        self.db.add(
            ReviewReport(
                task_id=task_id,
                contract_id=contract_id,
                report_title=report_data.get("report_title", "合同智能审查报告"),
                overall_risk=report_data.get("overall_risk"),
                markdown_report=report_data.get("markdown_report", ""),
                disclaimer=report_data.get("disclaimer", DISCLAIMER),
            )
        )

    # ── query helpers ────────────────────────────────────────────────────────

    def get_task(self, task_id: int, user_id: int) -> ReviewTask:
        return self._get_task(task_id, user_id)

    def get_agent_logs(self, task_id: int, user_id: int) -> list[AgentExecutionLog]:
        self._get_task(task_id, user_id)
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

    def get_clauses(self, task_id: int, user_id: int) -> list[dict]:
        self._get_task(task_id, user_id)
        items = (
            self.db.query(ContractClause)
            .filter(ContractClause.task_id == task_id)
            .all()
        )
        return [
            {
                "id": c.id,
                "clause_id": c.clause_id,
                "section_id": c.section_id,
                "title": c.title,
                "text": c.text,
                "clause_type": c.clause_type,
                "page_number": c.page_number,
                "source_text": c.source_text,
            }
            for c in items
        ]

    def get_risks(self, task_id: int, user_id: int) -> list[dict]:
        self._get_task(task_id, user_id)
        items = (
            self.db.query(RiskItem)
            .filter(RiskItem.task_id == task_id)
            .all()
        )
        return [
            {
                "id": r.id,
                "risk_id": r.risk_id,
                "clause_id": r.clause_id,
                "risk_level": r.risk_level,
                "risk_type": r.risk_type,
                "description": r.description,
                "reason": r.reason,
                "suggestion": r.suggestion,
                "need_human_review": r.need_human_review,
            }
            for r in items
        ]

    def get_suggestions(self, task_id: int, user_id: int) -> list[dict]:
        self._get_task(task_id, user_id)
        items = (
            self.db.query(ModifySuggestion)
            .filter(ModifySuggestion.task_id == task_id)
            .all()
        )
        return [
            {
                "id": s.id,
                "suggestion_id": s.suggestion_id,
                "risk_id": s.risk_id,
                "clause_id": s.clause_id,
                "original_text": s.original_text,
                "suggested_text": s.suggested_text,
                "reason": s.reason,
            }
            for s in items
        ]

    def get_report(self, task_id: int, user_id: int) -> dict | None:
        self._get_task(task_id, user_id)
        report = (
            self.db.query(ReviewReport)
            .filter(ReviewReport.task_id == task_id)
            .first()
        )
        if not report:
            return None
        return {
            "id": report.id,
            "task_id": report.task_id,
            "report_title": report.report_title,
            "overall_risk": report.overall_risk,
            "markdown_report": report.markdown_report,
            "disclaimer": report.disclaimer,
        }
