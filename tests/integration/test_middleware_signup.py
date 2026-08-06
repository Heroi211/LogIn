"""Testes de integração — middleware de signup."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_signup_rejects_empty_body(client: TestClient):
    response = client.post("/v1/users/signup", content=b"")
    assert response.status_code == 400
    assert "cadastro" in response.json().get("detail", "").lower()


@pytest.mark.integration
def test_signup_rejects_invalid_json_body(client: TestClient):
    response = client.post(
        "/v1/users/signup",
        content=b"{invalid-json",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 400
    assert "cadastro" in response.json().get("detail", "").lower()
