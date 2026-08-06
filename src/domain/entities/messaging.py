from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class WhatsAppMessage:
    to: str
    body: str
    from_number: str | None = None
    content_sid: str | None = None
    content_variables: dict[str, str] = field(default_factory=dict)


@dataclass
class WhatsAppMessageResult:
    sid: str
    status: str
    to: str
    from_number: str
    body: str | None = None
    error_code: int | None = None
    error_message: str | None = None
    created_at: datetime | None = None


@dataclass
class PhoneLookupResult:
    phone_number: str
    country_code: str | None = None
    carrier_name: str | None = None
    carrier_type: str | None = None
    valid: bool = True
    raw: dict[str, Any] = field(default_factory=dict)
