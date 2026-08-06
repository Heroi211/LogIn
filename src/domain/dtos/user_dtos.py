"""DTOs de domínio — sem dependência de Pydantic HTTP."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class UserCreateDTO:
    name: str
    email: str
    cpf: str
    phone: str
    role_id: int = 1


@dataclass
class RoleCreateDTO:
    description: str
    active: bool = True


@dataclass
class RoleUpdateDTO:
    description: str | None = None
    active: bool | None = None
