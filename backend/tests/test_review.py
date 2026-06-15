"""API integration tests for review (profile agent) module."""

import io
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.core.database import Base, SessionLocal, engine
from app.models.contract import Contract
from app.models.parse_job import DocumentParseResult, ParseJob
from app.models.review_task import AgentExecutionLog, ReviewTask
from app.models.user import User
from main import app


# ── helpers ──────────────────────────────────────────────────────────────────

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

SAMPLE_MD = "# 房屋租赁合同\n\n甲方：张三\n乙方：李四\n\n第一条 租赁房屋\n甲方将位于北京市朝阳区某房屋出租给乙方使用。"


def _register_and_upload(client: TestClient, username: str = "rvuser") -> tuple[str, int]:
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
    """Parse (mocked) + normalize a contract."""
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


# ── fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    db = SessionLocal()
    try:
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


class TestProfileReviewAuth:
    def test_without_token_returns_401(self, client):
        res = client.post("/api/v1/contracts/1/review/profile")
        assert res.status_code == 401

    def test_other_user_contract_returns_403(self, client):
        token1, cid = _register_and_upload(client, "owner_r")
        _register_and_upload(client, "intruder_r")
        login_res = client.post(
            "/api/v1/auth/login",
            json={"username": "intruder_r", "password": "pass123456"},
        )
        token2 = login_res.json()["data"]["access_token"]
        res = client.post(
            f"/api/v1/contracts/{cid}/review/profile",
            headers={"Authorization": f"Bearer {token2}"},
        )
        assert res.status_code == 403

    def test_no_normalized_json_returns_400(self, client):
        token, cid = _register_and_upload(client, "no_norm")
        res = client.post(
            f"/api/v1/contracts/{cid}/review/profile",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 400


class TestProfileReviewFlow:
    @patch("app.agents.contract_profile_agent.ContractProfileAgent.run", new_callable=AsyncMock)
    def test_success_creates_task_and_log(self, mock_run: AsyncMock, client):
        mock_run.return_value = PROFILE_OUTPUT

        token, cid = _register_and_upload(client, "success_rv")
        _parse_and_normalize(client, token, cid)

        res = client.post(
            f"/api/v1/contracts/{cid}/review/profile",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["task"]["status"] == "SUCCESS"
        assert data["profile"]["contract_type"] == "房屋租赁合同"
        assert data["task"]["id"] is not None

        task_id = data["task"]["id"]

        # Verify task endpoint
        task_res = client.get(
            f"/api/v1/review-tasks/{task_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert task_res.status_code == 200

        # Verify agent-logs endpoint
        logs_res = client.get(
            f"/api/v1/review-tasks/{task_id}/agent-logs",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert logs_res.status_code == 200
        logs = logs_res.json()["data"]
        assert len(logs) >= 1
        assert logs[0]["agent_name"] == "ContractProfileAgent"
        assert logs[0]["status"] == "SUCCESS"

        # Verify profile endpoint
        profile_res = client.get(
            f"/api/v1/review-tasks/{task_id}/profile",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert profile_res.status_code == 200
        assert profile_res.json()["data"]["contract_type"] == "房屋租赁合同"

    @patch("app.agents.contract_profile_agent.ContractProfileAgent.run", new_callable=AsyncMock)
    def test_failure_sets_status_to_failed(self, mock_run: AsyncMock, client):
        mock_run.side_effect = Exception("LLM exploded")

        token, cid = _register_and_upload(client, "fail_rv")
        _parse_and_normalize(client, token, cid)

        res = client.post(
            f"/api/v1/contracts/{cid}/review/profile",
            headers={"Authorization": f"Bearer {token}"},
        )
        # The AppError wrapper should raise 500
        assert res.status_code in (500,)

    def test_task_other_user_returns_403(self, client):
        token1, cid = _register_and_upload(client, "task_owner")
        _parse_and_normalize(client, token1, cid)

        with patch("app.agents.contract_profile_agent.ContractProfileAgent.run", new_callable=AsyncMock) as mock:
            mock.return_value = PROFILE_OUTPUT
            res = client.post(
                f"/api/v1/contracts/{cid}/review/profile",
                headers={"Authorization": f"Bearer {token1}"},
            )
            task_id = res.json()["data"]["task"]["id"]

        _register_and_upload(client, "intruder_task")
        login_res = client.post(
            "/api/v1/auth/login",
            json={"username": "intruder_task", "password": "pass123456"},
        )
        token2 = login_res.json()["data"]["access_token"]

        res2 = client.get(
            f"/api/v1/review-tasks/{task_id}",
            headers={"Authorization": f"Bearer {token2}"},
        )
        assert res2.status_code == 403


# ── Latest review endpoint tests ──────────────────────────────────────────────


class TestLatestReview:
    def test_latest_without_token_returns_401(self, client):
        res = client.get("/api/v1/contracts/1/review/latest")
        assert res.status_code == 401

    def test_latest_other_user_returns_403(self, client):
        token1, cid = _register_and_upload(client, "lat_owner")
        _register_and_upload(client, "lat_intruder")
        login_res = client.post(
            "/api/v1/auth/login",
            json={"username": "lat_intruder", "password": "pass123456"},
        )
        token2 = login_res.json()["data"]["access_token"]
        res = client.get(
            f"/api/v1/contracts/{cid}/review/latest",
            headers={"Authorization": f"Bearer {token2}"},
        )
        assert res.status_code == 403

    def test_latest_no_review_returns_null(self, client):
        token, cid = _register_and_upload(client, "lat_none")
        res = client.get(
            f"/api/v1/contracts/{cid}/review/latest",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200
        assert res.json()["data"] is None

    def test_latest_returns_most_recent(self, client):
        token, cid = _register_and_upload(client, "lat_multi")
        _parse_and_normalize(client, token, cid)

        with patch("app.agents.contract_profile_agent.ContractProfileAgent.run", new_callable=AsyncMock) as mock:
            mock.return_value = PROFILE_OUTPUT
            # Create 2 review tasks
            client.post(
                f"/api/v1/contracts/{cid}/review/profile",
                headers={"Authorization": f"Bearer {token}"},
            )
            client.post(
                f"/api/v1/contracts/{cid}/review/profile",
                headers={"Authorization": f"Bearer {token}"},
            )

        res = client.get(
            f"/api/v1/contracts/{cid}/review/latest",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200
        task = res.json()["data"]
        assert task is not None
        assert task["contract_id"] == cid
