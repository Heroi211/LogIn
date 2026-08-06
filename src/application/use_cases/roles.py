from __future__ import annotations

from dataclasses import dataclass

from domain.dtos.user_dtos import RoleCreateDTO, RoleUpdateDTO
from domain.exceptions import EntityNotFoundError
from domain.ports.repositories import RolesRepositoryPort
from schemas import roles_schemas


@dataclass
class ListRolesUseCase:
    roles: RolesRepositoryPort

    async def execute(self):
        return await self.roles.list_active()


@dataclass
class GetRoleUseCase:
    roles: RolesRepositoryPort

    async def execute(self, role_id: int):
        return await self.roles.get_by_id(role_id)


@dataclass
class CreateRoleUseCase:
    roles: RolesRepositoryPort

    async def execute(self, payload: roles_schemas.role):
        dto = RoleCreateDTO(description=payload.description, active=payload.active)
        return await self.roles.create(dto)


@dataclass
class UpdateRoleUseCase:
    roles: RolesRepositoryPort

    async def execute(self, role_id: int, payload: roles_schemas.role_update):
        dto = RoleUpdateDTO(description=payload.description, active=payload.active)
        updated = await self.roles.update(role_id, dto)
        if not updated:
            raise EntityNotFoundError("Role não encontrada.")
        return updated


@dataclass
class DeleteRoleUseCase:
    roles: RolesRepositoryPort

    async def execute(self, role_id: int):
        deleted = await self.roles.soft_delete(role_id)
        if not deleted:
            raise EntityNotFoundError("Role não encontrada.")
        return deleted
