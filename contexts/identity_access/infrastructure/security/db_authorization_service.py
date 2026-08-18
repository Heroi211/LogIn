from __future__ import annotations

from contexts.identity_access.application.ports.authorization_service import AuthorizationService
from contexts.identity_access.application.ports.permission_repository import PermissionRepository
from contexts.identity_access.domain.rbac import role_has_any_permission
from contexts.identity_access.domain.role_type import RoleType
from contexts.identity_access.infrastructure.security.permission_cache import PermissionCache


class DbAuthorizationService:
    def __init__(
        self,
        permissions: PermissionRepository,
        cache: PermissionCache,
    ) -> None:
        self._permissions = permissions
        self._cache = cache

    async def get_permissions_for_role(self, role_id: int | None) -> frozenset[str]:
        if role_id is None:
            return frozenset()
        if role_id == RoleType.ADMINISTRATOR:
            perms = self._cache.get(role_id)
            if perms is not None:
                return perms
            loaded = await self._permissions.get_codes_for_role(role_id)
            self._cache.set(role_id, loaded)
            return loaded

        cached = self._cache.get(role_id)
        if cached is not None:
            return cached

        loaded = await self._permissions.get_codes_for_role(role_id)
        self._cache.set(role_id, loaded)
        return loaded

    async def user_has_any_permission(self, role_id: int | None, *permissions: str) -> bool:
        if not permissions:
            return False
        if role_id == RoleType.ADMINISTRATOR:
            return True
        role_perms = await self.get_permissions_for_role(role_id)
        return role_has_any_permission(role_id, role_perms, *permissions)

    def invalidate_cache(self, role_id: int | None = None) -> None:
        self._cache.invalidate(role_id)
