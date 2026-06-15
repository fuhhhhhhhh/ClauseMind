"""Tests for document normalization module."""

import io
import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.core.database import Base, SessionLocal, engine
from app.models.contract import Contract
from app.models.parse_job import DocumentParseResult, ParseJob
from app.models.user import User
from app.services.document_normalizer import DocumentNormalizer
from main import app


# ── helpers ──────────────────────────────────────────────────────────────────


def _register_and_upload(client: TestClient, username: str = "normuser") -> tuple[str, int]:
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


def _patch_parse_and_upload(client: TestClient, token: str, cid: int, raw_md: str):
    """Mock MinerU.parse to return given markdown, then POST /parse."""
    with patch("app.services.mineru_service.MinerUService.parse") as mock:
        mock.return_value = {
            "markdown_path": "/tmp/test.md",
            "raw_markdown": raw_md,
            "content_json_path": None,
            "middle_json_path": None,
            "layout_pdf_path": None,
            "image_dir": "/tmp",
        }
        client.post(
            f"/api/v1/contracts/{cid}/parse",
            headers={"Authorization": f"Bearer {token}"},
        )


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


# ── Normalizer unit tests ────────────────────────────────────────────────────


SAMPLE_MARKDOWN = """\
# 房屋租赁合同

甲方：张三
乙方：李四

第一条 租赁房屋
甲方将位于北京市朝阳区某房屋出租给乙方使用。

第二条 租赁期限
租赁期限自2026年1月1日至2027年1月1日。

第三条 租金及支付方式
月租金为3000元，每月5日前支付。
"""


class TestDocumentNormalizer:
    def test_extract_title(self):
        norm = DocumentNormalizer()
        result = norm.normalize(SAMPLE_MARKDOWN)
        assert result["title"] == "房屋租赁合同"

    def test_extract_parties(self):
        norm = DocumentNormalizer()
        result = norm.normalize(SAMPLE_MARKDOWN)
        parties = result["parties"]
        roles = {p["role"] for p in parties}
        assert "甲方" in roles
        assert "乙方" in roles

    def test_extract_sections(self):
        norm = DocumentNormalizer()
        result = norm.normalize(SAMPLE_MARKDOWN)
        assert len(result["sections"]) >= 3
        titles = [s["title"] for s in result["sections"]]
        assert any("租赁房屋" in t for t in titles)

    def test_extract_clauses(self):
        norm = DocumentNormalizer()
        result = norm.normalize(SAMPLE_MARKDOWN)
        assert len(result["clauses"]) >= 3

    def test_fallback_for_plain_text(self):
        norm = DocumentNormalizer()
        result = norm.normalize("这是一份简单的合同文本，没有明确的章节结构。")
        assert len(result["sections"]) == 1
        assert result["sections"][0]["title"] == "全文"


# ── Normalize API tests ──────────────────────────────────────────────────────


class TestNormalizeAPI:
    def test_normalize_without_token_returns_401(self, client):
        res = client.post("/api/v1/contracts/1/normalize")
        assert res.status_code == 401

    def test_normalize_other_user_contract_returns_403(self, client):
        token1, cid = _register_and_upload(client, "owner_n")
        _register_and_upload(client, "intruder_n")
        login_res = client.post(
            "/api/v1/auth/login",
            json={"username": "intruder_n", "password": "pass123456"},
        )
        token2 = login_res.json()["data"]["access_token"]
        res = client.post(
            f"/api/v1/contracts/{cid}/normalize",
            headers={"Authorization": f"Bearer {token2}"},
        )
        assert res.status_code == 403

    def test_normalize_without_parse_result_returns_400(self, client):
        token, cid = _register_and_upload(client, "noparse2")
        res = client.post(
            f"/api/v1/contracts/{cid}/normalize",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 400

    def test_normalize_success(self, client):
        token, cid = _register_and_upload(client, "norm_ok")
        _patch_parse_and_upload(client, token, cid, SAMPLE_MARKDOWN)

        res = client.post(
            f"/api/v1/contracts/{cid}/normalize",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["title"] == "房屋租赁合同"
        assert len(data["parties"]) >= 2
        assert len(data["sections"]) >= 3

    def test_normalize_saves_to_db(self, client):
        token, cid = _register_and_upload(client, "norm_db")
        _patch_parse_and_upload(client, token, cid, SAMPLE_MARKDOWN)

        client.post(
            f"/api/v1/contracts/{cid}/normalize",
            headers={"Authorization": f"Bearer {token}"},
        )

        # Verify via parse-result
        result = client.get(
            f"/api/v1/contracts/{cid}/parse-result",
            headers={"Authorization": f"Bearer {token}"},
        )
        data = result.json()["data"]
        assert data["normalized_json"] is not None
        parsed = json.loads(data["normalized_json"])
        assert parsed["title"] == "房屋租赁合同"

    def test_idempotent_normalize(self, client):
        """Re-normalizing should overwrite (idempotent)."""
        token, cid = _register_and_upload(client, "norm_idem")
        _patch_parse_and_upload(client, token, cid, SAMPLE_MARKDOWN)

        res1 = client.post(
            f"/api/v1/contracts/{cid}/normalize",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res1.status_code == 200

        res2 = client.post(
            f"/api/v1/contracts/{cid}/normalize",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res2.status_code == 200
        assert res2.json()["data"]["title"] == "房屋租赁合同"

    def test_parse_result_no_internal_paths(self, client):
        """After normalize, parse-result still must not expose paths."""
        token, cid = _register_and_upload(client, "norm_safe")
        _patch_parse_and_upload(client, token, cid, SAMPLE_MARKDOWN)
        client.post(
            f"/api/v1/contracts/{cid}/normalize",
            headers={"Authorization": f"Bearer {token}"},
        )

        result = client.get(
            f"/api/v1/contracts/{cid}/parse-result",
            headers={"Authorization": f"Bearer {token}"},
        )
        data = result.json()["data"]
        assert "markdown_path" not in data
        assert "content_json_path" not in data
