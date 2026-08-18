from __future__ import annotations

from contexts.identity_access.application.dto.audit import AuditContext
from contexts.identity_access.application.dto.roles import RoleRecord, SetRolePermissionsInput
from contexts.identity_access.application.exceptions import PermissionNotFoundError, RoleNotFoundError
from contexts.identity_access.application.mappers import role_to_record
from contexts.identity_access.application.ports.audit_logger import AuditLogger
from contexts.identity_access.application.ports.authorization_service import AuthorizationService
from contexts.identity_access.application.ports.permission_repository import PermissionRepository
from contexts.identity_access.application.ports.role_repository import RoleRepository
from contexts.identity_access.application.use_cases._audit import record_audit
from contexts.identity_access.domain.audit.actions import AuditAction
from contexts.identity_access.domain.exceptions import PermissionNotFoundError as DomainPermissionNotFound
from contexts.identity_access.domain.exceptions import RoleNotFoundError as DomainRoleNotFound


class SetRolePermissions:
    def __init__(
        self,
        roles: RoleRepository,
        permissions: PermissionRepository,
        authz: AuthorizationService,
        audit: AuditLogger | None = None,
    ) -> None:
        self._roles = roles
        self._permissions = permissions
        self._authz = authz
        self._audit = audit

    async def execute(
        self,
        role_id: int,
        data: SetRolePermissionsInput,
        audit_ctx: AuditContext | None = None,
    ) -> RoleRecord:
        role = await self._roles.get_by_id(role_id, active_only=False)
        if not role:
            raise RoleNotFoundError("Papel não encontrado.")

        try:
            codes = await self._permissions.set_role_permissions(role_id, list(data.permissions))
        except DomainPermissionNotFound as exc:
            raise PermissionNotFoundError(str(exc)) from exc
        except DomainRoleNotFound as exc:
            raise RoleNotFoundError(str(exc)) from exc

        self._authz.invalidate_cache(role_id)
        role.set_permissions(codes)

        await record_audit(
            self._audit,
            audit_ctx,
            action=AuditAction.ROLE_PERMISSIONS_UPDATED,
            outcome="success",
            resource_type="role",
            resource_id=role_id,
            actor_user_id=audit_ctx.actor_user_id if audit_ctx else None,
            metadata={"permissions": sorted(codes)},
        )
        return role_to_record(role)


class GetMyPermissions:
    def __init__(self, authz: AuthorizationService) -> None:
        self._authz = authz

    async def execute(self, role_id: int | None) -> list[str]:
        perms = await self._authz.get_permissions_for_role(role_id)
        return sorted(perms)
