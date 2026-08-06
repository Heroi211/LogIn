"""Testes de integração — logout e fluxos adicionais de users."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_logout_revokes_session(client: TestClient):
    login = client.post(
        "/v1/users/login/json",
        json={"cpf": "11111111111", "password": "dev123"},
    )
    tokens = login.json()

    logout = client.post(
        "/v1/users/logout",
        json={
            "refresh_token": tokens["refresh_token"],
            "access_token": tokens["access_token"],
        },
    )
    assert logout.status_code == 200

    refresh = client.post(
        "/v1/users/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refresh.status_code == 401


@pytest.mark.integration
def test_get_user_by_id(client: TestClient, operator_headers: dict):
    response = client.get("/v1/users/1", headers=operator_headers)
    assert response.status_code == 200
    assert response.json()["cpf"] == "11111111111"


@pytest.mark.integration
def test_forgot_password_returns_200(client: TestClient):
    response = client.post("/v1/users/forgot-password/admin@example.com")
    assert response.status_code == 200
    assert "e-mail" in response.json()["message"].lower()
