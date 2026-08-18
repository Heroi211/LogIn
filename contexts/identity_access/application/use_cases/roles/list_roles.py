from __future__ import annotations

from contexts.identity_access.application.dto.roles import RoleRecord
from contexts.identity_access.application.mappers import role_to_record
from contexts.identity_access.application.ports.role_repository import RoleRepository


class ListRoles:
    def __init__(self, roles: RoleRepository) -> None:
        self._roles = roles

    async def execute(self) -> list[RoleRecord]:
        return [role_to_record(r) for r in await self._roles.list_active()]
