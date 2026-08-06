from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from application.dtos.auth_result import AuthResult
from application.services.session_revocation import SessionRevocationService
from application.use_cases.issue_auth import IssueAuthUseCase
from core.auth import (
    REFRESH_TOKEN_TYPE,
    decode_refresh_token_safe,
    token_expires_at_from_payload,
)
from core.configs import settings
from core.security import verify_password
from domain.entities.user import UserEntity
from domain.exceptions import (
    AccountLockedError,
    InvalidCredentialsError,
    OAuthLinkRequiredError,
    TokenRevokedError,
)
from domain.ports.repositories import (
    ApiKeysRepositoryPort,
    RevokedTokensRepositoryPort,
    SessionsRepositoryPort,
    UsersRepositoryPort,
)
from infrastructure.auth.token_utils import generate_api_key, hash_token


@dataclass
class LoginUserUseCase:
    users: UsersRepositoryPort
    sessions: SessionsRepositoryPort
    revoked_tokens: RevokedTokensRepositoryPort

    @property
    def _revocation(self) -> SessionRevocationService:
        return SessionRevocationService(self.sessions, self.revoked_tokens)

    @property
    def _issue(self) -> IssueAuthUseCase:
        return IssueAuthUseCase(self.sessions, self.revoked_tokens)

    async def execute(
        self,
        cpf: str,
        password: str,
        *,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AuthResult:
        max_attempts = settings.max_failed_login_attempts
        user = await self.users.get_by_cpf_for_auth(cpf)

        if not user:
            raise InvalidCredentialsError("Dados incorretos.")

        if not user.active:
            raise AccountLockedError("Conta bloqueada. Contate o administrador.")

        if not user.password_hash or not verify_password(password, user.password_hash):
            attempts = user.failed_login_attempts + 1
            update_data: dict = {"failed_login_attempts": attempts}
            if attempts >= max_attempts:
                update_data["active"] = False
            await self.users.update(user.id, update_data)

            if attempts >= max_attempts and user.id is not None:
                await self._revocation.revoke_all_for_user(user.id)
                raise AccountLockedError(
                    f"Conta bloqueada após {max_attempts} tentativas incorretas. Contate o administrador."
                )

            remaining = max_attempts - attempts
            raise InvalidCredentialsError(
                f"Dados incorretos. {remaining} tentativa(s) restante(s)."
            )

        if user.failed_login_attempts:
            await self.users.update(user.id, {"failed_login_attempts": 0})

        return await self._issue.execute(
            user,
            ip_address=ip_address,
            user_agent=user_agent,
            revoke_existing=True,
        )


@dataclass
class LogoutUserUseCase:
    sessions: SessionsRepositoryPort
    revoked_tokens: RevokedTokensRepositoryPort
    users: UsersRepositoryPort

    @property
    def _revocation(self) -> SessionRevocationService:
        return SessionRevocationService(self.sessions, self.revoked_tokens)

    async def execute(
        self,
        session_token: str | None,
        *,
        refresh_token: str | None = None,
        access_token: str | None = None,
    ) -> bool:
        user_id: int | None = None

        if session_token:
            session_entity = await self.sessions.get_by_token_hash(hash_token(session_token))
            if session_entity:
                user_id = session_entity.user_id

        if user_id is None and refresh_token:
            try:
                payload = decode_refresh_token_safe(refresh_token)
                user_id = int(payload["sub"])
            except InvalidCredentialsError:
                pass

        if user_id is None and access_token:
            try:
                from core.auth import decode_token_payload_safe

                payload = decode_token_payload_safe(access_token)
                user_id = int(payload["sub"])
            except InvalidCredentialsError:
                pass

        if user_id is not None:
            await self._revocation.revoke_user_access(
                user_id,
                session_token=session_token,
                refresh_token=refresh_token,
                access_token=access_token,
            )
            return True

        await self._revocation.revoke_session_token(session_token)
        await self._revocation.revoke_jwt_if_valid(refresh_token)
        await self._revocation.revoke_jwt_if_valid(access_token)
        return True


@dataclass
class RefreshTokenUseCase:
    users: UsersRepositoryPort
    sessions: SessionsRepositoryPort
    revoked_tokens: RevokedTokensRepositoryPort

    @property
    def _issue(self) -> IssueAuthUseCase:
        return IssueAuthUseCase(self.sessions, self.revoked_tokens)

    async def execute(
        self,
        refresh_token: str,
        *,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AuthResult:
        payload = decode_refresh_token_safe(refresh_token)
        jti = payload["jti"]

        if await self.revoked_tokens.is_revoked(jti):
            raise TokenRevokedError("Refresh token revogado.")

        user = await self.users.get_by_id(int(payload["sub"]))
        if not user or not user.active:
            raise InvalidCredentialsError("Usuário não encontrado ou inativo.")

        await self.revoked_tokens.revoke(
            jti=jti,
            token_type=REFRESH_TOKEN_TYPE,
            user_id=user.id,
            expires_at=token_expires_at_from_payload(payload),
        )

        return await self._issue.execute(
            user,
            ip_address=ip_address,
            user_agent=user_agent,
            revoke_existing=True,
            prior_refresh_token=refresh_token,
        )


@dataclass
class GoogleOAuthUseCase:
    users: UsersRepositoryPort
    sessions: SessionsRepositoryPort
    revoked_tokens: RevokedTokensRepositoryPort
    google: object

    @property
    def _issue(self) -> IssueAuthUseCase:
        return IssueAuthUseCase(self.sessions, self.revoked_tokens)

    async def execute(
        self,
        *,
        code: str | None = None,
        id_token: str | None = None,
        state: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AuthResult:
        self.google.validate_state(state)

        if code:
            profile = await self.google.exchange_code(code)
        elif id_token:
            if settings.is_production:
                raise InvalidCredentialsError(
                    "id_token direto não permitido em production. Use fluxo com code."
                )
            profile = await self.google.verify_id_token(id_token)
        else:
            raise InvalidCredentialsError("Informe code ou id_token.")

        google_id = profile["sub"]
        email = profile["email"]
        name = profile.get("name") or email.split("@")[0]

        user = await self.users.get_by_google_id(google_id)
        if not user:
            existing = await self.users.get_by_email(email)
            if existing and not existing.google_id:
                raise OAuthLinkRequiredError(
                    "Conta local já existe com este e-mail. "
                    "Vincule via POST /v1/auth/google/link com CPF e senha."
                )
            if existing:
                user = existing
            else:
                user = await self.users.create_oauth_user(
                    name=name,
                    email=email,
                    google_id=google_id,
                )

        if not user.active:
            raise AccountLockedError("Conta bloqueada. Contate o administrador.")

        return await self._issue.execute(
            user,
            ip_address=ip_address,
            user_agent=user_agent,
            revoke_existing=True,
        )


@dataclass
class GoogleLinkAccountUseCase:
    users: UsersRepositoryPort
    google: object

    async def execute(
        self,
        *,
        cpf: str,
        password: str,
        id_token: str | None = None,
        code: str | None = None,
        state: str | None = None,
    ) -> UserEntity:
        self.google.validate_state(state)

        if code:
            profile = await self.google.exchange_code(code)
        elif id_token:
            if settings.is_production:
                raise InvalidCredentialsError(
                    "id_token direto não permitido em production. Use fluxo com code."
                )
            profile = await self.google.verify_id_token(id_token)
        else:
            raise InvalidCredentialsError("Informe code ou id_token.")

        user = await self.users.get_by_cpf_for_auth(cpf)
        if not user or not user.active:
            raise InvalidCredentialsError("CPF ou senha incorretos.")
        if not user.password_hash or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError("CPF ou senha incorretos.")

        google_id = profile["sub"]
        if await self.users.get_by_google_id(google_id):
            raise InvalidCredentialsError("Conta Google já vinculada a outro usuário.")

        email = profile["email"]
        updated = await self.users.update(
            user.id,
            {
                "google_id": google_id,
                "auth_provider": "google",
                "email": email,
                "name": profile.get("name") or user.name,
            },
        )
        if not updated:
            raise InvalidCredentialsError("Não foi possível vincular a conta Google.")
        return updated


@dataclass
class CreateApiKeyUseCase:
    api_keys: ApiKeysRepositoryPort
    users: UsersRepositoryPort

    async def execute(
        self,
        *,
        user_id: int,
        name: str,
        scopes: str = "read",
        expires_at: datetime | None = None,
    ) -> tuple[str, object]:
        full_key, prefix, key_hash = generate_api_key()
        entity = await self.api_keys.create(
            key_prefix=prefix,
            key_hash=key_hash,
            name=name,
            user_id=user_id,
            scopes=scopes,
            expires_at=expires_at,
        )
        return full_key, entity


@dataclass
class RevokeApiKeyUseCase:
    api_keys: ApiKeysRepositoryPort

    async def execute(self, api_key_id: int, user_id: int) -> bool:
        return await self.api_keys.revoke(api_key_id, user_id=user_id)
