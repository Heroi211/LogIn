from __future__ import annotations

from typing import Protocol


class AuthorizationService(Protocol):
    async def get_permissions_for_role(self, role_id: int | None) -> frozenset[str]: ...

    async def user_has_any_permission(self, role_id: int | None, *permissions: str) -> bool: ...

    def invalidate_cache(self, role_id: int | None = None) -> None: ...
