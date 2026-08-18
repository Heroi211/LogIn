from __future__ import annotations

from contexts.identity_access.application.dto.audit import AuditContext
from contexts.identity_access.application.dto.roles import RoleRecord, UpdateRoleInput
from contexts.identity_access.application.exceptions import RoleNotFoundError
from contexts.identity_access.application.mappers import role_to_record
from contexts.identity_access.application.ports.audit_logger import AuditLogger
from contexts.identity_access.application.ports.role_repository import RoleRepository
from contexts.identity_access.application.use_cases._audit import record_audit
from contexts.identity_access.domain.audit.actions import AuditAction


class UpdateRole:
    def __init__(self, roles: RoleRepository, audit: AuditLogger | None = None) -> None:
        self._roles = roles
        self._audit = audit

    async def execute(
        self,
        role_id: int,
        data: UpdateRoleInput,
        audit_ctx: AuditContext | None = None,
    ) -> RoleRecord:
        role = await self._roles.get_by_id(role_id)
        if not role:
            raise RoleNotFoundError("Papel não encontrado.")

        role.update(description=data.description, active=data.active)
        saved = await self._roles.save(role)
        await record_audit(
            self._audit,
            audit_ctx,
            action=AuditAction.ROLE_UPDATED,
            outcome="success",
            resource_type="role",
            resource_id=role_id,
            actor_user_id=audit_ctx.actor_user_id if audit_ctx else None,
        )
        return role_to_record(saved)
