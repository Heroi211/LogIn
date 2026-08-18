# LogIn API

Backend de **Identity & Access** (usuários, papéis, autenticação JWT, RBAC e auditoria).  
Arquitetura: **Clean Architecture + DDD estratégico** (bounded context `identity_access`).

Documentação detalhada de arquitetura: [`docs/architecture/`](docs/architecture/README.md).

---

## Início rápido (5 minutos)

```bash
cp .env-sample .env          # ajuste APP_BRAND_NAME, DATABASE_*, SECRET
make install
make dev                     # Docker: API + PostgreSQL + pgAdmin
make health                  # verifica API + banco
```

O banco é criado e populado por **`init_db/database.sql`**, montado no PostgreSQL via Docker (`docker-compose.yaml` → `/docker-entrypoint-initdb.d/`).  
Isso roda **apenas no primeiro start** do volume. Para reaplicar do zero: `make docker-fresh`.

**Admin inicial** (definido em `init_db/database.sql`):

| Campo | Valor padrão |
|-------|----------------|
| CPF | `00000000000` |
| Senha | `Admin@123456` |
| E-mail | `admin@example.com` |

API local sem Docker (PostgreSQL já existente):

```bash
make run                     # http://localhost:8000/docs
```

Nesse caso, aplique `init_db/database.sql` manualmente no seu banco ou use `make docker-fresh`.

### Health

| Rota | Uso |
|------|-----|
| `GET /health` | Liveness (API viva) |
| `GET /health/ready` | Readiness (API + PostgreSQL) |
| `GET /metrics` | Métricas básicas (Prometheus-style) |

### Perfis (`APP_ENV`)

| Perfil | Uso |
|--------|-----|
| `development` | Local, debug opcional |
| `staging` | Pré-produção |
| `production` | Secrets fortes, SMTP configurado |

---

## Funcionalidades atuais

### Autenticação

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| POST | `/v1/users/signup` | Pública | Cadastro de usuário |
| POST | `/v1/users/login` | Pública | Login → access + refresh token |
| GET | `/v1/users/logged` | JWT | Usuário autenticado |
| GET | `/v1/users/me/permissions` | JWT | Permissões do usuário (telas/menus) |
| POST | `/v1/users/refresh` | Pública | Renova tokens |
| POST | `/v1/users/forgot-password/{email}` | Pública | Solicita reset por e-mail (máx. 3× / 30 dias) |
| POST | `/v1/users/reset-password` | Pública | Redefine senha com token |

**Segurança (Fase B):** bloqueio após 3 logins falhos, rate limit em login/signup/forgot, token de reset hasheado no banco, CORS configurável. Detalhes: [`docs/SECURITY.md`](docs/SECURITY.md).

### Usuários (RBAC)

| Método | Rota | Permissão | Quem acessa hoje |
|--------|------|-----------|------------------|
| GET | `/v1/users/` | `users:read` | Operator, Administrator |
| GET | `/v1/users/{id}` | `users:read` | Operator, Administrator |
| PUT | `/v1/users/{id}` | `users:update` | Administrator |
| DELETE | `/v1/users/{id}` | `users:delete` | Administrator |
| POST | `/v1/users/{id}/block` | `users:block` | Administrator |
| POST | `/v1/users/{id}/unblock` | `users:unblock` | Administrator |

### Permissões e RBAC dinâmico

| Método | Rota | Permissão | Descrição |
|--------|------|-----------|-----------|
| GET | `/v1/permissions/` | `permissions:read` | Catálogo de permissões |
| POST | `/v1/permissions/` | `permissions:create` | Cadastrar nova permissão (tela/função) |
| PUT | `/v1/roles/{id}/permissions` | `roles:update` | Associar permissões ao papel |

Matriz **papel → permissão** no PostgreSQL (`permissions` + `role_permissions`).  
Guia completo: [`docs/RBAC.md`](docs/RBAC.md).

### Papéis (RBAC)

| Método | Rota | Permissão | Quem acessa hoje |
|--------|------|-----------|------------------|
| POST | `/v1/roles/` | `roles:create` | Administrator |
| GET | `/v1/roles/` | `roles:read` | Administrator |
| GET | `/v1/roles/{id}` | `roles:read` | Administrator |
| PUT | `/v1/roles/{id}` | `roles:update` | Administrator |
| DELETE | `/v1/roles/{id}` | `roles:delete` | Administrator |

### Papéis de usuário

| ID | Papel | Permissões hoje |
|----|-------|-----------------|
| 1 | User | — |
| 2 | Operator | `users:read` |
| 3 | Administrator | bypass total + todas no DB |
| 4 | User_client | — |

