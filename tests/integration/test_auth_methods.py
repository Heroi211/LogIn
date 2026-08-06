"""Testes de integração — métodos de autenticação (cookie, API key, prioridade)."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_logged_with_session_cookie(client: TestClient):
    login = client.post(
        "/v1/users/login/json",
        json={"cpf": "11111111111", "password": "dev123"},
    )
    assert login.status_code == 200

    response = client.get("/v1/users/logged")
    assert response.status_code == 200
    assert response.json()["cpf"] == "11111111111"


@pytest.mark.integration
def test_logged_with_api_key(client: TestClient, admin_headers: dict):
    created = client.post(
        "/v1/api-keys/",
        json={"name": "AuthMethod", "scopes": "read"},
        headers=admin_headers,
    )
    assert created.status_code == 201
    api_key = created.json()["key"]

    response = client.get("/v1/users/logged", headers={"X-API-Key": api_key})
    assert response.status_code == 200
    assert response.json()["cpf"] == "22222222222"


@pytest.mark.integration
def test_api_key_priority_over_jwt(client: TestClient, admin_headers: dict):
    created = client.post(
        "/v1/api-keys/",
        json={"name": "ReadOnly", "scopes": "read"},
        headers=admin_headers,
    )
    assert created.status_code == 201
    api_key = created.json()["key"]

    operator_login = client.post(
        "/v1/users/login/json",
        json={"cpf": "11111111111", "password": "dev123"},
    )
    assert operator_login.status_code == 200
    operator_token = operator_login.json()["access_token"]

    response = client.get(
        "/v1/users/logged",
        headers={
            "Authorization": f"Bearer {operator_token}",
            "X-API-Key": api_key,
        },
    )
    assert response.status_code == 200
    assert response.json()["cpf"] == "22222222222"
