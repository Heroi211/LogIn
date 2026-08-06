"""Testes unitários — bloqueio por tentativas de login."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
def test_login_lockout_after_three_failures(client: TestClient):
    cpf = "44444444444"
    client.post(
        "/v1/users/signup",
        json={
            "name": "Lock Test",
            "email": "lock@example.com",
            "cpf": cpf,
            "phone": "11999990044",
            "password": "correct-pass1",
        },
    )

    for attempt in range(3):
        response = client.post(
            "/v1/users/login/json",
            json={"cpf": cpf, "password": "wrong-password"},
        )
        if attempt < 2:
            assert response.status_code == 401
        else:
            assert response.status_code == 403
            assert "bloqueada" in response.json()["detail"].lower()

    blocked = client.post(
        "/v1/users/login/json",
        json={"cpf": cpf, "password": "correct-pass1"},
    )
    assert blocked.status_code == 403
    assert "bloqueada" in blocked.json()["detail"].lower()
