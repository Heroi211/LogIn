"""Testes unitários — lockout revoga sessões e invalida refresh."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
def test_lockout_refresh_with_old_token_fails_401(client: TestClient):
    cpf = "77777777777"
    client.post(
        "/v1/users/signup",
        json={
            "name": "Lockout Refresh",
            "email": "lockout.refresh@example.com",
            "cpf": cpf,
            "phone": "11999990077",
            "password": "correct-pass1",
        },
    )

    login = client.post(
        "/v1/users/login/json",
        json={"cpf": cpf, "password": "correct-pass1"},
    )
    assert login.status_code == 200
    refresh_token = login.json()["refresh_token"]

    for attempt in range(3):
        response = client.post(
            "/v1/users/login/json",
            json={"cpf": cpf, "password": "wrong-password"},
        )
        if attempt < 2:
            assert response.status_code == 401
        else:
            assert response.status_code == 403

    refresh = client.post(
        "/v1/users/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh.status_code == 401
