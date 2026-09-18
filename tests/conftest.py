"""Shared Pytest fixtures.

Tests run against an isolated, in-memory SQLite database instead of the
real PostgreSQL database, so the test suite is fast, deterministic, and
never touches development or production data. The application code itself
is untouched: we only override the `get_db` dependency for the duration
of the test run.
"""

import os

os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest-only")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from main import app

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def _fresh_database():
    """Create all tables before each test and drop them afterward."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


def signup_and_login(client, username="testuser", password="testpassword123"):
    """Helper: register a user and return their JWT access token."""
    client.post("/signup", json={"username": username, "password": password})
    response = client.post(
        "/login",
        data={"username": username, "password": password},
    )
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(client):
    token = signup_and_login(client)
    return {"Authorization": f"Bearer {token}"}