Permissões por papel: `GET /v1/roles/{id}` → campo `permissions`.

---

## Fluxo do sistema

### Requisição HTTP típica (rota protegida)

```
Cliente HTTP
    │
    ▼
main.py → bootstrap/app.py          # FastAPI, CORS, middlewares
    │
    ▼
presentation/api/v1/endpoints/        # Controller fino
    │   require_permission(...)       # RBAC (infrastructure/security)
    │   Depends(get_*_use_case)       # DI (bootstrap/deps.py)
    ▼
application/use_cases/                # Orquestração + auditoria
    │
    ▼
domain/entities/                      # Regras de negócio (User, Role)
    │
    ▼
infrastructure/persistence/           # SQLAlchemy repositories
    │
    ▼
PostgreSQL
```

### Login

```
POST /v1/users/login (CPF + senha)
    → AuthenticateUser (use case)
        → UserRepository.get_by_cpf
        → User.verify_password + User.ensure_can_authenticate
        → AuditLogger (success/failure)
    → TokenService.create_access_token
    ← { access_token, token_type }
```

### Autorização (RBAC)

1. JWT validado em `infrastructure/security/deps.py` → `get_current_user`
2. `require_permission(Permission.XXX)` consulta `domain/rbac.py`
3. **Administrator sempre passa** (bypass no domínio)
4. Demais papéis: matriz `ROLE_PERMISSIONS` em `domain/permission.py`

---

## Estrutura do projeto

```
LogIn/
├── main.py                           # Entrypoint → bootstrap/app.create_app()
├── bootstrap/                        # Composition root (app, DI, sessão DB)
├── contexts/
│   ├── identity_access/              # Bounded context ativo
│   │   ├── domain/                   # Entidades, VOs, Permission, RBAC
│   │   ├── application/              # Use cases, ports, DTOs
│   │   ├── infrastructure/           # ORM, JWT, SMTP, audit, RBAC HTTP
│   │   └── presentation/             # Endpoints FastAPI + schemas Pydantic
│   └── ticket_management/            # Placeholder (futuro)
├── core/                             # Config, logging, bcrypt (cross-cutting)
├── shared/                           # Utilitários sem regra de negócio
├── docs/architecture/                # Documentação arquitetural
├── init_db/                          # SQL: schema + dados iniciais (Docker init)
├── Makefile
└── docker-compose.yaml
```

---

## Guia: próximas implementações

### Nova rota / endpoint

1. **Schema** (entrada/saída HTTP):  
   `contexts/identity_access/presentation/schemas/`

2. **Use case** (fluxo de negócio):  
   `contexts/identity_access/application/use_cases/<recurso>/`

3. **Registrar DI** em `bootstrap/deps.py`:
   ```python
   def get_meu_use_case(...) -> MeuUseCase:
       return MeuUseCase(repo, audit)
   ```

4. **Endpoint fino** em `presentation/api/v1/endpoints/`:
   ```python
   @router.post("/recurso")
   async def criar(
       request: Request,
       payload: meu_schema,
       use_case: Annotated[MeuUseCase, Depends(get_meu_use_case)],
       _: Annotated[User, Depends(require_permission(Permission.XXX))],
   ):
       audit_ctx = audit_context_from_request(request, actor_user_id=...)
       result = await use_case.execute(..., audit_ctx)
       return mapper_to_response(result)
   ```

5. **Registrar router** em `presentation/api/v1/api.py` se for módulo novo.

---

### Aplicar permissão por papel

**Rotas novas declaram o que precisam** — não listam papéis:

```python
from contexts.identity_access.domain.permission import Permission
from contexts.identity_access.infrastructure.security.authorization import require_permission

@router.get("/")
async def listar(_: Annotated[User, Depends(require_permission(Permission.USERS_READ))]):
    ...
```

**Quem pode fica na matriz** (`domain/permission.py`):

```python
ROLE_PERMISSIONS = {
    RoleType.OPERATOR: frozenset({
        Permission.USERS_READ,
        Permission.USERS_CREATE,  # ← adicionar aqui para liberar Operator
    }),
    ...
}
```

Se precisar de permissão nova:

1. Adicionar constante em `class Permission`
2. Incluir em `ALL_PERMISSIONS`
3. Atribuir em `ROLE_PERMISSIONS`
4. Usar `require_permission(Permission.NOVA)` na rota

---

### Registrar log de auditoria

Auditoria de negócio/segurança vai nos **use cases**, não nos endpoints.

