from __future__ import annotations

from domain.dtos.user_dtos import RoleCreateDTO, RoleUpdateDTO
from models.roles import Roles
from repositories.base import RolesRepository
from repositories.mocks.data import get_mock_store
from services.utils import utcnow


class MockRolesRepository(RolesRepository):
    def __init__(self) -> None:
        self._store = get_mock_store()

    async def list_active(self) -> list[Roles]:
        return [
            self._store.clone_role(role)
            for role in self._store.roles.values()
            if role.active
        ]

    async def get_by_id(self, role_id: int) -> Roles | None:
        role = self._store.roles.get(role_id)
        if role and role.active:
            return self._store.clone_role(role)
        return None

    async def create(self, payload: RoleCreateDTO) -> Roles:
        role_id = self._store._next_role_id
        self._store._next_role_id += 1
        role = Roles(description=payload.description)
        role.id = role_id
        role.active = payload.active if payload.active is not None else True
        role.created_at = utcnow()
        self._store.roles[role_id] = role
        return self._store.clone_role(role)

    async def update(self, role_id: int, payload: RoleUpdateDTO) -> Roles | None:
        role = self._store.roles.get(role_id)
        if not role or not role.active:
            return None
        if payload.description:
            role.description = payload.description
        if payload.active is not None:
            role.active = payload.active
        return self._store.clone_role(role)

    async def soft_delete(self, role_id: int) -> Roles | None:
        role = self._store.roles.get(role_id)
        if not role or not role.active:
            return None
        role.active = False
        return self._store.clone_role(role)

    async def get_role_display(self, role_id: int) -> str | None:
        role = self._store.roles.get(role_id)
        if role and role.active:
            return role.get_role_display()
        return None
