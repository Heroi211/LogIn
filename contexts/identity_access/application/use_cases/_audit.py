from __future__ import annotations

from typing import Any

from contexts.identity_access.application.dto.audit import AuditContext, AuditRecord
from contexts.identity_access.application.ports.audit_logger import AuditLogger


async def record_audit(
    audit: AuditLogger | None,
    ctx: AuditContext | None,
    *,
    action: str,
    outcome: str,
    resource_type: str | None = None,
    resource_id: str | int | None = None,
    metadata: dict[str, Any] | None = None,
    actor_user_id: int | None = None,
) -> None:
    if audit is None:
        return

    actor = actor_user_id
    if actor is None and ctx is not None:
        actor = ctx.actor_user_id

    await audit.record(
        AuditRecord(
            action=action,
            outcome=outcome,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id is not None else None,
            actor_user_id=actor,
            request_id=ctx.request_id if ctx else None,
            ip_address=ctx.ip_address if ctx else None,
            metadata=metadata,
        )
    )
