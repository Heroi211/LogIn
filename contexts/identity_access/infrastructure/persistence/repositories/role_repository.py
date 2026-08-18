from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from contexts.identity_access.domain.entities.role import Role
from contexts.identity_access.infrastructure.persistence.mappers import orm_to_role, role_to_orm
from contexts.identity_access.infrastructure.persistence.models.roles import Roles


class SqlAlchemyRoleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _base_query(self):
        return select(Roles).options(selectinload(Roles.permissions))

    async def get_by_id(self, role_id: int, *, active_only: bool = True) -> Role | None:
        query = self._base_query().filter(Roles.id == role_id)
        if active_only:
            query = query.filter(Roles.active.is_(True))
        result = await self._session.execute(query)
        entity = result.scalars().unique().one_or_none()
        return orm_to_role(entity) if entity else None

    async def list_active(self) -> list[Role]:
        result = await self._session.execute(
            self._base_query().filter(Roles.active.is_(True)).order_by(Roles.id.asc())
        )
        return [orm_to_role(r) for r in result.scalars().unique().all()]

    async def add(self, role: Role) -> Role:
        entity = role_to_orm(role)
        self._session.add(entity)
        await self._session.commit()
        await self._session.refresh(entity)
        return orm_to_role(entity)

    async def save(self, role: Role) -> Role:
        if role.id is None:
            return await self.add(role)

        result = await self._session.execute(select(Roles).filter(Roles.id == role.id))
        entity = result.scalars().unique().one_or_none()
        if entity is None:
            raise ValueError(f"Role id={role.id} não encontrada.")

        role_to_orm(role, entity)
        await self._session.commit()
        await self._session.refresh(entity)
        return orm_to_role(entity)
