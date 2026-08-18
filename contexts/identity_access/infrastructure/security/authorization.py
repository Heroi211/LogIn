"""
Adapter FastAPI para RBAC dinâmico (PostgreSQL).

Rotas declaram ``require_permission(Permission.USERS_READ)``.
Quem pode fica em ``permissions`` + ``role_permissions`` no banco.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status

from bootstrap.deps import get_authorization_service
from contexts.identity_access.application.ports.authorization_service import AuthorizationService
from contexts.identity_access.domain.entities.user import User
from contexts.identity_access.domain.permission import Permission
from contexts.identity_access.infrastructure.security.deps import get_current_user
from contexts.identity_access.infrastructure.security.oauth import oauth2_scheme

_FORBIDDEN = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Você não possui permissão para acessar este recurso.",
)


def require_permission(*permissions: str) -> Callable:
    if not permissions:
        raise ValueError("require_permission exige ao menos uma permissão")

    async def _checker(
        user: Annotated[User, Depends(get_current_user)],
        authz: Annotated[AuthorizationService, Depends(get_authorization_service)],
    ) -> User:
        if await authz.user_has_any_permission(user.role_id, *permissions):
            return user
        raise _FORBIDDEN

    return _checker


def require_administrator() -> Callable:
    from contexts.identity_access.domain.role_type import RoleType

    async def _checker(user: User = Depends(get_current_user)) -> User:
        if user.role_id != RoleType.ADMINISTRATOR:
            raise _FORBIDDEN
        return user

    return _checker


require_role = require_administrator
require_admin = require_administrator()
require_operator = require_permission(Permission.USERS_READ)

__all__ = [
    "Permission",
    "oauth2_scheme",
    "require_admin",
    "require_administrator",
    "require_operator",
    "require_permission",
    "require_role",
]
