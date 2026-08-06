"""Emissão de tokens JWT + sessão server-side."""

from __future__ import annotations

from dataclasses import dataclass

from application.dtos.auth_result import AuthResult
from application.services.session_revocation import SessionRevocationService
from core.auth import create_token_response
from core.configs import settings
from domain.entities.user import UserEntity
from domain.ports.repositories import RevokedTokensRepositoryPort, SessionsRepositoryPort
from infrastructure.auth.token_utils import generate_session_token, hash_token, session_expires_at


@dataclass
class IssueAuthUseCase:
    sessions: SessionsRepositoryPort
    revoked_tokens: RevokedTokensRepositoryPort

    @property
    def _revocation(self) -> SessionRevocationService:
        return SessionRevocationService(self.sessions, self.revoked_tokens)

    async def execute(
        self,
        user: UserEntity,
        *,
        ip_address: str | None = None,
        user_agent: str | None = None,
        revoke_existing: bool = True,
        prior_refresh_token: str | None = None,
        prior_access_token: str | None = None,
    ) -> AuthResult:
        if revoke_existing and user.id is not None:
            await self._revocation.revoke_user_access(
                user.id,
                refresh_token=prior_refresh_token,
                access_token=prior_access_token,
            )

        session_token = generate_session_token()
        await self.sessions.create(
            user_id=user.id,
            token_hash=hash_token(session_token),
            expires_at=session_expires_at(days=int(settings.SESSION_EXPIRE_DAYS)),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return AuthResult(
            token_response=create_token_response(user),
            session_token=session_token,
        )
