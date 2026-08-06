"""Testes de integração — health."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_health_live(client: TestClient):
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.integration
def test_health_ready_mocked_db(client: TestClient):
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json()["database"] == "mocked"


@pytest.mark.integration
def test_meta_bootstrap(client: TestClient):
    response = client.get("/v1/meta")
    assert response.status_code == 200
    body = response.json()
    assert body["environment"] == "development"
    assert "login_json" in body["auth"]
