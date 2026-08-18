from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class UserRecord:
    id: int
    name: str
    email: str
    cpf: str
    phone: str
    active: bool
    blocked: bool
    role_id: int
    password_hash: str
    reset_password_token: str | None = None
    reset_password_expires: datetime | None = None


@dataclass(frozen=True, slots=True)
class UserListItem:
    id: int
    name: str
    email: str
    cpf: str
    phone: str
    active: bool
    blocked: bool
    role: str | None


@dataclass(frozen=True, slots=True)
class RegisterUserInput:
    name: str
    email: str
    cpf: str
    phone: str
    password: str


@dataclass(frozen=True, slots=True)
class UpdateUserInput:
    name: str | None = None
    email: str | None = None
    cpf: str | None = None
    phone: str | None = None
    active: bool | None = None
