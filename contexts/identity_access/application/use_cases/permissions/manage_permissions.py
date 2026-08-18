from __future__ import annotations

from contexts.identity_access.application.dto.roles import CreatePermissionInput, PermissionRecord
from contexts.identity_access.application.exceptions import DuplicateUserError
from contexts.identity_access.application.ports.audit_logger import AuditLogger
from contexts.identity_access.application.ports.permission_repository import PermissionRepository
from contexts.identity_access.domain.audit.actions import AuditAction
from contexts.identity_access.domain.entities.permission import Permission
from contexts.identity_access.domain.exceptions import DuplicateUserError as DomainDuplicateError


def permission_to_record(permission: Permission) -> PermissionRecord:
    assert permission.id is not None
    return PermissionRecord(
        id=permission.id,
        code=permission.code,
        description=permission.description,
        module=permission.module,
        active=permission.active,
    )


class ListPermissions:
    def __init__(self, permissions: PermissionRepository) -> None:
        self._permissions = permissions

    async def execute(self) -> list[PermissionRecord]:
        return [permission_to_record(p) for p in await self._permissions.list_active()]


class CreatePermission:
    def __init__(
        self,
        permissions: PermissionRepository,
        audit: AuditLogger | None = None,
    ) -> None:
        self._permissions = permissions
        self._audit = audit

    async def execute(self, data: CreatePermissionInput, audit_ctx=None) -> PermissionRecord:
        permission = Permission.create(
            code=data.code,
            description=data.description,
            module=data.module,
        )
        try:
            saved = await self._permissions.add(permission)
        except DomainDuplicateError as exc:
            raise DuplicateUserError(str(exc)) from exc

        from contexts.identity_access.application.use_cases._audit import record_audit

        await record_audit(
            self._audit,
            audit_ctx,
            action=AuditAction.PERMISSION_CREATED,
            outcome="success",
            resource_type="permission",
            resource_id=saved.code,
            actor_user_id=audit_ctx.actor_user_id if audit_ctx else None,
        )
        return permission_to_record(saved)
