"""Pytest configuration for isolating the test database from the dev database."""

import os
from pathlib import Path


TEST_DB_PATH = Path(__file__).resolve().parent.parent / "test_contract_review.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"


def pytest_sessionfinish(session, exitstatus):
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
