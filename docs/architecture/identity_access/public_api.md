# API pública — Identity & Access

Outros bounded contexts (ex.: **Ticket Management**) devem consumir **apenas** estes contratos.

## Import permitido (domínio)

```python
from contexts.identity_access.domain.public_api import (
    UserId,
    RoleType,
    Permission,
    AuditAction,
)
```

## Import permitido (autorização entre contextos)

```python
from contexts.identity_access.application.ports.authorization_service import AuthorizationService
```

Injetado via `bootstrap/deps.py` → `get_authorization_service`.

## Import proibido (de outros contextos)

```python
# ❌ Nunca faça isso a partir de outro bounded context
from contexts.identity_access.infrastructure.persistence.models.users import Users
from contexts.identity_access.infrastructure.persistence.repositories.user_repository import ...
```

## Tipos expostos

### `UserId`

Identificador opaco de usuário na fronteira entre contextos.

### `RoleType`

Enum de papéis seed (`USER`, `OPERATOR`, `ADMINISTRATOR`, `USER_CLIENT`). Papéis adicionais existem no banco com IDs > 4.

### `Permission`

Constantes de referência (`users:read`, `roles:create`, …). O catálogo real e a matriz papel→permissão estão no PostgreSQL — ver [`../../RBAC.md`](../../RBAC.md).

## Integração com outros contextos

| Necessidade | Como consumir |
|---|---|
| Saber quem é o usuário | `UserId` no token/sessão |
| Verificar permissão | Port `AuthorizationService` |
| Listar permissões do usuário | HTTP `GET /v1/users/me/permissions` |
| Dados completos do perfil | HTTP `GET /v1/users/{id}` — não importar ORM |

## Catálogo e RBAC

- Catálogo implementado: [`../../FUNCTIONALITY_CATALOG.md`](../../FUNCTIONALITY_CATALOG.md)
- Manual RBAC: [`../../RBAC.md`](../../RBAC.md)
