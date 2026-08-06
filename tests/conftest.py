"""Fixtures globais — ENVIRONMENT=development + mocks (sem PostgreSQL)."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

# Variáveis antes de importar a app
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("SECRET", "test-secret-key-pytest-only-32chars-min!!")
os.environ.setdefault("LOG_HTTP_REQUESTS", "false")
os.environ.setdefault("LOG_HTTP_REQUESTS_FILE", "false")

from main import app  # noqa: E402


@pytest.fixture(autouse=True)
def reset_mock_store():
    """Isola testes — store in-memory é compartilhado entre repositórios mock."""
    import repositories.mocks.data as mock_data

    mock_data._store = None
    yield
    mock_data._store = None


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def admin_token(client: TestClient) -> str:
    response = client.post(
        "/v1/users/login/json",
        json={"cpf": "22222222222", "password": "admin123"},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


@pytest.fixture
def admin_headers(admin_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def operator_token(client: TestClient) -> str:
    response = client.post(
        "/v1/users/login/json",
        json={"cpf": "11111111111", "password": "dev123"},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


@pytest.fixture
def operator_headers(operator_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {operator_token}"}
