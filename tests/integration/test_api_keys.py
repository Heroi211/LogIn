"""Testes de integração — API keys."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_api_keys_lifecycle(client: TestClient, admin_headers: dict):
    created = client.post(
        "/v1/api-keys/",
        json={"name": "Integração", "scopes": "read"},
        headers=admin_headers,
    )
    assert created.status_code == 201
    body = created.json()
    assert body["key"].startswith("ltk_")
    key_id = body["id"]

    listed = client.get("/v1/api-keys/", headers=admin_headers)
    assert listed.status_code == 200
    assert any(item["id"] == key_id for item in listed.json())

    revoked = client.delete(f"/v1/api-keys/{key_id}", headers=admin_headers)
    assert revoked.status_code == 204


@pytest.mark.integration
def test_api_keys_requires_admin(client: TestClient, operator_headers: dict):
    response = client.get("/v1/api-keys/", headers=operator_headers)
    assert response.status_code == 403
