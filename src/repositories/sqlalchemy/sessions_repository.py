from __future__ import annotations

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from domain.entities.user import ApiKeyEntity, SessionEntity
from infrastructure.auth.token_utils import hash_token
from infrastructure.persistence.mappers import api_key_to_entity, session_to_entity
from models.api_keys import ApiKeys
from models.sessions import Sessions
from repositories.base import ApiKeysRepository, SessionsRepository
from services.utils import utcnow


class SqlAlchemySessionsRepository(SessionsRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        user_id: int,
        token_hash: str,
        expires_at: datetime,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> SessionEntity:
        async with self._session as session:
            record = Sessions(
                user_id=user_id,
                token_hash=token_hash,
                expires_at=expires_at,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            session.add(record)
            await session.commit()
            await session.refresh(record)
            return session_to_entity(record)

    async def get_by_token_hash(self, token_hash: str) -> SessionEntity | None:
        async with self._session as session:
            query = select(Sessions).filter(
                Sessions.token_hash == token_hash,
                Sessions.active == True,
            )
            result = await session.execute(query)
            record = result.scalars().unique().one_or_none()
            if not record:
                return None
            if record.expires_at < utcnow():
                record.active = False
                await session.commit()
                return None
            return session_to_entity(record)

    async def revoke(self, token_hash: str) -> bool:
        async with self._session as session:
            query = select(Sessions).filter(
                Sessions.token_hash == token_hash,
                Sessions.active == True,
            )
            result = await session.execute(query)
            record = result.scalars().unique().one_or_none()
            if not record:
                return False
            record.active = False
            await session.commit()
            return True

    async def revoke_all_for_user(self, user_id: int) -> int:
        async with self._session as session:
            query = select(Sessions).filter(
                Sessions.user_id == user_id,
                Sessions.active == True,
            )
            result = await session.execute(query)
            records = result.scalars().unique().all()
            for record in records:
                record.active = False
            await session.commit()
            return len(records)


class SqlAlchemyApiKeysRepository(ApiKeysRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        key_prefix: str,
        key_hash: str,
        name: str,
        user_id: int,
        scopes: str,
        expires_at: datetime | None = None,
    ) -> ApiKeyEntity:
        async with self._session as session:
            record = ApiKeys(
                key_prefix=key_prefix,
                key_hash=key_hash,
                name=name,
                user_id=user_id,
                scopes=scopes,
                expires_at=expires_at,
            )
            session.add(record)
            await session.commit()
            await session.refresh(record)
            return api_key_to_entity(record)

    async def get_by_prefix(self, key_prefix: str) -> ApiKeyEntity | None:
        async with self._session as session:
            query = select(ApiKeys).filter(
                ApiKeys.key_prefix == key_prefix,
                ApiKeys.active == True,
            )
            result = await session.execute(query)
            record = result.scalars().unique().one_or_none()
            return api_key_to_entity(record) if record else None

    async def list_by_user(self, user_id: int) -> list[ApiKeyEntity]:
        async with self._session as session:
            query = select(ApiKeys).filter(
                ApiKeys.user_id == user_id,
                ApiKeys.active == True,
            )
            result = await session.execute(query)
            records = result.scalars().unique().all()
            return [api_key_to_entity(record) for record in records]

    async def revoke(self, api_key_id: int, user_id: int | None = None) -> bool:
        async with self._session as session:
            query = select(ApiKeys).filter(ApiKeys.id == api_key_id, ApiKeys.active == True)
            if user_id is not None:
                query = query.filter(ApiKeys.user_id == user_id)
            result = await session.execute(query)
            record = result.scalars().unique().one_or_none()
            if not record:
                return False
            record.active = False
            await session.commit()
            return True

    async def verify_key(self, full_key: str) -> ApiKeyEntity | None:
        if not full_key.startswith("ltk_"):
            return None
        parts = full_key.split("_", 2)
        if len(parts) != 3:
            return None
        prefix = parts[1]
        entity = await self.get_by_prefix(prefix)
        if not entity:
            return None
        if entity.key_hash != hash_token(full_key):
            return None
        if entity.expires_at and entity.expires_at < utcnow():
            return None
        return entity
