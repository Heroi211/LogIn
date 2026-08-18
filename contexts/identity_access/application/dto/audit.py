from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class AuditContext:
    request_id: str | None = None
    ip_address: str | None = None
    actor_user_id: int | None = None


@dataclass(frozen=True, slots=True)
class AuditRecord:
    action: str
    outcome: str
    resource_type: str | None = None
    resource_id: str | None = None
    actor_user_id: int | None = None
    request_id: str | None = None
    ip_address: str | None = None
    metadata: dict[str, Any] | None = None
