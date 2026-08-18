from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RoleRecord:
    id: int
    description: str
    active: bool
    permissions: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class CreateRoleInput:
    description: str
    active: bool
    permissions: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class UpdateRoleInput:
    description: str | None = None
    active: bool | None = None


@dataclass(frozen=True, slots=True)
class SetRolePermissionsInput:
    permissions: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PermissionRecord:
    id: int
    code: str
    description: str
    module: str | None
    active: bool


@dataclass(frozen=True, slots=True)
class CreatePermissionInput:
    code: str
    description: str
    module: str | None = None
