"""Códigos de permissão usados nas rotas (contrato estável).

A matriz papel→permissão vive no banco (`permissions` + `role_permissions`).
Novas telas/funções: cadastre o código via API e associe ao papel — sem redeploy de RBAC.
"""

from contexts.identity_access.domain.role_type import RoleType


class Permission:
    USERS_READ = "users:read"
    USERS_CREATE = "users:create"
    USERS_UPDATE = "users:update"
    USERS_DELETE = "users:delete"
    USERS_BLOCK = "users:block"
    USERS_UNBLOCK = "users:unblock"

    ROLES_READ = "roles:read"
    ROLES_CREATE = "roles:create"
    ROLES_UPDATE = "roles:update"
    ROLES_DELETE = "roles:delete"

    PERMISSIONS_READ = "permissions:read"
    PERMISSIONS_CREATE = "permissions:create"


# Permissões conhecidas pelo código (referência / bootstrap). O catálogo real está no DB.
BUILTIN_PERMISSION_CODES: frozenset[str] = frozenset(
    {
        Permission.USERS_READ,
        Permission.USERS_CREATE,
        Permission.USERS_UPDATE,
        Permission.USERS_DELETE,
        Permission.USERS_BLOCK,
        Permission.USERS_UNBLOCK,
        Permission.ROLES_READ,
        Permission.ROLES_CREATE,
        Permission.ROLES_UPDATE,
        Permission.ROLES_DELETE,
        Permission.PERMISSIONS_READ,
        Permission.PERMISSIONS_CREATE,
    }
)

# Alias legado — preferir consulta ao banco via AuthorizationService.
ALL_PERMISSIONS = BUILTIN_PERMISSION_CODES

# Removido: ROLE_PERMISSIONS — use role_permissions no PostgreSQL.
