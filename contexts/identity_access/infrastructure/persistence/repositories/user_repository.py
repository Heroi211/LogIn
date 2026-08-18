from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from contexts.identity_access.domain.entities.user import User
from contexts.identity_access.domain.exceptions import DuplicateUserError
from contexts.identity_access.infrastructure.persistence.mappers import orm_to_user, user_to_orm
from contexts.identity_access.infrastructure.persistence.models.users import Users
from contexts.identity_access.infrastructure.security.token_hash import hash_reset_token


class SqlAlchemyUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: int, *, active_only: bool = True) -> User | None:
        query = select(Users).filter(Users.id == user_id)
        if active_only:
            query = query.filter(Users.active.is_(True))
        result = await self._session.execute(query)
        entity = result.scalars().unique().one_or_none()
        return orm_to_user(entity) if entity else None

    async def get_by_cpf(self, cpf: str) -> User | None:
        result = await self._session.execute(select(Users).filter(Users.cpf == cpf))
        entity = result.scalars().unique().one_or_none()
        return orm_to_user(entity) if entity else None

    async def get_by_email(self, email: str, *, active_only: bool = True) -> User | None:
        query = select(Users).filter(Users.email == email)
        if active_only:
            query = query.filter(Users.active.is_(True))
        result = await self._session.execute(query)
        entity = result.scalars().unique().one_or_none()
        return orm_to_user(entity) if entity else None

    async def get_by_reset_token(self, token: str) -> User | None:
        token_hash = hash_reset_token(token)
        result = await self._session.execute(
            select(Users).filter(
                Users.reset_password_token == token_hash,
                Users.active.is_(True),
                Users.blocked.is_(False),
            )
        )
        entity = result.scalars().unique().one_or_none()
        return orm_to_user(entity) if entity else None

    async def list_active(self) -> list[User]:
        result = await self._session.execute(
            select(Users).order_by(Users.id.asc()).filter(Users.active.is_(True))
        )
        return [orm_to_user(u) for u in result.scalars().unique().all()]

    async def add(self, user: User) -> User:
        entity = user_to_orm(user)
        self._session.add(entity)
        try:
            await self._session.commit()
        except IntegrityError as exc:
            await self._session.rollback()
            raise DuplicateUserError("Usuário já cadastrado na base de dados") from exc
        await self._session.refresh(entity)
        return orm_to_user(entity)

    async def save(self, user: User) -> User:
        if user.id is None:
            return await self.add(user)

        result = await self._session.execute(select(Users).filter(Users.id == user.id.value))
        entity = result.scalars().unique().one_or_none()
        if entity is None:
            raise DuplicateUserError(f"Usuário id={user.id.value} não encontrado para persistência.")

        user_to_orm(user, entity)
        try:
            await self._session.commit()
        except IntegrityError as exc:
            await self._session.rollback()
            raise DuplicateUserError("Conflito ao atualizar usuário.") from exc
        await self._session.refresh(entity)
        return orm_to_user(entity)
