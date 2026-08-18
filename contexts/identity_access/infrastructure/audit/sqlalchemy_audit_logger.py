from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from contexts.identity_access.application.dto.audit import AuditRecord
from contexts.identity_access.application.ports.audit_logger import AuditLogger
from contexts.identity_access.infrastructure.persistence.models.audit_events import AuditEvent

logger = logging.getLogger("audit")

VALID_OUTCOMES = frozenset({"success", "failure", "denied"})


class SqlAlchemyAuditLogger:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def record(self, event: AuditRecord) -> None:
        outcome = event.outcome.strip().lower()
        if outcome not in VALID_OUTCOMES:
            logger.warning("Auditoria ignorada: outcome inválido=%s action=%s", outcome, event.action)
            return

        row = AuditEvent(
            action=event.action.strip(),
            outcome=outcome,
            resource_type=event.resource_type,
            resource_id=event.resource_id,
            actor_user_id=event.actor_user_id,
            request_id=event.request_id,
            ip_address=event.ip_address,
            event_metadata=event.metadata,
        )

        try:
            self._session.add(row)
            await self._session.commit()
            logger.info(
                "audit | action=%s outcome=%s actor=%s resource=%s:%s request_id=%s",
                event.action,
                outcome,
                event.actor_user_id,
                event.resource_type,
                event.resource_id,
                event.request_id,
            )
        except Exception:
            await self._session.rollback()
            logger.exception("Falha ao persistir evento de auditoria action=%s", event.action)
