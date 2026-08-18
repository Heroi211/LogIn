# API pública — Identity & Access

Outros bounded contexts (ex.: **Ticket Management**) devem consumir **apenas** estes contratos.

## Import permitido

```python
from contexts.identity_access.domain.public_api import (
    UserId,
    RoleType,
    Permission,
    AuditAction,
    role_has_permission,
    user_has_permission,
)
```

## Import proibido (de outros contextos)

```python
# ❌ Nunca faça isso a partir de Ticket Management
from models.users import Users
from contexts.identity_access.infrastructure.persistence.models.users import Users
from contexts.identity_access.infrastructure.persistence.repositories.user_repository import ...
```

## Tipos expostos

### `UserId`

Identificador opaco de usuário na fronteira entre contextos.

```python
user_id = UserId(42)
int(user_id)  # 42
```

### `RoleType`

Enum de papéis (`USER`, `OPERATOR`, `ADMINISTRATOR`, `USER_CLIENT`).

### `Permission`

Strings de capacidade (`users:read`, `roles:create`, …). Matriz em `domain/permission.py`.

### Funções de política

```python
role_has_permission(RoleType.OPERATOR, Permission.USERS_READ)  # True
user_has_permission(actor, Permission.USERS_DELETE)            # depende do role_id
```

## Integração futura com Ticket Management

| Necessidade | Como consumir |
|---|---|
| Saber quem é o usuário | `UserId` no token/sessão |
| Verificar permissão | Port `AuthorizationService` (Fase 7) ou API interna |
| Dados completos do perfil | API read-only `/v1/users/{id}` (HTTP) — não importar ORM |

## Anti-Corruption Layer (ACL)

A borda HTTP (`presentation/schemas/`) traduz Pydantic ↔ DTOs ↔ entidades de domínio.
Schemas **nunca** são usados dentro de `domain/` ou `application/`.

## Evolução

Quando Ticket Management entrar, criar port:

```python
class AuthorizationService(Protocol):
    async def user_can(self, user_id: UserId, permission: str) -> bool: ...
```

Implementação delega para `domain/rbac.py`.
