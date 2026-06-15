"""Tests for auth module."""

import pytest
from fastapi.testclient import TestClient

from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password, verify_password
from app.models.user import User
from main import app


@pytest.fixture(autouse=True)
def setup_db():
    """Create tables before each test and clean up after."""
    Base.metadata.create_all(bind=engine)
    yield
    # Clean up
    db = SessionLocal()
    try:
        db.query(User).delete()
        db.commit()
    finally:
        db.close()


@pytest.fixture
def client():
    return TestClient(app)


class TestPasswordHashing:
    def test_hash_and_verify(self):
        password = "my-secret-password"
        hashed = hash_password(password)
        assert hashed != password
        assert verify_password(password, hashed)

    def test_wrong_password(self):
        hashed = hash_password("correct")
        assert not verify_password("wrong", hashed)


class TestAuthAPIs:
    def test_register_success(self, client):
        res = client.post(
            "/api/v1/auth/register",
            json={"username": "newuser", "password": "pass123456"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["code"] == 200
        assert data["data"]["access_token"]
        assert data["data"]["user"]["username"] == "newuser"

    def test_register_duplicate(self, client):
        client.post(
            "/api/v1/auth/register",
            json={"username": "dup", "password": "pass123456"},
        )
        res = client.post(
            "/api/v1/auth/register",
            json={"username": "dup", "password": "pass123456"},
        )
        assert res.status_code == 409

    def test_login_success(self, client):
        client.post(
            "/api/v1/auth/register",
            json={"username": "loginuser", "password": "pass123456"},
        )
        res = client.post(
            "/api/v1/auth/login",
            json={"username": "loginuser", "password": "pass123456"},
        )
        assert res.status_code == 200
        assert res.json()["data"]["access_token"]

    def test_login_wrong_password(self, client):
        client.post(
            "/api/v1/auth/register",
            json={"username": "lpuser", "password": "correct"},
        )
        res = client.post(
            "/api/v1/auth/login",
            json={"username": "lpuser", "password": "wrong"},
        )
        assert res.status_code == 401

    def test_login_nonexistent_user(self, client):
        res = client.post(
            "/api/v1/auth/login",
            json={"username": "nobody", "password": "pass123456"},
        )
        assert res.status_code == 401

    def test_me_with_token(self, client):
        register_res = client.post(
            "/api/v1/auth/register",
            json={"username": "meuser", "password": "pass123456"},
        )
        token = register_res.json()["data"]["access_token"]

        res = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200
        assert res.json()["data"]["username"] == "meuser"

    def test_me_without_token(self, client):
        res = client.get("/api/v1/auth/me")
        assert res.status_code == 401

    def test_me_with_invalid_token(self, client):
        res = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid-token"},
        )
        assert res.status_code == 401
