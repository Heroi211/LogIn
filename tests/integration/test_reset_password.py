"""Testes de integração — fluxo forgot/reset password."""

import pytest
from fastapi.testclient import TestClient

from repositories.mocks.data import get_mock_store


def _reset_token_for_email(email: str) -> str | None:
    store = get_mock_store()
    for user in store.users.values():
        if user.email == email:
            return user.reset_password_token
    return None


@pytest.mark.integration
def test_forgot_and_reset_password_e2e(client: TestClient):
    forgot = client.post("/v1/users/forgot-password/admin@example.com")
    assert forgot.status_code == 200

    token = _reset_token_for_email("admin@example.com")
    assert token

    reset = client.post(
        "/v1/users/reset-password",
        json={"token": token, "password": "novaSenha123"},
    )
    assert reset.status_code == 200
    assert "sucesso" in reset.json()["message"].lower()

    login = client.post(
        "/v1/users/login/json",
        json={"cpf": "22222222222", "password": "novaSenha123"},
    )
    assert login.status_code == 200


@pytest.mark.integration
def test_reset_password_invalid_token_returns_404(client: TestClient):
    response = client.post(
        "/v1/users/reset-password",
        json={"token": "token-invalido", "password": "novaSenha123"},
    )
    assert response.status_code == 404
