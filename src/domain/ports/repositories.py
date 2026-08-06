from __future__ import annotations

from datetime import datetime
from typing import Any

from domain.dtos.user_dtos import RoleCreateDTO, RoleUpdateDTO, UserCreateDTO
from domain.entities.user import ApiKeyEntity, SessionEntity, UserEntity


class UsersRepositoryPort:
    async def get_by_id(self, user_id: int) -> UserEntity | None: ...

    async def get_by_cpf(self, cpf: str) -> UserEntity | None: ...

    async def get_by_cpf_for_auth(self, cpf: str) -> UserEntity | None: ...

    async def get_by_email(self, email: str) -> UserEntity | None: ...

    async def get_by_google_id(self, google_id: str) -> UserEntity | None: ...

    async def get_by_reset_token(self, token: str) -> UserEntity | None: ...

    async def list_with_role_display(self) -> list[dict[str, Any]]: ...

    async def create(self, payload: UserCreateDTO, password_hash: str) -> UserEntity: ...

    async def create_oauth_user(
        self,
        *,
        name: str,
        email: str,
        google_id: str,
        role_id: int = 1,
    ) -> UserEntity: ...

    async def update(self, user_id: int, data: dict[str, Any]) -> UserEntity | None: ...

    async def soft_delete(self, user_id: int) -> UserEntity | None: ...

    async def set_reset_token(self, user_id: int, token: str, expires: datetime) -> UserEntity | None: ...

    async def reset_password(self, user_id: int, password_hash: str) -> UserEntity | None: ...


class RolesRepositoryPort:
    async def list_active(self) -> list[Any]: ...

    async def get_by_id(self, role_id: int) -> Any | None: ...

    async def create(self, payload: RoleCreateDTO) -> Any: ...

    async def update(self, role_id: int, payload: RoleUpdateDTO) -> Any | None: ...

    async def soft_delete(self, role_id: int) -> Any | None: ...

    async def get_role_display(self, role_id: int) -> str | None: ...


class SessionsRepositoryPort:
    async def create(
        self,
        *,
        user_id: int,
        token_hash: str,
        expires_at: datetime,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> SessionEntity: ...

    async def get_by_token_hash(self, token_hash: str) -> SessionEntity | None: ...

    async def revoke(self, token_hash: str) -> bool: ...

    async def revoke_all_for_user(self, user_id: int) -> int: ...


class ApiKeysRepositoryPort:
    async def create(
        self,
        *,
        key_prefix: str,
        key_hash: str,
        name: str,
        user_id: int,
        scopes: str,
        expires_at: datetime | None = None,
    ) -> ApiKeyEntity: ...

    async def get_by_prefix(self, key_prefix: str) -> ApiKeyEntity | None: ...

    async def list_by_user(self, user_id: int) -> list[ApiKeyEntity]: ...

    async def revoke(self, api_key_id: int, user_id: int | None = None) -> bool: ...

    async def verify_key(self, full_key: str) -> ApiKeyEntity | None: ...


class RevokedTokensRepositoryPort:
    async def is_revoked(self, jti: str) -> bool: ...

    async def revoke(
        self,
        *,
        jti: str,
        token_type: str,
        user_id: int | None,
        expires_at: datetime,
    ) -> None: ...
