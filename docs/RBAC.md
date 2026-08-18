# RBAC dinâmico

Permissões e a matriz **papel → permissão** vivem no PostgreSQL. Rotas continuam declarando o que exigem; quem pode é configurado sem redeploy.

## Modelo

```
permissions          role_permissions          roles
─────────────        ─────────────────         ─────
id                   role_id (FK)              id
code (users:read)    permission_id (FK)        description
description          PK(role_id, perm_id)     active
module (opcional)
active
```

## Fluxo para nova tela/função

1. **Cadastrar permissão** (admin):
   ```http
   POST /v1/permissions
   Authorization: Bearer <admin>
   {"code": "tickets:read", "description": "Ver tickets", "module": "tickets"}
   ```

2. **Proteger rota no backend** (uma vez, ao criar o endpoint):
   ```python
   @router.get("/tickets")
   async def list_tickets(_: User = Depends(require_permission("tickets:read"))):
       ...
   ```

3. **Associar ao papel** (admin, sem deploy):
   ```http
   PUT /v1/roles/2/permissions
   {"permissions": ["users:read", "tickets:read"]}
   ```

4. **Frontend** consulta permissões do usuário logado:
   ```http
   GET /v1/users/me/permissions
   → {"permissions": ["users:read", "tickets:read"]}
   ```

Cache in-process (TTL: `PERMISSION_CACHE_TTL_SECONDS`) é invalidado ao alterar permissões de um papel.

## Papéis de sistema

| ID | Papel | Comportamento |
|----|-------|---------------|
| 3 | Administrador | Bypass total em `require_permission` |
| 1, 2, 4+ | Demais | Permissões vindas do banco |

Papéis criados via `POST /v1/roles` começam **sem permissões** até o admin associar via `PUT /v1/roles/{id}/permissions`.

## Signup público vs protegido

| `SIGNUP_PUBLIC` | Comportamento |
|-----------------|---------------|
| `true` (padrão) | Qualquer um usa `POST /v1/users/signup` |
| `false` | Exige JWT com permissão `users:create` |

## Refresh token

Login retorna `access_token` + `refresh_token`. Renovar:

```http
POST /v1/users/refresh?refresh_token=<token>
```

## Port para outros bounded contexts

Outros contextos verificam permissão via port (Fase D):

```python
from contexts.identity_access.application.ports.authorization_service import AuthorizationService
```

Injetado pelo composition root (`bootstrap/deps.py` → `get_authorization_service`).

## Auditoria

| Evento | Quando |
|--------|--------|
| `permission.created` | Nova permissão cadastrada |
| `role.permissions.updated` | Permissões de um papel alteradas |
