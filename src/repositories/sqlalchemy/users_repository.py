from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from domain.dtos.user_dtos import UserCreateDTO
from domain.entities.user import UserEntity
from infrastructure.persistence.mappers import user_to_entity
from models.roles import Roles
from models.roles import Roles as roles_models
from models.users import Users as users_models
from repositories.base import UsersRepository


class SqlAlchemyUsersRepository(UsersRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: int) -> UserEntity | None:
        async with self._session as session:
            query = select(users_models).filter(
                users_models.id == user_id, users_models.active == True
            )
            result = await session.execute(query)
            user = result.scalars().unique().one_or_none()
            return user_to_entity(user) if user else None

    async def get_by_cpf(self, cpf: str) -> UserEntity | None:
        async with self._session as session:
            query = select(users_models).filter(
                users_models.cpf == cpf, users_models.active == True
            )
            result = await session.execute(query)
            user = result.scalars().unique().one_or_none()
            return user_to_entity(user) if user else None

    async def get_by_cpf_for_auth(self, cpf: str) -> UserEntity | None:
        async with self._session as session:
            query = select(users_models).filter(users_models.cpf == cpf)
            result = await session.execute(query)
            user = result.scalars().unique().one_or_none()
            return user_to_entity(user) if user else None

    async def get_by_email(self, email: str) -> UserEntity | None:
        async with self._session as session:
            query = select(users_models).filter(
                users_models.email == email, users_models.active == True
            )
            result = await session.execute(query)
            user = result.scalars().unique().one_or_none()
            return user_to_entity(user) if user else None

    async def get_by_google_id(self, google_id: str) -> UserEntity | None:
        async with self._session as session:
            query = select(users_models).filter(
                users_models.google_id == google_id, users_models.active == True
            )
            result = await session.execute(query)
            user = result.scalars().unique().one_or_none()
            return user_to_entity(user) if user else None

    async def get_by_reset_token(self, token: str) -> UserEntity | None:
        async with self._session as session:
            query = select(users_models).filter(
                users_models.reset_password_token == token, users_models.active == True
            )
            result = await session.execute(query)
            user = result.scalars().unique().one_or_none()
            return user_to_entity(user) if user else None

    async def list_with_role_display(self) -> list[dict[str, Any]]:
        async with self._session as session:
            query = (
                select(users_models)
                .order_by(users_models.id.asc())
                .filter(users_models.active == True)
            )
            result = await session.execute(query)
            users = result.scalars().unique().all()

            rows = []
            for user in users:
                role_query = select(roles_models).filter(
                    roles_models.id == user.role_id, roles_models.active == True
                )
                role_result = await session.execute(role_query)
                role = role_result.scalars().unique().one_or_none()
                rows.append(
                    {
                        "id": user.id,
                        "name": user.name,
                        "email": user.email,
                        "cpf": user.cpf,
                        "phone": user.phone,
                        "active": user.active,
                        "role": role.get_role_display() if role else None,
                    }
                )
            return rows

    async def create(self, payload: UserCreateDTO, password_hash: str) -> UserEntity:
        async with self._session as session:
            new_user = users_models(
                name=payload.name,
                email=payload.email,
                cpf=payload.cpf,
                phone=payload.phone,
                password=password_hash,
                role_id=payload.role_id,
                auth_provider="local",
            )
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            return user_to_entity(new_user)

    async def create_oauth_user(
        self,
        *,
        name: str,
        email: str,
        google_id: str,
        role_id: int = Roles.OPERATOR,
    ) -> UserEntity:
        async with self._session as session:
            new_user = users_models(
                name=name,
                email=email,
                phone="00000000000",
                cpf=None,
                password=None,
                auth_provider="google",
                google_id=google_id,
                role_id=role_id,
            )
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            return user_to_entity(new_user)

    async def update(self, user_id: int, data: dict[str, Any]) -> UserEntity | None:
        async with self._session as session:
            query = select(users_models).filter(
                users_models.id == user_id, users_models.active == True
            )
            result = await session.execute(query)
            user = result.scalars().unique().one_or_none()
            if not user:
                return None
            if data.get("name"):
                user.name = data["name"]
            if data.get("email"):
                user.email = data["email"]
            if data.get("active") is not None:
                user.active = data["active"]
            if data.get("phone"):
                user.phone = data["phone"]
            if data.get("cpf"):
                user.cpf = data["cpf"]
            if data.get("google_id"):
                user.google_id = data["google_id"]
            if data.get("auth_provider"):
                user.auth_provider = data["auth_provider"]
            if data.get("role_id") is not None:
                user.role_id = data["role_id"]
            if data.get("failed_login_attempts") is not None:
                user.failed_login_attempts = data["failed_login_attempts"]
            if data.get("active") is True:
                user.failed_login_attempts = 0
            await session.commit()
            await session.refresh(user)
            return user_to_entity(user)

    async def soft_delete(self, user_id: int) -> UserEntity | None:
        async with self._session as session:
            query = select(users_models).filter(
                users_models.id == int(user_id), users_models.active == True
            )
            result = await session.execute(query)
            user = result.scalars().unique().one_or_none()
            if not user:
                return None
            user.active = False
            await session.commit()
            await session.refresh(user)
            return user_to_entity(user)

    async def set_reset_token(self, user_id: int, token: str, expires: datetime) -> UserEntity | None:
        async with self._session as session:
            query = select(users_models).filter(
                users_models.id == user_id, users_models.active == True
            )
            result = await session.execute(query)
            user = result.scalars().unique().one_or_none()
            if not user:
                return None
            user.reset_password_token = token
            user.reset_password_expires = expires
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user_to_entity(user)

    async def reset_password(self, user_id: int, password_hash: str) -> UserEntity | None:
        async with self._session as session:
            query = select(users_models).filter(users_models.id == user_id)
            result = await session.execute(query)
            user = result.scalars().unique().one_or_none()
            if not user:
                return None
            user.password = password_hash
            user.auth_provider = "local"
            user.reset_password_token = None
            user.reset_password_expires = None
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user_to_entity(user)
