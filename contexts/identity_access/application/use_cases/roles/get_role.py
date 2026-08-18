from __future__ import annotations

from contexts.identity_access.application.dto.roles import RoleRecord
from contexts.identity_access.application.exceptions import RoleNotFoundError
from contexts.identity_access.application.mappers import role_to_record
from contexts.identity_access.application.ports.role_repository import RoleRepository


class GetRoleById:
    def __init__(self, roles: RoleRepository) -> None:
        self._roles = roles

    async def execute(self, role_id: int) -> RoleRecord:
        role = await self._roles.get_by_id(role_id)
        if not role:
            raise RoleNotFoundError("Papel não encontrado.")
        return role_to_record(role)
