from __future__ import annotations

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.revoked_tokens import RevokedTokens
from repositories.base import RevokedTokensRepository


class SqlAlchemyRevokedTokensRepository(RevokedTokensRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def is_revoked(self, jti: str) -> bool:
        async with self._session as session:
            query = select(RevokedTokens).filter(RevokedTokens.jti == jti)
            result = await session.execute(query)
            return result.scalars().unique().one_or_none() is not None

    async def revoke(
        self,
        *,
        jti: str,
        token_type: str,
        user_id: int | None,
        expires_at: datetime,
    ) -> None:
        if await self.is_revoked(jti):
            return

        async with self._session as session:
            record = RevokedTokens(
                jti=jti,
                token_type=token_type,
                user_id=user_id,
                expires_at=expires_at,
            )
            session.add(record)
            await session.commit()
