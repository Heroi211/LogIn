"""Testes unitários — normalização de telefone WhatsApp."""

import pytest

from infrastructure.messaging.phone_utils import normalize_phone_digits, to_whatsapp_address


@pytest.mark.unit
def test_normalize_brazil_mobile():
    assert normalize_phone_digits("11999990001") == "+5511999990001"


@pytest.mark.unit
def test_to_whatsapp_address():
    assert to_whatsapp_address("11999990001") == "whatsapp:+5511999990001"
    assert to_whatsapp_address("whatsapp:+5511999990001") == "whatsapp:+5511999990001"
