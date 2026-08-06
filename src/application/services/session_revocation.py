"""Revogação unificada de sessões server-side e tokens JWT."""

from __future__ import annotations

from dataclasses import dataclass

from core.auth import decode_token_payload_safe
from domain.exceptions import InvalidCredentialsError
from domain.ports.repositories import RevokedTokensRepositoryPort, SessionsRepositoryPort
from infrastructure.auth.token_utils import hash_token


@dataclass
class SessionRevocationService:
    sessions: SessionsRepositoryPort
    revoked_tokens: RevokedTokensRepositoryPort

    async def revoke_all_for_user(self, user_id: int) -> int:
        return await self.sessions.revoke_all_for_user(user_id)

    async def revoke_session_token(self, session_token: str | None) -> bool:
        if not session_token:
            return False
        return await self.sessions.revoke(hash_token(session_token))

    async def revoke_jwt_if_valid(self, token: str | None) -> bool:
        if not token:
            return False
        try:
            payload = decode_token_payload_safe(token)
        except InvalidCredentialsError:
            return False

        jti = payload.get("jti")
        if not jti:
            return False

        from core.auth import token_expires_at_from_payload

        await self.revoked_tokens.revoke(
            jti=jti,
            token_type=payload.get("type", "unknown"),
            user_id=int(payload["sub"]) if payload.get("sub") else None,
            expires_at=token_expires_at_from_payload(payload),
        )
        return True

    async def revoke_user_access(
        self,
        user_id: int,
        *,
        session_token: str | None = None,
        refresh_token: str | None = None,
        access_token: str | None = None,
    ) -> None:
        await self.revoke_session_token(session_token)
        await self.revoke_all_for_user(user_id)
        await self.revoke_jwt_if_valid(refresh_token)
        await self.revoke_jwt_if_valid(access_token)
