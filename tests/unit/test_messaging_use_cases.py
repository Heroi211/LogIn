"""Testes unitários — use cases de messaging (mock)."""

import pytest

from application.container import get_container


@pytest.mark.unit
@pytest.mark.asyncio
async def test_send_whatsapp_mock():
    container = get_container(None)
    result = await container.send_whatsapp.execute(
        to="11999990001",
        body="Mensagem de teste",
    )
    assert result.sid.startswith("SM")
    assert result.status == "queued"
    assert "whatsapp:" in result.to


@pytest.mark.unit
@pytest.mark.asyncio
async def test_notify_admin_mock():
    container = get_container(None)
    result = await container.notify_admin_whatsapp.execute("Alerta admin teste")
    assert result is not None
    assert result.body == "Alerta admin teste"
