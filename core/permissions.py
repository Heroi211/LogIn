"""
Controle de acesso por permissões (RBAC).

Como funciona
-----------
1. Rotas declaram *o que precisam* → ``require_permission(Permission.USERS_READ)``
2. Quem pode fazer fica em ``ROLE_PERMISSIONS`` (matriz central)
3. Administrator (id=3) pode **tudo**, sempre

Para dar cadastro de usuários ao Operator no futuro, basta adicionar
``Permission.USERS_CREATE`` em ``ROLE_PERMISSIONS[Roles.OPERATOR]``.
Nenhuma rota precisa mudar.

Para um novo papel (ex.: USER_CLIENT), adicione uma entrada em
``ROLE_PERMISSIONS`` com as permissões desejadas. Rotas intactas.

Uso em rota:

    from core.permissions import Permission, require_permission

    @router.get("/")
    async def list_users(_: Users = Depends(require_permission(Permission.USERS_READ))):
        ...
"""

from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, HTTPException, status

from core.deps import get_current_user
from models.roles import Roles
from models.users import Users

_FORBIDDEN = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Você não possui permissão para acessar este recurso.",
)


class Permission:
    """Permissões nomeadas do backend (recurso:ação)."""

    USERS_READ = "users:read"
    USERS_CREATE = "users:create"
    USERS_UPDATE = "users:update"
    USERS_DELETE = "users:delete"

    ROLES_READ = "roles:read"
    ROLES_CREATE = "roles:create"
    ROLES_UPDATE = "roles:update"
    ROLES_DELETE = "roles:delete"


ALL_PERMISSIONS: frozenset[str] = frozenset(
    {
        Permission.USERS_READ,
        Permission.USERS_CREATE,
        Permission.USERS_UPDATE,
        Permission.USERS_DELETE,
        Permission.ROLES_READ,
        Permission.ROLES_CREATE,
        Permission.ROLES_UPDATE,
        Permission.ROLES_DELETE,
    }
)


# Único lugar para evoluir papéis — rotas não listam role_id.
ROLE_PERMISSIONS: dict[int, frozenset[str]] = {
    Roles.USER: frozenset(),
    Roles.OPERATOR: frozenset(
        {
            Permission.USERS_READ,
        }
    ),
    Roles.ADMINISTRATOR: frozenset(ALL_PERMISSIONS),
    Roles.USER_CLIENT: frozenset(),
}


def permissions_for_role(role_id: int | None) -> frozenset[str]:
    """Permissões efetivas do papel."""
    if role_id == Roles.ADMINISTRATOR:
        return ALL_PERMISSIONS
    return ROLE_PERMISSIONS.get(role_id, frozenset())


def role_has_permission(role_id: int | None, permission: str) -> bool:
    if role_id == Roles.ADMINISTRATOR:
        return True
    return permission in ROLE_PERMISSIONS.get(role_id, frozenset())


def user_has_permission(user: Users, permission: str) -> bool:
    return role_has_permission(user.role_id, permission)


def user_has_any_permission(user: Users, *permissions: str) -> bool:
    if user.role_id == Roles.ADMINISTRATOR:
        return True
    role_perms = ROLE_PERMISSIONS.get(user.role_id, frozenset())
    return any(permission in role_perms for permission in permissions)


def require_permission(*permissions: str) -> Callable:
    """
    Dependency factory global: exige autenticação e ao menos uma permissão (OR).

    Administrator sempre autorizado.
    """
    if not permissions:
        raise ValueError("require_permission exige ao menos uma permissão")

    unknown = set(permissions) - ALL_PERMISSIONS
    if unknown:
        raise ValueError(f"Permissões desconhecidas: {sorted(unknown)}")

    async def _checker(user: Users = Depends(get_current_user)) -> Users:
        if user_has_any_permission(user, *permissions):
            return user
        raise _FORBIDDEN

    return _checker


def require_administrator() -> Callable:
    """Somente Administrator — evite em rotas novas; prefira ``require_permission``."""

    async def _checker(user: Users = Depends(get_current_user)) -> Users:
        if user.role_id != Roles.ADMINISTRATOR:
            raise _FORBIDDEN
        return user

    return _checker


# Compatibilidade com código antigo (evite em rotas novas).
require_role = require_administrator
require_admin = require_administrator()
require_operator = require_permission(Permission.USERS_READ)
