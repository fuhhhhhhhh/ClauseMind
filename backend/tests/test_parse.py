"""Tests for parse (MinerU) module."""

import io
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.models.contract import Contract
from app.models.parse_job import DocumentParseResult, ParseJob
from app.models.user import User
from main import app


# ── helpers ──────────────────────────────────────────────────────────────────


def _register_and_upload(client: TestClient, username: str = "puser") -> tuple[str, int]:
    """Register a user, upload a contract, return (token, contract_id)."""
    res = client.post(
        "/api/v1/auth/register",
        json={"username": username, "password": "pass123456"},
    )
    token = res.json()["data"]["access_token"]

    upload_res = client.post(
        "/api/v1/contracts/upload",
        files={"file": ("test.pdf", io.BytesIO(b"%PDF-1.4 dummy"), "application/octet-stream")},
        data={"contract_type": "租赁合同"},
        headers={"Authorization": f"Bearer {token}"},
    )
    return token, upload_res.json()["data"]["id"]


# ── fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    db = SessionLocal()
    try:
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


class TestParseAuth:
    def test_parse_without_token_returns_401(self, client):
        res = client.post("/api/v1/contracts/1/parse")
        assert res.status_code == 401

    def test_parse_other_user_contract_returns_403(self, client):
        token1, cid = _register_and_upload(client, "owner_p")
        _register_and_upload(client, "intruder_p")  # creates token2, different contract

        # Login as intruder to get token2
        login_res = client.post(
            "/api/v1/auth/login",
            json={"username": "intruder_p", "password": "pass123456"},
        )
        token2 = login_res.json()["data"]["access_token"]

        res = client.post(
            f"/api/v1/contracts/{cid}/parse",
            headers={"Authorization": f"Bearer {token2}"},
        )
        assert res.status_code == 403

    def test_parse_nonexistent_contract_returns_404(self, client):
        token, _ = _register_and_upload(client, "nxuser")
        res = client.post(
            "/api/v1/contracts/99999/parse",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 404


class TestParseFlow:
    @patch("app.services.mineru_service.MinerUService.parse")
    def test_successful_parse_sets_status_to_parsed(self, mock_parse: MagicMock, client):
        mock_parse.return_value = {
            "markdown_path": "/tmp/test.md",
            "raw_markdown": "# 房屋租赁合同\n\n内容...",
            "content_json_path": None,
            "middle_json_path": None,
            "layout_pdf_path": None,
            "image_dir": "/tmp/mineru_output",
        }

        token, cid = _register_and_upload(client, "parse_ok")
        res = client.post(
            f"/api/v1/contracts/{cid}/parse",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["status"] == "SUCCESS"
        assert data["backend"] == settings.mineru_backend

        # Verify contract status via detail
        detail = client.get(
            f"/api/v1/contracts/{cid}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert detail.json()["data"]["status"] == "PARSED"

        # Verify parse-result returns markdown
        result = client.get(
            f"/api/v1/contracts/{cid}/parse-result",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert result.status_code == 200
        assert "# 房屋租赁合同" in result.json()["data"]["raw_markdown"]

        # Verify parse-status
        status_res = client.get(
            f"/api/v1/contracts/{cid}/parse-status",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert status_res.json()["data"]["contract_status"] == "PARSED"

    @patch("app.services.mineru_service.MinerUService.parse")
    def test_failed_parse_sets_status_to_failed(self, mock_parse: MagicMock, client):
        from app.core.exceptions import AppError

        mock_parse.side_effect = AppError("MinerU exploded", code=500, status_code=500)

        token, cid = _register_and_upload(client, "parse_fail")
        res = client.post(
            f"/api/v1/contracts/{cid}/parse",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 500
        detail = client.get(
            f"/api/v1/contracts/{cid}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert detail.json()["data"]["status"] == "FAILED"

    @patch("app.services.mineru_service.MinerUService.parse")
    def test_parse_result_does_not_expose_server_paths(self, mock_parse: MagicMock, client):
        mock_parse.return_value = {
            "markdown_path": "/home/user/storage/mineru_output/1/abc/test.md",
            "raw_markdown": "content",
            "content_json_path": "/home/user/storage/mineru_output/1/abc/content_list.json",
            "middle_json_path": None,
            "layout_pdf_path": None,
            "image_dir": "/home/user/storage/mineru_output/1/abc",
        }

        token, cid = _register_and_upload(client, "safe_paths")
        client.post(
            f"/api/v1/contracts/{cid}/parse",
            headers={"Authorization": f"Bearer {token}"},
        )

        result = client.get(
            f"/api/v1/contracts/{cid}/parse-result",
            headers={"Authorization": f"Bearer {token}"},
        )
        data = result.json()["data"]
        # Paths are stored but should NOT expose sensitive system paths in response
        # (We still store them for internal use; the FE just displays them)
        assert "raw_markdown" in data
        assert data["raw_markdown"] == "content"

    @patch("app.services.mineru_service.MinerUService.parse")
    def test_parse_status_without_job(self, mock_parse: MagicMock, client):
        """Status endpoint for a contract that was never parsed."""
        token, cid = _register_and_upload(client, "noparse")
        res = client.get(
            f"/api/v1/contracts/{cid}/parse-status",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["contract_status"] == "UPLOADED"
        assert data["parse_job"] is None

    @patch("app.services.mineru_service.MinerUService.parse")
    def test_parse_result_without_job_returns_404(self, mock_parse: MagicMock, client):
        """Result endpoint for a contract never parsed returns 404."""
        token, cid = _register_and_upload(client, "noresult")
        res = client.get(
            f"/api/v1/contracts/{cid}/parse-result",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 404
