from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class UserEntity:
    id: int | None
    name: str
    email: str
    phone: str
    role_id: int
    active: bool
    auth_provider: str = "local"
    cpf: str | None = None
    password_hash: str | None = None
    google_id: str | None = None
    failed_login_attempts: int = 0
    reset_password_token: str | None = None
    reset_password_expires: datetime | None = None
    created_at: datetime | None = None


@dataclass
class RoleEntity:
    id: int | None
    description: str
    active: bool
    created_at: datetime | None = None


@dataclass
class SessionEntity:
    id: int | None
    user_id: int
    token_hash: str
    expires_at: datetime
    active: bool
    ip_address: str | None = None
    user_agent: str | None = None
    created_at: datetime | None = None


@dataclass
class RevokedTokenEntity:
    id: int | None
    jti: str
    token_type: str
    user_id: int | None
    expires_at: datetime
    created_at: datetime | None = None


@dataclass
class ApiKeyEntity:
    id: int | None
    key_prefix: str
    key_hash: str
    name: str
    user_id: int
    scopes: str
    active: bool
    expires_at: datetime | None = None
    created_at: datetime | None = None
