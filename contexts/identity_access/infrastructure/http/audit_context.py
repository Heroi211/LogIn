from __future__ import annotations

from typing import Any

from starlette.requests import Request

from contexts.identity_access.application.dto.audit import AuditContext


def audit_context_from_request(
    request: Request | None,
    *,
    actor_user_id: int | None = None,
) -> AuditContext:
    if request is None:
        return AuditContext(actor_user_id=actor_user_id)

    request_id = getattr(request.state, "request_id", None) or request.headers.get("X-Request-ID")
    client = request.client.host if request.client else None
    return AuditContext(
        request_id=request_id,
        ip_address=client,
        actor_user_id=actor_user_id,
    )
