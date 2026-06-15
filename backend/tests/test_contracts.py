"""Tests for contract module: upload, list, detail, delete with auth."""

import io

import pytest
from fastapi.testclient import TestClient

from app.core.database import Base, SessionLocal, engine
from app.models.contract import Contract
from app.models.user import User
from main import app

# ── helpers ──────────────────────────────────────────────────────────────────


def _register_and_login(client: TestClient, username: str = "ctuser") -> tuple[str, int]:
    """Register a user, return (token, user_id)."""
    res = client.post(
        "/api/v1/auth/register",
        json={"username": username, "password": "pass123456"},
    )
    assert res.status_code == 200
    data = res.json()["data"]
    return data["access_token"], data["user"]["id"]


def _upload(client: TestClient, token: str, filename: str = "test.pdf", **kwargs):
    """Helper: upload a dummy PDF."""
    content = kwargs.pop("content", b"%PDF-1.4 dummy")
    ct = kwargs.pop("contract_type", None)
    form = {"file": (filename, io.BytesIO(content), "application/octet-stream")}
    if ct:
        form["contract_type"] = (None, ct)
    return client.post(
        "/api/v1/contracts/upload",
        files=form,
        headers={"Authorization": f"Bearer {token}"},
    )


# ── fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def setup_db():
    """Create tables + clean up after each test."""
    Base.metadata.create_all(bind=engine)
    yield
    db = SessionLocal()
    try:
        db.query(Contract).delete()
        db.query(User).delete()
        db.commit()
    finally:
        db.close()


@pytest.fixture
def client():
    return TestClient(app)


# ── tests ────────────────────────────────────────────────────────────────────


class TestContractUpload:
    def test_upload_without_token_returns_401(self, client):
        res = client.post("/api/v1/contracts/upload")
        assert res.status_code == 401

    def test_upload_success(self, client):
        token, uid = _register_and_login(client)
        res = _upload(client, token, "合同.pdf", contract_type="房屋租赁")
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["file_name"] == "合同.pdf"
        assert data["file_type"] == "pdf"
        assert data["contract_type"] == "房屋租赁"
        assert data["status"] == "UPLOADED"
        assert data["user_id"] == uid

    def test_upload_unsupported_extension(self, client):
        token, _ = _register_and_login(client)
        res = _upload(client, token, "virus.exe", content=b"bad")
        assert res.status_code == 400
        assert "不支持" in res.json()["message"]

    def test_upload_png_allowed(self, client):
        token, _ = _register_and_login(client)
        res = _upload(client, token, "scan.png", content=b"\x89PNG\r\n\x1a\n")
        assert res.status_code == 200
        assert res.json()["data"]["file_type"] == "png"


class TestContractList:
    def test_list_returns_user_contracts_only(self, client):
        tok1, _ = _register_and_login(client, "user_a")
        tok2, _ = _register_and_login(client, "user_b")

        _upload(client, tok1, "a1.pdf")
        _upload(client, tok1, "a2.docx", content=b"docx")
        _upload(client, tok2, "b1.pdf")

        # user_a sees only 2
        res = client.get("/api/v1/contracts", headers={"Authorization": f"Bearer {tok1}"})
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["total"] == 2
        names = {item["file_name"] for item in data["items"]}
        assert names == {"a1.pdf", "a2.docx"}

    def test_list_without_token(self, client):
        res = client.get("/api/v1/contracts")
        assert res.status_code == 401


class TestContractDetail:
    def test_detail_own_contract(self, client):
        token, _ = _register_and_login(client)
        upload_res = _upload(client, token, "detail.pdf")
        cid = upload_res.json()["data"]["id"]

        res = client.get(f"/api/v1/contracts/{cid}", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        assert res.json()["data"]["file_name"] == "detail.pdf"

    def test_detail_other_user_contract_forbidden(self, client):
        tok1, _ = _register_and_login(client, "owner")
        tok2, _ = _register_and_login(client, "intruder")

        upload_res = _upload(client, tok1, "secret.pdf")
        cid = upload_res.json()["data"]["id"]

        res = client.get(f"/api/v1/contracts/{cid}", headers={"Authorization": f"Bearer {tok2}"})
        assert res.status_code == 403

    def test_detail_not_found(self, client):
        token, _ = _register_and_login(client)
        res = client.get("/api/v1/contracts/99999", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 404


class TestContractDelete:
    def test_delete_own_contract(self, client):
        token, _ = _register_and_login(client)
        upload_res = _upload(client, token, "del.pdf")
        cid = upload_res.json()["data"]["id"]

        res = client.delete(f"/api/v1/contracts/{cid}", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200

        # verify gone
        get_res = client.get(f"/api/v1/contracts/{cid}", headers={"Authorization": f"Bearer {token}"})
        assert get_res.status_code == 404

    def test_delete_other_user_forbidden(self, client):
        tok1, _ = _register_and_login(client, "owner2")
        tok2, _ = _register_and_login(client, "intruder2")

        upload_res = _upload(client, tok1, "keep.pdf")
        cid = upload_res.json()["data"]["id"]

        res = client.delete(f"/api/v1/contracts/{cid}", headers={"Authorization": f"Bearer {tok2}"})
        assert res.status_code == 403

    def test_delete_without_token(self, client):
        res = client.delete("/api/v1/contracts/1")
        assert res.status_code == 401
