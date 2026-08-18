from __future__ import annotations

from contexts.identity_access.application.dto.audit import AuditContext
from contexts.identity_access.application.dto.users import UserRecord
from contexts.identity_access.application.exceptions import UserNotFoundError
from contexts.identity_access.application.mappers import user_to_record
from contexts.identity_access.application.ports.audit_logger import AuditLogger
from contexts.identity_access.application.ports.user_repository import UserRepository
from contexts.identity_access.application.use_cases._audit import record_audit
from contexts.identity_access.domain.audit.actions import AuditAction


class UnblockUser:
    def __init__(self, users: UserRepository, audit: AuditLogger | None = None) -> None:
        self._users = users
        self._audit = audit

    async def execute(self, user_id: int, audit_ctx: AuditContext | None = None) -> UserRecord:
        user = await self._users.get_by_id(user_id, active_only=False)
        if not user:
            raise UserNotFoundError("Usuário não encontrado.")

        user.unblock()
        saved = await self._users.save(user)
        await record_audit(
            self._audit,
            audit_ctx,
            action=AuditAction.USER_UNBLOCKED,
            outcome="success",
            resource_type="user",
            resource_id=user_id,
            actor_user_id=audit_ctx.actor_user_id if audit_ctx else None,
        )
        return user_to_record(saved)
