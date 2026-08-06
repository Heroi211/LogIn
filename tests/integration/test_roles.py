"""Testes de integração — roles (admin)."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_list_roles_requires_admin(client: TestClient, operator_headers: dict):
    response = client.get("/v1/roles/", headers=operator_headers)
    assert response.status_code == 403


@pytest.mark.integration
def test_roles_crud_admin(client: TestClient, admin_headers: dict):
    created = client.post(
        "/v1/roles/",
        json={"description": "Role Teste", "active": True},
        headers=admin_headers,
    )
    assert created.status_code == 201
    role_id = created.json()["id"]

    fetched = client.get(f"/v1/roles/{role_id}", headers=admin_headers)
    assert fetched.status_code == 200
    assert fetched.json()["description"] == "Role Teste"
