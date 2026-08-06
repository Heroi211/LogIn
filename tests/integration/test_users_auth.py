"""Testes de integração — users e auth."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_login_json_returns_tokens_and_user(client: TestClient):
    response = client.post(
        "/v1/users/login/json",
        json={"cpf": "22222222222", "password": "admin123"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["user"]["role"] == "Administrador"


@pytest.mark.integration
def test_logged_requires_auth(client: TestClient):
    unauthorized = client.get("/v1/users/logged")
    assert unauthorized.status_code == 401

    login = client.post(
        "/v1/users/login/json",
        json={"cpf": "11111111111", "password": "dev123"},
    )
    token = login.json()["access_token"]
    response = client.get(
        "/v1/users/logged",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["cpf"] == "11111111111"


@pytest.mark.integration
def test_refresh_token_rotation(client: TestClient):
    login = client.post(
        "/v1/users/login/json",
        json={"cpf": "22222222222", "password": "admin123"},
    )
    refresh_token = login.json()["refresh_token"]

    refreshed = client.post(
        "/v1/users/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refreshed.status_code == 200
    assert refreshed.json()["access_token"]


@pytest.mark.integration
def test_signup_and_list_users(client: TestClient, admin_headers: dict):
    signup = client.post(
        "/v1/users/signup",
        json={
            "name": "Novo Usuario",
            "email": "novo.user@example.com",
            "cpf": "55555555555",
            "phone": "11999990055",
            "password": "senha1234",
        },
    )
    assert signup.status_code == 201

    listed = client.get("/v1/users/", headers=admin_headers)
    assert listed.status_code == 200
    cpfs = [user["cpf"] for user in listed.json()]
    assert "55555555555" in cpfs
