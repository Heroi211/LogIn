from __future__ import annotations

from typing import Protocol

from contexts.identity_access.domain.entities.role import Role


class RoleRepository(Protocol):
    async def get_by_id(self, role_id: int, *, active_only: bool = True) -> Role | None: ...

    async def list_active(self) -> list[Role]: ...

    async def add(self, role: Role) -> Role: ...

    async def save(self, role: Role) -> Role: ...
