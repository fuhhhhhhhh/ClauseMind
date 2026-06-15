"""API integration tests for full multi-agent review workflow."""

import io
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.core.database import Base, SessionLocal, engine
from app.models.contract import Contract
from app.models.parse_job import DocumentParseResult, ParseJob
from app.models.review_results import (
    ContractClause,
    ModifySuggestion,
    ReviewReport,
    RiskItem,
)
from app.models.review_task import AgentExecutionLog, ReviewTask
from app.models.user import User
from main import app


# ── mock agent outputs ───────────────────────────────────────────────────────

PROFILE_OUTPUT = {
    "contract_type": "房屋租赁合同",
    "party_a": "张三",
    "party_b": "李四",
    "sign_date": "2026-06-01",
    "amount": "3000元/月",
    "duration": "2026-06-01 至 2027-06-01",
    "subject": "房屋租赁",
    "summary": "租赁合同摘要",
    "missing_fields": [],
}

CLAUSE_OUTPUT = {
    "clauses": [
        {
            "clause_id": "C1",
            "clause_type": "主体条款",
            "title": "合同主体",
            "content": "甲方张三出租给乙方李四",
            "source_section_id": "S1",
            "page": 1,
            "status": "found",
        },
    ],
    "missing_clause_types": [],
}

RISK_OUTPUT = {
    "risks": [
        {
            "risk_id": "R1",
            "risk_level": "中风险",
            "risk_type": "违约责任模糊",
            "related_clause_id": "C1",
            "source_text": "原文",
            "reason": "违约责任不明确",
            "impact": "难以确定赔偿标准",
            "need_human_review": True,
        }
    ],
    "overall_risk": "中风险",
}

SUGGESTION_OUTPUT = {
    "suggestions": [
        {
            "suggestion_id": "SUG1",
            "risk_id": "R1",
            "original_text": "原文",
            "suggested_text": "建议修改",
            "reason": "增强明确性",
            "rewrite_type": "明确化",
        }
    ]
}

CHECK_OUTPUT = {"passed": True, "issues": []}

REPORT_OUTPUT = {
    "report_title": "合同智能审查报告",
    "overall_risk": "中风险",
    "summary": "摘要",
    "risk_statistics": {"high": 0, "medium": 1, "low": 0},
    "markdown_report": "# 合同审查报告\n\n免责声明...",
    "disclaimer": "本报告由 AI 系统自动生成，仅用于合同阅读辅助和风险提示，不构成正式法律意见。重要合同请咨询专业律师或法律顾问。",
}

SAMPLE_MD = "# 房屋租赁合同\n\n甲方：张三\n乙方：李四\n\n第一条 租赁房屋"


# ── helpers ──────────────────────────────────────────────────────────────────


def _register_and_upload(client: TestClient, username: str = "rv7user") -> tuple[str, int]:
    res = client.post(
        "/api/v1/auth/register",
        json={"username": username, "password": "pass123456"},
    )
    token = res.json()["data"]["access_token"]
    upload_res = client.post(
        "/api/v1/contracts/upload",
        files={"file": ("test.pdf", io.BytesIO(b"%PDF-1.4"), "application/octet-stream")},
        data={"contract_type": "租赁合同"},
        headers={"Authorization": f"Bearer {token}"},
    )
    return token, upload_res.json()["data"]["id"]


def _parse_and_normalize(client: TestClient, token: str, cid: int):
    with patch("app.services.mineru_service.MinerUService.parse") as mock:
        mock.return_value = {
            "markdown_path": "/tmp/test.md",
            "raw_markdown": SAMPLE_MD,
            "content_json_path": None,
            "middle_json_path": None,
            "layout_pdf_path": None,
            "image_dir": "/tmp",
        }
        client.post(
            f"/api/v1/contracts/{cid}/parse",
            headers={"Authorization": f"Bearer {token}"},
        )
    client.post(
        f"/api/v1/contracts/{cid}/normalize",
        headers={"Authorization": f"Bearer {token}"},
    )


def _mock_all_agents():
    """Patch all 6 agent .run methods to return canned outputs."""
    return [
        patch(
            "app.agents.contract_profile_agent.ContractProfileAgent.run",
            new_callable=AsyncMock,
            return_value=PROFILE_OUTPUT,
        ),
        patch(
            "app.agents.clause_extraction_agent.ClauseExtractionAgent.run",
            new_callable=AsyncMock,
            return_value=CLAUSE_OUTPUT,
        ),
        patch(
            "app.agents.risk_detection_agent.RiskDetectionAgent.run",
            new_callable=AsyncMock,
            return_value=RISK_OUTPUT,
        ),
        patch(
            "app.agents.suggestion_agent.SuggestionAgent.run",
            new_callable=AsyncMock,
            return_value=SUGGESTION_OUTPUT,
        ),
        patch(
            "app.agents.consistency_check_agent.ConsistencyCheckAgent.run",
            new_callable=AsyncMock,
            return_value=CHECK_OUTPUT,
        ),
        patch(
            "app.agents.report_generation_agent.ReportGenerationAgent.run",
            new_callable=AsyncMock,
            return_value=REPORT_OUTPUT,
        ),
    ]


# ── fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    db = SessionLocal()
    try:
        db.query(ReviewReport).delete()
        db.query(ModifySuggestion).delete()
        db.query(RiskItem).delete()
        db.query(ContractClause).delete()
        db.query(AgentExecutionLog).delete()
        db.query(ReviewTask).delete()
        db.query(DocumentParseResult).delete()
        db.query(ParseJob).delete()
        db.query(Contract).delete()
        db.query(User).delete()
        db.commit()
    finally:
        db.close()


