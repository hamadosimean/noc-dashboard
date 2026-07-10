import os

# Must be set before any app module is imported (constants are read at import time).
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("NOC_API_KEY", "test-api-key")
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")
os.environ.setdefault("SYNC_MV_REFRESH", "false")
os.environ.setdefault("NOTIFICATIONS_ENABLED", "false")
os.environ.setdefault("REDIS_HOST", "127.0.0.1")

import pytest
from fastapi.testclient import TestClient

from app.db.session import get_db
from app.main import app
from app.models.user import User
from app.services.auth_service import create_access_token

API_KEY_HEADERS = {"Authorization": "Bearer test-api-key"}


def make_user(user_id: int, role: str) -> User:
    return User(
        id=user_id,
        username=role,
        full_name=f"Test {role}",
        role=role,
        password_hash="x",
        is_active=True,
    )


USERS = {
    1: make_user(1, "admin"),
    2: make_user(2, "analyst"),
    3: make_user(3, "noc_agent"),
}


class FakeSession:
    """Just enough of a SQLAlchemy session for get_current_user (db.get)."""

    def get(self, model, pk):
        return USERS.get(pk)


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = FakeSession
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def auth_headers(user_id: int) -> dict:
    token = create_access_token(USERS[user_id])
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers():
    return auth_headers(1)


@pytest.fixture
def analyst_headers():
    return auth_headers(2)


@pytest.fixture
def noc_agent_headers():
    return auth_headers(3)
