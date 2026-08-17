"""
Registro global de eventos de auditoria no banco de dados.

Uso nos endpoints (quando necessário):

    from core.audit import record_audit_event, audit_context_from_request

    await record_audit_event(
        db,
        action="auth.login.failed",
        outcome="failure",
        **audit_context_from_request(request),
        metadata={"cpf": form_data.username},
    )
"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from models.audit_events import AuditEvent

logger = logging.getLogger("audit")

VALID_OUTCOMES = frozenset({"success", "failure", "denied"})


class AuditAction:
    """Convenção de nomes para eventos de auditoria (namespace por domínio)."""

    AUTH_LOGIN_SUCCESS = "auth.login.success"
    AUTH_LOGIN_FAILED = "auth.login.failed"
    AUTH_PASSWORD_RESET_REQUESTED = "auth.password.reset.requested"
    AUTH_PASSWORD_RESET_COMPLETED = "auth.password.reset.completed"

    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DEACTIVATED = "user.deactivated"

    ROLE_CREATED = "role.created"
    ROLE_UPDATED = "role.updated"
    ROLE_DEACTIVATED = "role.deactivated"

    AUTHZ_DENIED = "authz.denied"


def audit_context_from_request(request: Request | None) -> dict[str, Any]:
    """Extrai metadados HTTP úteis para auditoria a partir da requisição."""
    if request is None:
        return {}

    request_id = getattr(request.state, "request_id", None)
    if not request_id:
        request_id = request.headers.get("X-Request-ID")

    client = request.client.host if request.client else None
    return {
        "request_id": request_id,
        "ip_address": client,
    }


async def record_audit_event(
    db: AsyncSession,
    *,
    action: str,
    outcome: str,
    resource_type: str | None = None,
    resource_id: str | None = None,
    actor_user_id: int | None = None,
    request_id: str | None = None,
    ip_address: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> AuditEvent | None:
    """
    Persiste um evento de auditoria (append-only).

    Falhas na gravação são logadas no console e não interrompem o fluxo principal.
    """
    action = (action or "").strip()
    outcome = (outcome or "").strip().lower()

    if not action:
        logger.warning("Auditoria ignorada: action vazio")
        return None
    if outcome not in VALID_OUTCOMES:
        logger.warning("Auditoria ignorada: outcome inválido=%s action=%s", outcome, action)
        return None

    event = AuditEvent(
        action=action,
        outcome=outcome,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id is not None else None,
        actor_user_id=actor_user_id,
        request_id=request_id,
        ip_address=ip_address,
        event_metadata=metadata or None,
    )

    try:
        db.add(event)
        await db.commit()
        await db.refresh(event)
        logger.info(
            "audit | action=%s outcome=%s actor=%s resource=%s:%s request_id=%s",
            action,
            outcome,
            actor_user_id,
            resource_type,
            resource_id,
            request_id,
        )
        return event
    except Exception:
        await db.rollback()
        logger.exception("Falha ao persistir evento de auditoria action=%s", action)
        return None
