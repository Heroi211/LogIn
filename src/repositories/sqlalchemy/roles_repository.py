from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from domain.dtos.user_dtos import RoleCreateDTO, RoleUpdateDTO
from models.roles import Roles as roles_models
from repositories.base import RolesRepository


class SqlAlchemyRolesRepository(RolesRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_active(self) -> list[roles_models]:
        async with self._session as session:
            query = select(roles_models).filter(roles_models.active == True)
            result = await session.execute(query)
            return result.scalars().unique().all()

    async def get_by_id(self, role_id: int) -> roles_models | None:
        async with self._session as session:
            query = select(roles_models).filter(
                roles_models.id == role_id, roles_models.active == True
            )
            result = await session.execute(query)
            return result.scalars().unique().one_or_none()

    async def create(self, payload: RoleCreateDTO) -> roles_models:
        async with self._session as session:
            new_role = roles_models(description=payload.description)
            new_role.active = payload.active
            session.add(new_role)
            await session.commit()
            await session.refresh(new_role)
            return new_role

    async def update(self, role_id: int, payload: RoleUpdateDTO) -> roles_models | None:
        async with self._session as session:
            query = select(roles_models).filter(
                roles_models.id == role_id, roles_models.active == True
            )
            result = await session.execute(query)
            role = result.scalars().unique().one_or_none()
            if not role:
                return None
            if payload.description:
                role.description = payload.description
            if payload.active is not None:
                role.active = payload.active
            await session.commit()
            await session.refresh(role)
            return role

    async def soft_delete(self, role_id: int) -> roles_models | None:
        async with self._session as session:
            query = select(roles_models).filter(
                roles_models.id == role_id, roles_models.active == True
            )
            result = await session.execute(query)
            role = result.scalars().unique().one_or_none()
            if not role:
                return None
            role.active = False
            await session.commit()
            await session.refresh(role)
            return role

    async def get_role_display(self, role_id: int) -> str | None:
        role = await self.get_by_id(role_id)
        return role.get_role_display() if role else None
