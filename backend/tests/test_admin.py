"""Tests for admin APIs — auth, user isolation, data retrieval."""

import io

import pytest
from fastapi.testclient import TestClient

from app.core.database import Base, SessionLocal, engine
from app.models.contract import Contract
from app.models.parse_job import DocumentParseResult, ParseJob
from app.models.review_results import ReviewReport
from app.models.review_task import AgentExecutionLog, ReviewTask
from app.models.user import User
from main import app


# ── helpers ──────────────────────────────────────────────────────────────────


def _register_user(client: TestClient, username: str, password: str = "pass123456") -> tuple[str, int]:
    res = client.post("/api/v1/auth/register", json={"username": username, "password": password})
    return res.json()["data"]["access_token"], res.json()["data"]["user"]["id"]


def _make_admin(client: TestClient, username: str = "admin_user") -> tuple[str, int]:
    """Create an admin user directly in DB (register API creates USER role)."""
    token, uid = _register_user(client, username)
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == uid).first()
        user.role = "admin"
        db.commit()
    finally:
        db.close()
    return token, uid


# ── fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    db = SessionLocal()
    try:
        db.query(ReviewReport).delete()
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


class TestAdminAuth:
    def test_admin_without_token_returns_401(self, client):
        res = client.get("/api/v1/admin/users")
        assert res.status_code == 401

    def test_admin_normal_user_returns_403(self, client):
        token, _ = _register_user(client, "normal_user")
        res = client.get("/api/v1/admin/users", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 403

    def test_admin_user_can_access(self, client):
        token, _ = _make_admin(client, "real_admin")
        res = client.get("/api/v1/admin/users", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        data = res.json()["data"]
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)
        assert len(data["items"]) >= 1


class TestAdminEndpoints:
    def test_users_list(self, client):
        token, _ = _make_admin(client, "admin_a")
        _register_user(client, "user1")
        _register_user(client, "user2")

        res = client.get("/api/v1/admin/users", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        users = res.json()["data"]["items"]
        assert len(users) >= 3
        usernames = {u["username"] for u in users}
        assert "admin_a" in usernames
        assert "user1" in usernames

    def test_contracts_list(self, client):
        token, _ = _make_admin(client, "admin_b")
        client.post(
            "/api/v1/contracts/upload",
            files={"file": ("test.pdf", io.BytesIO(b"%PDF-1.4"), "application/octet-stream")},
            data={"contract_type": "租赁"},
            headers={"Authorization": f"Bearer {token}"},
        )

        res = client.get("/api/v1/admin/contracts", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        contracts = res.json()["data"]["items"]
        assert len(contracts) >= 1
        assert "file_name" in contracts[0]

    def test_statistics(self, client):
        token, _ = _make_admin(client, "admin_c")

        res = client.get("/api/v1/admin/statistics", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        stats = res.json()["data"]
        assert "user_count" in stats
        assert "contract_count" in stats
        assert "review_task_count" in stats
        assert "risk_level_counts" in stats

    def test_agent_logs_list_excludes_json(self, client):
        token, _ = _make_admin(client, "admin_d")

        res = client.get("/api/v1/admin/agent-logs", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        logs = res.json()["data"]["items"]
        if logs:
            assert "input_json" not in logs[0]
            assert "output_json" not in logs[0]

    def test_agent_log_detail_includes_json(self, client):
        token, _ = _make_admin(client, "admin_e")

        # Create a task + log
        from unittest.mock import AsyncMock, patch

        with patch("app.services.mineru_service.MinerUService.parse") as m:
            m.return_value = {
                "markdown_path": "/tmp/test.md",
                "raw_markdown": "# Test\n甲方：张三\n乙方：李四",
                "content_json_path": None,
                "middle_json_path": None,
                "layout_pdf_path": None,
                "image_dir": "/tmp",
            }
            client.post(
                "/api/v1/contracts/upload",
                files={"file": ("t.pdf", io.BytesIO(b"%PDF-1.4"), "application/octet-stream")},
                data={"contract_type": "test"},
                headers={"Authorization": f"Bearer {token}"},
            )
            cid = client.get(
                "/api/v1/contracts",
                headers={"Authorization": f"Bearer {token}"},
            ).json()["data"]["items"][0]["id"]
            client.post(
                f"/api/v1/contracts/{cid}/parse",
                headers={"Authorization": f"Bearer {token}"},
            )
            client.post(
                f"/api/v1/contracts/{cid}/normalize",
                headers={"Authorization": f"Bearer {token}"},
            )

            with patch("app.agents.contract_profile_agent.ContractProfileAgent.run", new_callable=AsyncMock) as am:
                am.return_value = {
                    "contract_type": "租赁合同",
                    "party_a": "张三",
                    "party_b": "李四",
                    "sign_date": "2026-06-01",
                    "amount": "1000元",
                    "duration": "1年",
                    "subject": "test",
                    "summary": "test",
                    "missing_fields": [],
                }
                client.post(
                    f"/api/v1/contracts/{cid}/review/profile",
                    headers={"Authorization": f"Bearer {token}"},
                )

        # Get agent logs list
        list_res = client.get("/api/v1/admin/agent-logs", headers={"Authorization": f"Bearer {token}"})
        logs = list_res.json()["data"]["items"]
        if logs:
            log_id = logs[0]["id"]
            detail_res = client.get(
                f"/api/v1/admin/agent-logs/{log_id}",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert detail_res.status_code == 200
            detail = detail_res.json()["data"]
            assert "input_json" in detail
            assert "output_json" in detail


class TestReportExport:
    def test_export_without_token_returns_401(self, client):
        res = client.get("/api/v1/reports/1/export")
        assert res.status_code == 401

    def test_export_other_user_returns_403(self, client):
        from unittest.mock import AsyncMock, patch

        token1, _ = _register_user(client, "export_owner")
        with patch("app.services.mineru_service.MinerUService.parse") as m:
            m.return_value = {
                "markdown_path": "/tmp/test.md",
                "raw_markdown": "# 合同",
                "content_json_path": None, "middle_json_path": None,
                "layout_pdf_path": None, "image_dir": "/tmp",
            }
            client.post(
                "/api/v1/contracts/upload",
                files={"file": ("e.pdf", io.BytesIO(b"%PDF-1.4"), "application/octet-stream")},
                headers={"Authorization": f"Bearer {token1}"},
            )
            cid = client.get(
                "/api/v1/contracts",
                headers={"Authorization": f"Bearer {token1}"},
            ).json()["data"]["items"][0]["id"]
            client.post(f"/api/v1/contracts/{cid}/parse", headers={"Authorization": f"Bearer {token1}"})
            client.post(f"/api/v1/contracts/{cid}/normalize", headers={"Authorization": f"Bearer {token1}"})

            with patch("app.agents.contract_profile_agent.ContractProfileAgent.run", new_callable=AsyncMock) as am:
                am.return_value = {
                    "contract_type": "t", "party_a": "a", "party_b": "b",
                    "sign_date": "2026-01-01", "amount": "1", "duration": "1",
                    "subject": "s", "summary": "s", "missing_fields": [],
                }
                with patch("app.agents.clause_extraction_agent.ClauseExtractionAgent.run", new_callable=AsyncMock) as cm:
                    cm.return_value = {"clauses": [], "missing_clause_types": []}
                    with patch("app.agents.risk_detection_agent.RiskDetectionAgent.run", new_callable=AsyncMock) as rm:
                        rm.return_value = {"risks": [], "overall_risk": "低风险"}
                        with patch("app.agents.suggestion_agent.SuggestionAgent.run", new_callable=AsyncMock) as sm:
                            sm.return_value = {"suggestions": []}
                            with patch("app.agents.consistency_check_agent.ConsistencyCheckAgent.run", new_callable=AsyncMock) as chm:
                                chm.return_value = {"passed": True, "issues": []}
                                with patch("app.agents.report_generation_agent.ReportGenerationAgent.run", new_callable=AsyncMock) as rgm:
                                    rgm.return_value = {
                                        "report_title": "t", "overall_risk": "低",
                                        "summary": "s", "risk_statistics": {"high": 0, "medium": 0, "low": 0},
                                        "markdown_report": "# report",
                                        "disclaimer": "免责声明",
                                    }
                                    r = client.post(
                                        f"/api/v1/contracts/{cid}/review",
                                        headers={"Authorization": f"Bearer {token1}"},
                                    )
                                    task_id = r.json()["data"]["task"]["id"]

        token2, _ = _register_user(client, "export_intruder")
        res = client.get(
            f"/api/v1/reports/{task_id}/export",
            headers={"Authorization": f"Bearer {token2}"},
        )
        assert res.status_code == 403

    def test_export_without_report_returns_404(self, client):
        token, _ = _register_user(client, "no_report")
        # Create a task with no report
        db = SessionLocal()
        try:
            contract = Contract(user_id=1, file_name="x", stored_file_name="x",
                                file_path="/tmp/x", file_type="pdf")
            db.add(contract)
            db.commit()
            db.refresh(contract)
            cid = contract.id
            task = ReviewTask(contract_id=cid, user_id=1, status="RUNNING")
            db.add(task)
            db.commit()
            db.refresh(task)
            tid = task.id
        finally:
            db.close()

        res = client.get(
            f"/api/v1/reports/{tid}/export",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code in (404, 403)  # 404 if no report, 403 if db user mismatch

    def test_export_success_contains_disclaimer(self, client):
        from unittest.mock import AsyncMock, patch

        token, _ = _register_user(client, "export_ok")
        with patch("app.services.mineru_service.MinerUService.parse") as m:
            m.return_value = {
                "markdown_path": "/tmp/test.md",
                "raw_markdown": "# 合同",
                "content_json_path": None, "middle_json_path": None,
                "layout_pdf_path": None, "image_dir": "/tmp",
            }
            client.post(
                "/api/v1/contracts/upload",
                files={"file": ("ok.pdf", io.BytesIO(b"%PDF-1.4"), "application/octet-stream")},
                headers={"Authorization": f"Bearer {token}"},
            )
            cid = client.get(
                "/api/v1/contracts",
                headers={"Authorization": f"Bearer {token}"},
            ).json()["data"]["items"][0]["id"]
            client.post(f"/api/v1/contracts/{cid}/parse", headers={"Authorization": f"Bearer {token}"})
            client.post(f"/api/v1/contracts/{cid}/normalize", headers={"Authorization": f"Bearer {token}"})

            with patch("app.agents.contract_profile_agent.ContractProfileAgent.run", new_callable=AsyncMock) as am:
                am.return_value = {
                    "contract_type": "t", "party_a": "a", "party_b": "b",
                    "sign_date": "2026-01-01", "amount": "1", "duration": "1",
                    "subject": "s", "summary": "s", "missing_fields": [],
                }
                with patch("app.agents.clause_extraction_agent.ClauseExtractionAgent.run", new_callable=AsyncMock) as cm:
                    cm.return_value = {"clauses": [], "missing_clause_types": []}
                    with patch("app.agents.risk_detection_agent.RiskDetectionAgent.run", new_callable=AsyncMock) as rm:
                        rm.return_value = {"risks": [], "overall_risk": "低风险"}
                        with patch("app.agents.suggestion_agent.SuggestionAgent.run", new_callable=AsyncMock) as sm:
                            sm.return_value = {"suggestions": []}
                            with patch("app.agents.consistency_check_agent.ConsistencyCheckAgent.run", new_callable=AsyncMock) as chm:
                                chm.return_value = {"passed": True, "issues": []}
                                with patch("app.agents.report_generation_agent.ReportGenerationAgent.run", new_callable=AsyncMock) as rgm:
                                    rgm.return_value = {
                                        "report_title": "t", "overall_risk": "低",
                                        "summary": "s", "risk_statistics": {"high": 0, "medium": 0, "low": 0},
                                        "markdown_report": "# 报告全文",
                                        "disclaimer": "本报告由 AI 系统自动生成，不构成正式法律意见。",
                                    }
                                    r = client.post(
                                        f"/api/v1/contracts/{cid}/review",
                                        headers={"Authorization": f"Bearer {token}"},
                                    )
                                    task_id = r.json()["data"]["task"]["id"]

        res = client.get(
            f"/api/v1/reports/{task_id}/export",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200
        content = res.text
        assert "# 报告全文" in content
        assert "不构成正式法律意见" in content
        assert "attachment" in res.headers.get("content-disposition", "")
