from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from domain.dtos.user_dtos import RoleCreateDTO, RoleUpdateDTO, UserCreateDTO
from domain.entities.messaging import PhoneLookupResult, WhatsAppMessage, WhatsAppMessageResult
from domain.entities.user import ApiKeyEntity, SessionEntity, UserEntity
from domain.ports.messaging import WhatsAppMessagingPort
from domain.ports.repositories import (
    ApiKeysRepositoryPort,
    RevokedTokensRepositoryPort,
    RolesRepositoryPort,
    SessionsRepositoryPort,
    UsersRepositoryPort,
)
from models.roles import Roles

# Re-export ports for compatibilidade
__all__ = [
    "UsersRepository",
    "RolesRepository",
    "SessionsRepository",
    "ApiKeysRepository",
    "RevokedTokensRepository",
    "WhatsAppMessagingRepository",
    "UsersRepositoryPort",
    "RolesRepositoryPort",
    "SessionsRepositoryPort",
    "ApiKeysRepositoryPort",
]


class UsersRepository(UsersRepositoryPort, ABC):
    @abstractmethod
    async def get_by_id(self, user_id: int) -> UserEntity | None: ...

    @abstractmethod
    async def get_by_cpf(self, cpf: str) -> UserEntity | None: ...

    @abstractmethod
    async def get_by_cpf_for_auth(self, cpf: str) -> UserEntity | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> UserEntity | None: ...

    @abstractmethod
    async def get_by_google_id(self, google_id: str) -> UserEntity | None: ...

    @abstractmethod
    async def get_by_reset_token(self, token: str) -> UserEntity | None: ...

    @abstractmethod
    async def list_with_role_display(self) -> list[dict[str, Any]]: ...

    @abstractmethod
    async def create(self, payload: UserCreateDTO, password_hash: str) -> UserEntity: ...

    @abstractmethod
    async def create_oauth_user(
        self,
        *,
        name: str,
        email: str,
        google_id: str,
        role_id: int = 1,
    ) -> UserEntity: ...

    @abstractmethod
    async def update(self, user_id: int, data: dict[str, Any]) -> UserEntity | None: ...

    @abstractmethod
    async def soft_delete(self, user_id: int) -> UserEntity | None: ...

    @abstractmethod
    async def set_reset_token(self, user_id: int, token: str, expires: datetime) -> UserEntity | None: ...

    @abstractmethod
    async def reset_password(self, user_id: int, password_hash: str) -> UserEntity | None: ...


class RolesRepository(RolesRepositoryPort, ABC):
    @abstractmethod
    async def list_active(self) -> list[Roles]: ...

    @abstractmethod
    async def get_by_id(self, role_id: int) -> Roles | None: ...

    @abstractmethod
    async def create(self, payload: RoleCreateDTO) -> Roles: ...

    @abstractmethod
    async def update(self, role_id: int, payload: RoleUpdateDTO) -> Roles | None: ...

    @abstractmethod
    async def soft_delete(self, role_id: int) -> Roles | None: ...

    @abstractmethod
    async def get_role_display(self, role_id: int) -> str | None: ...


class SessionsRepository(SessionsRepositoryPort, ABC):
    @abstractmethod
    async def create(
        self,
        *,
        user_id: int,
        token_hash: str,
        expires_at: datetime,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> SessionEntity: ...

    @abstractmethod
    async def get_by_token_hash(self, token_hash: str) -> SessionEntity | None: ...

    @abstractmethod
    async def revoke(self, token_hash: str) -> bool: ...

    @abstractmethod
    async def revoke_all_for_user(self, user_id: int) -> int: ...


class ApiKeysRepository(ApiKeysRepositoryPort, ABC):
    @abstractmethod
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

    @abstractmethod
    async def get_by_prefix(self, key_prefix: str) -> ApiKeyEntity | None: ...

    @abstractmethod
    async def list_by_user(self, user_id: int) -> list[ApiKeyEntity]: ...

    @abstractmethod
    async def revoke(self, api_key_id: int, user_id: int | None = None) -> bool: ...

    @abstractmethod
    async def verify_key(self, full_key: str) -> ApiKeyEntity | None: ...


class RevokedTokensRepository(RevokedTokensRepositoryPort, ABC):
    @abstractmethod
    async def is_revoked(self, jti: str) -> bool: ...

    @abstractmethod
    async def revoke(
        self,
        *,
        jti: str,
        token_type: str,
        user_id: int | None,
        expires_at: datetime,
    ) -> None: ...


class WhatsAppMessagingRepository(WhatsAppMessagingPort, ABC):
    @abstractmethod
    async def send_message(self, message: WhatsAppMessage) -> WhatsAppMessageResult: ...

    @abstractmethod
    async def send_template(
        self,
        *,
        to: str,
        content_sid: str,
        content_variables: dict[str, str] | None = None,
    ) -> WhatsAppMessageResult: ...

    @abstractmethod
    async def get_message_status(self, message_sid: str) -> WhatsAppMessageResult: ...

    @abstractmethod
    async def lookup_phone(self, phone_number: str) -> PhoneLookupResult | None: ...

    @abstractmethod
    async def notify_admin(self, body: str) -> WhatsAppMessageResult | None: ...
