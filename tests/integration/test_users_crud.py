"""Testes de integração — CRUD de usuários (admin)."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_put_user_admin_updates_name(client: TestClient, admin_headers: dict):
    response = client.put(
        "/v1/users/1",
        json={"name": "Operador Atualizado"},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Operador Atualizado"

    fetched = client.get("/v1/users/1", headers=admin_headers)
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "Operador Atualizado"
