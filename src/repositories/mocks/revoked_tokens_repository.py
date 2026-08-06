from __future__ import annotations

from datetime import datetime

from repositories.base import RevokedTokensRepository
from repositories.mocks.data import get_mock_store


class MockRevokedTokensRepository(RevokedTokensRepository):
    def __init__(self) -> None:
        self._store = get_mock_store()

    async def is_revoked(self, jti: str) -> bool:
        return jti in self._store.revoked_jtis

    async def revoke(
        self,
        *,
        jti: str,
        token_type: str,
        user_id: int | None,
        expires_at: datetime,
    ) -> None:
        self._store.revoked_jtis.add(jti)
