"""Limpeza de JTIs expirados na blacklist."""

from __future__ import annotations

import logging
from datetime import datetime

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from core.configs import settings
from core.database import Session
from models.revoked_tokens import RevokedTokens

logger = logging.getLogger(__name__)


async def purge_expired_revoked_tokens() -> int:
    if settings.is_development or Session is None:
        return 0

    async with Session() as session:
        session: AsyncSession
        result = await session.execute(
            delete(RevokedTokens).where(RevokedTokens.expires_at < datetime.utcnow())
        )
        await session.commit()
        removed = result.rowcount or 0
        if removed:
            logger.info("revoked_tokens cleanup: removidos %s registros expirados", removed)
        return removed
