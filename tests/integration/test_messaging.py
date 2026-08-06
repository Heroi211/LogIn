"""Testes de integração — messaging (mock)."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_messaging_whatsapp_admin(client: TestClient, admin_headers: dict):
    sent = client.post(
        "/v1/messaging/whatsapp",
        json={"to": "11999990001", "body": "Teste integração"},
        headers=admin_headers,
    )
    assert sent.status_code == 200
    sid = sent.json()["sid"]

    status_resp = client.get(f"/v1/messaging/whatsapp/{sid}", headers=admin_headers)
    assert status_resp.status_code == 200

    lookup = client.get("/v1/messaging/phone/11999990001/lookup", headers=admin_headers)
    assert lookup.status_code == 200
    assert lookup.json()["valid"] is True


@pytest.mark.integration
def test_messaging_notify_admin(client: TestClient, admin_headers: dict):
    response = client.post(
        "/v1/messaging/whatsapp/notify-admin",
        json={"body": "Alerta de teste"},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["body"] == "Alerta de teste"
