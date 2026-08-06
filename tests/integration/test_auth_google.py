"""Testes de integração — OAuth Google (mock dev)."""

import pytest
from fastapi.testclient import TestClient

from infrastructure.auth.google_oauth import DEV_MOCK_ID_TOKEN


def _oauth_state(client: TestClient) -> str:
    response = client.get("/v1/auth/google/url")
    assert response.status_code == 200
    return response.json()["state"]


@pytest.mark.integration
def test_google_auth_url_dev(client: TestClient):
    response = client.get("/v1/auth/google/url")
    assert response.status_code == 200
    body = response.json()
    assert "url" in body
    assert body["state"]
    assert body["mock_id_token"] == DEV_MOCK_ID_TOKEN


@pytest.mark.integration
def test_google_callback_mock_token(client: TestClient):
    state = _oauth_state(client)
    response = client.post(
        "/v1/auth/google/callback",
        json={"id_token": DEV_MOCK_ID_TOKEN, "state": state},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["user"]["auth_provider"] == "google"


@pytest.mark.integration
def test_google_callback_requires_state(client: TestClient):
    response = client.post(
        "/v1/auth/google/callback",
        json={"id_token": DEV_MOCK_ID_TOKEN, "state": "invalid-state"},
    )
    assert response.status_code == 503


@pytest.mark.integration
def test_google_link_local_account(client: TestClient):
    state = _oauth_state(client)
    linked = client.post(
        "/v1/auth/google/link",
        json={
            "cpf": "11111111111",
            "password": "dev123",
            "id_token": DEV_MOCK_ID_TOKEN,
            "state": state,
        },
    )
    assert linked.status_code == 200
    assert linked.json()["auth_provider"] == "google"
