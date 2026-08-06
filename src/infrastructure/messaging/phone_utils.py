from __future__ import annotations

import re


def normalize_phone_digits(phone: str) -> str:
    """Normaliza para E.164 básico (apenas dígitos e + inicial)."""
    cleaned = phone.strip()
    if cleaned.startswith("whatsapp:"):
        cleaned = cleaned.split(":", 1)[1]
    digits = re.sub(r"[^\d+]", "", cleaned)
    if not digits.startswith("+"):
        if len(digits) == 11:
            digits = f"+55{digits}"
        else:
            digits = f"+{digits}"
    return digits


def to_whatsapp_address(phone: str) -> str:
    """Formato exigido pela Twilio: ``whatsapp:+<E.164>``."""
    e164 = normalize_phone_digits(phone)
    return f"whatsapp:{e164}"
