"""Testes de integração — update e delete de roles (admin)."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_put_and_delete_role(client: TestClient, admin_headers: dict):
    created = client.post(
        "/v1/roles/",
        json={"description": "Role CRUD", "active": True},
        headers=admin_headers,
    )
    assert created.status_code == 201
    role_id = created.json()["id"]

    updated = client.put(
        f"/v1/roles/{role_id}",
        json={"description": "Role Atualizada", "active": True},
        headers=admin_headers,
    )
    assert updated.status_code == 200
    assert updated.json()["description"] == "Role Atualizada"

    deleted = client.delete(f"/v1/roles/{role_id}", headers=admin_headers)
    assert deleted.status_code == 204

    fetched = client.get(f"/v1/roles/{role_id}", headers=admin_headers)
    assert fetched.status_code == 404
