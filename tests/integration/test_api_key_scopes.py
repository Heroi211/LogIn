"""Testes — API key scopes (cap RBAC)."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_api_key_read_scope_blocks_post(client: TestClient, admin_headers: dict):
    created = client.post(
        "/v1/api-keys/",
        json={"name": "ReadOnly", "scopes": "read"},
        headers=admin_headers,
    )
    assert created.status_code == 201
    api_key = created.json()["key"]

    blocked = client.post(
        "/v1/messaging/whatsapp",
        json={"to": "11999990001", "body": "teste"},
        headers={"X-API-Key": api_key},
    )
    assert blocked.status_code == 403

    allowed = client.get("/v1/users/logged", headers={"X-API-Key": api_key})
    assert allowed.status_code == 200


@pytest.mark.integration
def test_signup_duplicate_returns_409(client: TestClient):
    payload = {
        "name": "Dup User",
        "email": "dup@example.com",
        "cpf": "66666666666",
        "phone": "11999990066",
        "password": "senha1234",
    }
    first = client.post("/v1/users/signup", json=payload)
    assert first.status_code == 201
    second = client.post("/v1/users/signup", json=payload)
    assert second.status_code == 409
