from __future__ import annotations

from typing import Protocol

from contexts.identity_access.domain.role_type import RoleType


class HasRoleId(Protocol):
    role_id: int | None


def role_has_any_permission(
    role_id: int | None,
    role_permissions: frozenset[str],
    *permissions: str,
) -> bool:
    """Checagem pura dado um conjunto de permissões já resolvido."""
    if role_id == RoleType.ADMINISTRATOR:
        return True
    return any(permission in role_permissions for permission in permissions)


def user_has_any_permission(
    user: HasRoleId,
    role_permissions: frozenset[str],
    *permissions: str,
) -> bool:
    return role_has_any_permission(user.role_id, role_permissions, *permissions)