@pytest.fixture
def client():
    return TestClient(app)


# ── tests ────────────────────────────────────────────────────────────────────


class TestFullReviewAuth:
    def test_full_review_without_token_returns_401(self, client):
        res = client.post("/api/v1/contracts/1/review")
        assert res.status_code == 401

    def test_full_review_other_user_returns_403(self, client):
        token1, cid = _register_and_upload(client, "owner_fr")
        _register_and_upload(client, "intruder_fr")
        login_res = client.post(
            "/api/v1/auth/login",
            json={"username": "intruder_fr", "password": "pass123456"},
        )
        token2 = login_res.json()["data"]["access_token"]
        res = client.post(
            f"/api/v1/contracts/{cid}/review",
            headers={"Authorization": f"Bearer {token2}"},
        )
        assert res.status_code == 403

    def test_full_review_no_normalized_json_returns_400(self, client):
        token, cid = _register_and_upload(client, "nonorm_fr")
        res = client.post(
            f"/api/v1/contracts/{cid}/review",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 400


class TestFullReviewFlow:
    def test_full_review_success(self, client):
        token, cid = _register_and_upload(client, "fullok")
        _parse_and_normalize(client, token, cid)

        patches = _mock_all_agents()
        for p in patches:
            p.start()

        try:
            res = client.post(
                f"/api/v1/contracts/{cid}/review",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert res.status_code == 200
            data = res.json()["data"]
            assert data["task"]["status"] == "SUCCESS"
            task_id = data["task"]["id"]

            # Verify 6 agent execution logs
            logs_res = client.get(
                f"/api/v1/review-tasks/{task_id}/agent-logs",
                headers={"Authorization": f"Bearer {token}"},
            )
            logs = logs_res.json()["data"]
            assert len(logs) == 6
            agent_names = {log["agent_name"] for log in logs}
            assert "ContractProfileAgent" in agent_names
            assert "ReportGenerationAgent" in agent_names

            # Verify clauses
            clauses_res = client.get(
                f"/api/v1/review-tasks/{task_id}/clauses",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert clauses_res.status_code == 200
            assert len(clauses_res.json()["data"]) >= 1

            # Verify risks
            risks_res = client.get(
                f"/api/v1/review-tasks/{task_id}/risks",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert risks_res.status_code == 200
            assert len(risks_res.json()["data"]) >= 1

            # Verify suggestions
            sug_res = client.get(
                f"/api/v1/review-tasks/{task_id}/suggestions",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert sug_res.status_code == 200
            assert len(sug_res.json()["data"]) >= 1

            # Verify report has disclaimer
            report_res = client.get(
                f"/api/v1/reports/{task_id}",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert report_res.status_code == 200
            report = report_res.json()["data"]
            assert "不构成正式法律意见" in report["disclaimer"]
        finally:
            for p in patches:
                p.stop()

    def test_mid_agent_failure_stops_pipeline(self, client):
        token, cid = _register_and_upload(client, "midfail")
        _parse_and_normalize(client, token, cid)

        # Mock: profile succeeds, clause extraction fails
        p1 = patch(
            "app.agents.contract_profile_agent.ContractProfileAgent.run",
            new_callable=AsyncMock,
            return_value=PROFILE_OUTPUT,
        )
        p2 = patch(
            "app.agents.clause_extraction_agent.ClauseExtractionAgent.run",
            new_callable=AsyncMock,
            side_effect=Exception("Clause extraction crashed"),
        )
        p1.start()
        p2.start()

        try:
            res = client.post(
                f"/api/v1/contracts/{cid}/review",
                headers={"Authorization": f"Bearer {token}"},
            )
            # Should return error (500 wrapped by AppError)
            assert res.status_code == 500

            # Verify task is FAILED
            task_res = client.get(
                "/api/v1/review-tasks/1",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert task_res.json()["data"]["status"] == "FAILED"
            assert "Clause" in task_res.json()["data"]["error_message"]
        finally:
            p1.stop()
            p2.stop()

    def test_result_endpoints_other_user_forbidden(self, client):
        token1, cid = _register_and_upload(client, "owner_fr2")
        _parse_and_normalize(client, token1, cid)

        patches = _mock_all_agents()
        for p in patches:
            p.start()

        try:
            res = client.post(
                f"/api/v1/contracts/{cid}/review",
                headers={"Authorization": f"Bearer {token1}"},
            )
            task_id = res.json()["data"]["task"]["id"]
        finally:
            for p in patches:
                p.stop()

        _register_and_upload(client, "intruder_fr2")
        login_res = client.post(
            "/api/v1/auth/login",
            json={"username": "intruder_fr2", "password": "pass123456"},
        )
        token2 = login_res.json()["data"]["access_token"]

        for endpoint in [
            f"/api/v1/review-tasks/{task_id}",
            f"/api/v1/review-tasks/{task_id}/progress",
            f"/api/v1/review-tasks/{task_id}/agent-logs",
            f"/api/v1/review-tasks/{task_id}/profile",
            f"/api/v1/review-tasks/{task_id}/clauses",
            f"/api/v1/review-tasks/{task_id}/risks",
            f"/api/v1/review-tasks/{task_id}/suggestions",
            f"/api/v1/reports/{task_id}",
        ]:
            resp = client.get(endpoint, headers={"Authorization": f"Bearer {token2}"})
            assert resp.status_code == 403, f"{endpoint} should return 403, got {resp.status_code}"