1. Injetar `AuditLogger` no use case (via `bootstrap/deps.py` → `get_audit_logger`)
2. Usar helper `application/use_cases/_audit.py`:

```python
from contexts.identity_access.domain.audit.actions import AuditAction
from contexts.identity_access.application.use_cases._audit import record_audit

await record_audit(
    self._audit,
    audit_ctx,
    action=AuditAction.USER_CREATED,
    outcome="success",
    resource_type="user",
    resource_id=user.id.value,
)
```

3. No endpoint, passar contexto HTTP:

```python
from contexts.identity_access.infrastructure.http.audit_context import audit_context_from_request

audit_ctx = audit_context_from_request(request, actor_user_id=actor.id.value)
await use_case.execute(..., audit_ctx)
```

**Log HTTP** (access log): automático via middleware em `core/middleware/request_record.py`.  
Configure `LOG_HTTP_REQUESTS` e `LOG_HTTP_REQUESTS_FILE` no `.env`.

---

### Aplicar DDD / Clean Architecture

| O quê | Onde colocar |
|-------|--------------|
| Regra de negócio | `domain/entities/`, `domain/value_objects/` |
| Orquestração de fluxo | `application/use_cases/` |
| Interface de persistência | `application/ports/` |
| SQLAlchemy, SMTP, JWT | `infrastructure/` |
| HTTP, Pydantic | `presentation/` |
| Wiring / DI | `bootstrap/deps.py` |

**Regra de dependência:** camadas externas dependem das internas. `domain/` **não** importa FastAPI, SQLAlchemy ou Pydantic.

**Novo agregado (ex.: Ticket):** criar bounded context em `contexts/ticket_management/` — não importar ORM de users; usar `UserId` de `domain/public_api.py`.

---

### Novo repositório

1. Port em `application/ports/meu_repository.py` (Protocol)
2. Implementação em `infrastructure/persistence/repositories/`
3. Mapper ORM ↔ domínio em `infrastructure/persistence/mappers.py`
4. Factory em `bootstrap/deps.py`

---

### Nova invariante de domínio

Adicionar método na entidade (`domain/entities/user.py`) e chamar no use case:

```python
# domain
def ensure_can_authenticate(self) -> None:
    if not self.active:
        raise UserInactiveError("Usuário inativo.")

# use case
user.verify_password(senha, self._hasher.verify)
```

---

## Variáveis de ambiente

Copie `.env-sample` para `.env`. Principais:

| Variável | Uso |
|----------|-----|
| `SECRET` | JWT + app |
| `DATABASE_*` | PostgreSQL |
| `SMTP_*` | E-mail de reset de senha |
| `FRONTEND_URL` | Link no e-mail de reset |
| `CORS_ORIGINS` | Origens permitidas (vírgula ou `*`) |
| `LOGIN_MAX_FAILED_ATTEMPTS` | Bloqueio após N logins falhos (padrão: 3) |
| `PASSWORD_RESET_MAX_REQUESTS` | Máx. resets por janela (padrão: 3) |
| `PASSWORD_RESET_WINDOW_DAYS` | Janela em dias (padrão: 30) |
| `PASSWORD_MIN_LENGTH` | Tamanho mínimo da senha (padrão: 8) |
| `RATE_LIMIT_*_PER_MINUTE` | Rate limit por IP (login, signup, forgot) |
| `LOG_HTTP_REQUESTS` | Access log no console |
| `LOG_HTTP_REQUESTS_FILE` | Gravar JSONL (`logs/api_requests/`) |

---

## Próximos passos (quando retomar)

| Fase | Foco |
|------|------|
| **A–B** | ✅ Fundação + segurança |
| **RBAC dinâmico** | ✅ Permissões no DB + API de gestão |
| **C** | ✅ Observabilidade (correlation ID, metrics, JSON logs, shutdown) |
| **D** | ✅ Template BC + `new_context.py` + `make check-arch` |
| **E** | ✅ Signup configurável + refresh token + [`docs/RBAC.md`](docs/RBAC.md) |
| **F** | Testes automatizados + CI |
| **G** | Empacotamento template GitHub |
| **H** | Integrações plug-and-play |

---

## Referências

- [Arquitetura geral](docs/architecture/README.md)
- [Identity & Access (contexto)](docs/architecture/identity_access/README.md)
- [API pública entre contextos](docs/architecture/identity_access/public_api.md)
- [Context map](docs/architecture/identity_access/context_map.md)
- [Regras de ouro (checklist)](docs/architecture/golden_rules.md)
