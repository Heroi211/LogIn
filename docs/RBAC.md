# RBAC — manual do desenvolvedor

Como funciona o permissionamento implementado e como estender o sistema.

---

## Modelo de dados

```
users.role_id  →  roles  ←→  role_permissions  ←→  permissions
```

| Tabela | Função |
|--------|--------|
| `permissions` | Catálogo de funcionalidades (`code`, `description`, `module`) |
| `role_permissions` | Quais permissões cada papel possui |
| `roles` | Papéis (grupos de acesso) |
| `users.role_id` | Papel do usuário (herda permissões do papel) |

**Não há permissão direta por usuário** — sempre via papel.

---

## Duas camadas de proteção

| Camada | Onde | Responsabilidade |
|--------|------|------------------|
| HTTP | `require_permission(...)` na rota | Porta de entrada da API |
| Application | Use case + `AuthorizationService` | Regra quando há múltiplos entrypoints |

**Repositório não valida permissão** — apenas persiste dados.

Fluxo recomendado:

```
Rota / job / handler
    → Use case (recebe actor_role_id)
        → AuthorizationService.user_has_any_permission(...)
        → Domínio + Repository
```

Chamar `Repository.save()` direto **sem** passar pelo use case autorizado contorna o RBAC.

---

## Como o backend decide acesso

1. JWT → `get_current_user` → `user.role_id`
2. Rota chama `require_permission("modulo:acao")`
3. `DbAuthorizationService` consulta `role_permissions` no PostgreSQL (cache TTL configurável)
4. **Administrator (role_id=3):** bypass — passa em qualquer `require_permission`
5. Demais papéis: precisam ter o `code` associado no banco

Arquivos centrais:

| Arquivo | Papel |
|---------|-------|
| `infrastructure/security/authorization.py` | `require_permission` (FastAPI) |
| `infrastructure/security/db_authorization_service.py` | Consulta banco + cache |
| `infrastructure/persistence/repositories/permission_repository.py` | SQL de permissões |
| `domain/permission.py` | Constantes `Permission.*` (referência no código) |

---

## Fluxo: implementar nova funcionalidade

### 1. Definir permissões (catálogo)

Uma permissão por **ação de negócio**, não por tela inteira.

Exemplo módulo `products`:

| Code | Ação |
|------|------|
| `products:read` | GET list/detail |
| `products:create` | POST |
| `products:update` | PUT / PATCH / auto-save |
| `products:delete` | DELETE |

Registrar no banco (admin):

```http
POST /v1/permissions
{"code": "products:read", "description": "Listar produtos", "module": "products"}
```

Ou incluir no `init_db/database.sql` para novos ambientes.

Atualizar [`FUNCTIONALITY_CATALOG.md`](FUNCTIONALITY_CATALOG.md).

### 2. Implementar use case

```python
class UpdateProduct:
    def __init__(self, repo, authz: AuthorizationService):
        self._repo = repo
        self._authz = authz

    async def execute(self, product_id: int, data, *, actor_role_id: int | None):
        if not await self._authz.user_has_any_permission(actor_role_id, "products:update"):
            raise ForbiddenError(...)
        ...
```

Vários entrypoints (PUT, PATCH, evento interno) devem chamar **o mesmo use case**.

### 3. Proteger rotas

```python
@router.put("/products/{id}")
async def update_product(
    actor: Annotated[User, Depends(require_permission("products:update"))],
    use_case: Annotated[UpdateProduct, Depends(get_update_product)],
):
    return await use_case.execute(..., actor_role_id=actor.role_id)
```

### 4. Associar permissões aos papéis (operacional)

```http
PUT /v1/roles/2/permissions
{"permissions": ["users:read", "products:read", "products:update"]}
```

**Atenção:** este endpoint **substitui a lista inteira** do papel. Inclua permissões já existentes que o papel deve manter.

### 5. Frontend

```http
GET /v1/users/me/permissions
→ {"permissions": ["users:read", "products:read"]}
```

Use para menus e botões. O backend **sempre** revalida.

---

## Fluxo: criar novo papel

```http
POST /v1/roles
{"description": "Gerente", "active": true}
→ id: 5

GET /v1/permissions
→ listar todos os codes

PUT /v1/roles/5/permissions
{"permissions": ["users:read", "products:read", ...]}
```

Para acesso amplo: incluir todos os codes retornados por `GET /v1/permissions`.  
Papel com bypass total igual ao Admin: hoje apenas **role_id=3** (hardcoded).

---

## Constantes no código vs banco

| Onde | O quê |
|------|-------|
| Código (`Permission.USERS_READ` ou string) | Contrato estável usado em rotas/use cases |
| Banco (`permissions.id` + `code`) | Catálogo e associação com papéis |

Use **code legível** no código (`products:read`), não ID numérico.

---

## Cache

Permissões por papel são cacheadas em memória (`PERMISSION_CACHE_TTL_SECONDS`, padrão 60s).  
Invalidado automaticamente em `SetRolePermissions`.

---

## Signup e tokens

| Recurso | Detalhe |
|---------|---------|
| `SIGNUP_PUBLIC=true` | Cadastro aberto |
| `SIGNUP_PUBLIC=false` | Exige JWT com `users:create` |
| Login | Retorna `access_token` + `refresh_token` |
| Refresh | `POST /v1/users/refresh?refresh_token=...` |

---

## Port para outros bounded contexts

```python
from contexts.identity_access.application.ports.authorization_service import AuthorizationService
```

Injetado via `bootstrap/deps.py` → `get_authorization_service`.

---

## Auditoria

| Evento | Quando |
|--------|--------|
| `permission.created` | Nova permissão no catálogo |
| `role.permissions.updated` | Permissões de um papel alteradas |
| `authz.denied` | (reservado) |

---

## Referências

- Catálogo completo: [`FUNCTIONALITY_CATALOG.md`](FUNCTIONALITY_CATALOG.md)
- Segurança operacional: [`SECURITY.md`](SECURITY.md)
- Troubleshooting: [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md)
