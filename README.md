# LogIn API

Backend **Identity & Access** — usuários, papéis, JWT, RBAC dinâmico e auditoria.  
Arquitetura: Clean Architecture + DDD (`contexts/identity_access`).

---

## Sumário — onde está cada informação

Use este mapa para se contextualizar **antes de implementar qualquer coisa**.  
Leia na ordem indicada conforme o tipo de tarefa.

### Documentação (leia primeiro)

| Arquivo | Conteúdo | Quando consultar |
|---------|----------|----------------|
| **[`docs/FUNCTIONALITY_CATALOG.md`](docs/FUNCTIONALITY_CATALOG.md)** | Catálogo oficial: rotas, permissões, use cases, papéis seed, checklist de entrega | Saber **o que já existe**; atualizar ao entregar feature |
| **[`docs/RBAC.md`](docs/RBAC.md)** | RBAC dinâmico: modelo DB, fluxo dev/ops, use case vs rota, cache, signup, refresh | **Permissionar** ou associar papéis |
| **[`docs/SECURITY.md`](docs/SECURITY.md)** | Bloqueio, rate limit, CORS, reset de senha, checklist produção | Segurança e hardening |
| **[`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md)** | Diagnóstico: login, 403, banco, correlation ID | Problemas em runtime |
| **[`docs/architecture/golden_rules.md`](docs/architecture/golden_rules.md)** | Checklist de camadas — o que pode/não pode em domain, application, etc. | **Code review** e conformidade |
| **[`docs/architecture/README.md`](docs/architecture/README.md)** | Visão geral Clean Architecture + bounded contexts | Entender estrutura macro |
| **[`docs/architecture/identity_access/public_api.md`](docs/architecture/identity_access/public_api.md)** | Contratos entre bounded contexts (`UserId`, `AuthorizationService`) | Integrar **outro módulo** com Identity |
| **[`docs/README.md`](docs/README.md)** | Índice da pasta `docs/` | Navegação |
| **[`init_db/README.md`](init_db/README.md)** | Como o SQL é aplicado (Docker init, reset) | Banco / seed |
| **[`.env-sample`](.env-sample)** | Variáveis de ambiente comentadas | Config local/staging/prod |
| **[`AGENT_IMPLEMENTATION_PROMPT.md`](AGENT_IMPLEMENTATION_PROMPT.md)** | Prompt copy-paste para agentes de IA + fluxos obrigatórios | **Início de toda implementação via agente** |

### Código — onde implementar (não inventar outro lugar)

| Caminho | Responsabilidade | Exemplos no projeto |
|---------|------------------|---------------------|
| `contexts/identity_access/domain/` | Entidades, VOs, regras puras, `Permission`, exceções | `entities/user.py`, `permission.py` |
| `contexts/identity_access/application/use_cases/` | Orquestração, auditoria, **autorização quando múltiplos entrypoints** | `users/authenticate_user.py` |
| `contexts/identity_access/application/ports/` | Interfaces (Protocol) | `authorization_service.py`, `user_repository.py` |
| `contexts/identity_access/infrastructure/persistence/` | ORM, repositórios, mappers | `repositories/`, `models/` |
| `contexts/identity_access/infrastructure/security/` | JWT, RBAC HTTP, rate limit | `authorization.py`, `db_authorization_service.py` |
| `contexts/identity_access/presentation/api/v1/endpoints/` | Rotas finas + `require_permission` | `users.py`, `roles.py`, `permissions.py` |
| `contexts/identity_access/presentation/schemas/` | Pydantic (entrada/saída HTTP) | `users_schemas.py` |
| `bootstrap/deps.py` | Injeção de dependências (composition root) | `get_*_use_case`, `get_authorization_service` |
| `bootstrap/app.py` | FastAPI, middlewares, lifespan | CORS, correlation ID, métricas |
| `init_db/database.sql` | **Única fonte** de schema + seed (sem migrations) | `permissions`, `role_permissions`, `roles` |
| `core/configs.py` | Settings lidos do `.env` | JWT, RBAC cache, segurança |
| `scripts/new_context.py` | Gerar novo bounded context | `make new-context NAME=x` |
| `scripts/check_domain_imports.py` | Validar domain/ sem FastAPI/SQLAlchemy | `make check-arch` |
| `contexts/_template/README.md` | Template para novo módulo | Novo bounded context |

### Banco de dados (RBAC)

| Tabela | Função |
|--------|--------|
| `permissions` | Catálogo de funcionalidades (`code` = ex. `users:read`) |
| `role_permissions` | N:N papel ↔ permissão |
| `roles` | Papéis (grupos de acesso) |
| `users.role_id` | Papel do usuário — **herda permissões do papel** |

Matriz papel→permissão **não está no código** (não existe `ROLE_PERMISSIONS`). Admin altera via `PUT /v1/roles/{id}/permissions`.

---

## Guia rápido para agentes de IA

Ao receber uma tarefa de implementação, use **[`AGENT_IMPLEMENTATION_PROMPT.md`](AGENT_IMPLEMENTATION_PROMPT.md)** (prompt copy-paste) e siga esta ordem:

### 1. Contextualizar (obrigatório)

1. Ler [`docs/FUNCTIONALITY_CATALOG.md`](docs/FUNCTIONALITY_CATALOG.md) — não duplicar rotas/permissões existentes.
2. Ler [`docs/RBAC.md`](docs/RBAC.md) se a tarefa envolve acesso, papéis ou novas telas.
3. Ler [`docs/architecture/golden_rules.md`](docs/architecture/golden_rules.md) — respeitar camadas.

### 2. Implementar nova feature (ordem correta)

```
Permissões (modulo:acao) → init_db ou POST /permissions
    → use case em application/use_cases/
    → port + repositório em infrastructure/ (se persistência nova)
    → endpoint em presentation/ + require_permission(...)
    → DI em bootstrap/deps.py
    → atualizar docs/FUNCTIONALITY_CATALOG.md
```

### 3. Regras que **não** podem ser violadas

| ❌ Não fazer | ✅ Fazer |
|-------------|----------|
| Matriz RBAC no código Python | Associar permissões no banco (`role_permissions`) |
| SQLAlchemy / FastAPI em `domain/` | Infra e presentation nas camadas corretas |
| Lógica de negócio em endpoints | Use cases em `application/` |
| Chamar repositório direto sem use case (mutação) | Use case + `AuthorizationService` quando necessário |
| Permissão direta por usuário | Sempre via `users.role_id` → papel |
| Migrations / Alembic | Alterar `init_db/database.sql` (+ `make docker-fresh` em dev) |
| Esquecer de atualizar o catálogo | Sempre atualizar `FUNCTIONALITY_CATALOG.md` |

### 4. Tarefa → documento principal

| Tarefa | Ler |
|--------|-----|
| Nova rota / CRUD / módulo | `FUNCTIONALITY_CATALOG.md` + seção 4 deste README + `golden_rules.md` |
| Permissão / papel / quem acessa o quê | `RBAC.md` |
| Login, JWT, bloqueio, reset senha | `SECURITY.md` + catálogo (rotas auth) |
| Novo bounded context | `contexts/_template/README.md` + `public_api.md` |
| Bug / 403 / banco offline | `TROUBLESHOOTING.md` |
| Variável de ambiente | `.env-sample` + `core/configs.py` |

### 5. Arquivos-chave do RBAC (referência rápida)

```
require_permission(...)     → infrastructure/security/authorization.py
Consulta banco + cache      → infrastructure/security/db_authorization_service.py
Catálogo SQL                → init_db/database.sql (tabelas permissions, role_permissions)
Constantes de referência    → domain/permission.py (não é matriz de acesso)
JWT / usuário logado        → infrastructure/security/deps.py
```

---

## Manual de uso (fluxos)

## 1. Subir o ambiente

```bash
cp .env-sample .env
make install
make dev          # Docker: API + PostgreSQL + pgAdmin
make health       # GET /health e /health/ready
```

- Schema + seed: `init_db/database.sql` (primeiro start do volume Docker)
- Reset total do banco: `make docker-fresh`
- API local: `make run` → http://localhost:8000/docs

**Admin inicial** (`init_db/database.sql`):

| Campo | Valor |
|-------|-------|
| CPF | `00000000000` |
| Senha | `Admin@123456` |
| E-mail | `admin@example.com` |

---

## 2. Fluxo: autenticar

```
1. POST /v1/users/login     (CPF + senha, form OAuth2)
   ← access_token, refresh_token, token_type

2. Requisições protegidas:
   Header: Authorization: Bearer <access_token>

3. Token expirado:
   POST /v1/users/refresh?refresh_token=<token>

4. Dados do usuário logado:
   GET /v1/users/logged

5. Permissões para o frontend (menus/botões):
   GET /v1/users/me/permissions
   ← {"permissions": ["users:read", ...]}
```

---

## 3. Fluxo: gerenciar acesso (operacional / admin)

RBAC é **dinâmico**: catálogo e matriz papel→permissão ficam no PostgreSQL.

```
┌─ Catálogo de funcionalidades ─────────────────────────────┐
│  GET  /v1/permissions/          (permissions:read)       │
│  POST /v1/permissions/          (permissions:create)     │
│       → registra code ex: "products:read"               │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─ Papéis (grupos) ───────────────────────────────────────┐
│  GET  /v1/roles/                (roles:read)            │
│  POST /v1/roles/                (roles:create)          │
│  PUT  /v1/roles/{id}/permissions (roles:update)         │
│       → {"permissions": ["users:read", "products:read"]} │
│       ⚠ substitui a lista inteira do papel              │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─ Usuários ───────────────────────────────────────────────┐
│  Cada usuário tem role_id → herda permissões do papel   │
│  GET /v1/users/  PUT /v1/users/{id}  block/unblock       │
└─────────────────────────────────────────────────────────┘
```

**Papéis seed (IDs fixos):**

| ID | Papel | Seed |
|----|-------|------|
| 1 | User | sem permissões |
| 2 | Operator | `users:read` |
| 3 | Administrator | todas + bypass em código |
| 4 | User_client | sem permissões |

Detalhes: [`docs/RBAC.md`](docs/RBAC.md) · Catálogo completo: [`docs/FUNCTIONALITY_CATALOG.md`](docs/FUNCTIONALITY_CATALOG.md)

---

## 4. Fluxo: implementar nova feature (desenvolvedor)

```
1. Definir permissões por ação
   Ex: products:read, products:create, products:update, products:delete

2. Registrar no catálogo (banco)
   POST /v1/permissions  ou  init_db/database.sql

3. Atualizar docs/FUNCTIONALITY_CATALOG.md

4. Criar use case(s) em application/use_cases/
   → receber actor_role_id; checar AuthorizationService quando necessário

5. Criar rotas em presentation/api/v1/endpoints/
   → require_permission("products:read") por endpoint

6. Registrar DI em bootstrap/deps.py

7. Associar permissões aos papéis (admin)
   PUT /v1/roles/{id}/permissions

8. Frontend: GET /v1/users/me/permissions
```

**Regra:** rota protege a entrada HTTP; **use case** protege a regra de negócio quando há mais de um caminho até o repositório. Não chamar repositório direto sem autorização.

Novo bounded context: `make new-context NAME=meu_modulo` · Validar camadas: `make check-arch`

---

## 5. Fluxo: requisição HTTP protegida

```
Cliente
  → middleware (correlation ID, métricas, access log)
  → endpoint + require_permission("modulo:acao")
  → get_current_user (JWT)
  → DbAuthorizationService → role_permissions (PostgreSQL)
  → use case → domínio → repositório → PostgreSQL
```

---

## 6. Referência rápida de rotas

Consulte o catálogo completo em [`docs/FUNCTIONALITY_CATALOG.md`](docs/FUNCTIONALITY_CATALOG.md).

| Grupo | Exemplos |
|-------|----------|
| Auth | login, refresh, signup, forgot/reset password |
| Usuários | CRUD, block/unblock, me/permissions |
| Papéis | CRUD, PUT …/permissions |
| Permissões | GET/POST catálogo |
| Ops | /health, /health/ready, /metrics |

---

## 7. Variáveis de ambiente

Copie `.env-sample` → `.env`.

| Variável | Uso |
|----------|-----|
| `SECRET` | JWT |
| `DATABASE_*` | PostgreSQL |
| `SIGNUP_PUBLIC` | Cadastro aberto (`true`) ou exige `users:create` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Validade do refresh token |
| `CORS_ORIGINS` | Origens permitidas |
| `LOGIN_MAX_FAILED_ATTEMPTS` | Bloqueio por login (padrão 3) |
| `PASSWORD_RESET_*` | Limite de reset de senha |
| `PERMISSION_CACHE_TTL_SECONDS` | Cache RBAC por papel |
| `LOG_FORMAT` | `text` ou `json` |
| `METRICS_ENABLED` | Middleware de métricas |

Lista completa: `.env-sample`

---

## 8. Estrutura do projeto

```
LogIn/
├── bootstrap/              # app, DI, sessão
├── contexts/
│   └── identity_access/    # domain → application → infrastructure → presentation
├── core/                   # config, logging, middleware
├── docs/                   # catálogo, RBAC, segurança
├── init_db/                # database.sql (schema + seed)
├── scripts/                # new_context.py, check_domain_imports.py
└── main.py
```

---

## 9. Comandos úteis

| Comando | Ação |
|---------|------|
| `make dev` | Stack Docker com hot reload |
| `make run` | API local (uvicorn) |
| `make health` | Testa health endpoints |
| `make docker-fresh` | Apaga volume e reaplica SQL |
| `make new-context NAME=x` | Gera bounded context template |
| `make check-arch` | Valida imports proibidos em domain/ |

---

## 10. Status das fases

| Fase | Status |
|------|--------|
| A — Fundação (env, Docker, health) | ✅ |
| B — Segurança (bloqueio, rate limit, CORS) | ✅ |
| RBAC dinâmico (permissions + role_permissions) | ✅ |
| C — Observabilidade | ✅ |
| D — Template bounded context | ✅ |
| E — Signup configurável + refresh token | ✅ |
| F — Testes + CI | Pendente |
| G — Template GitHub | Pendente |
| H — Integrações plug-and-play | Pendente |
