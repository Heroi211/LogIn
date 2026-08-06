"""Testes de integração — WhatsApp template messaging."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_send_whatsapp_template(client: TestClient, admin_headers: dict):
    response = client.post(
        "/v1/messaging/whatsapp/template",
        json={
            "to": "11999990001",
            "content_sid": "HX1234567890abcdef",
            "content_variables": {"1": "João"},
        },
        headers=admin_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["sid"]
    assert "template" in body["body"].lower() or "HX1234567890abcdef" in body["body"]
