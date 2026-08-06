# Status do Backend — LogIn

Documento de acompanhamento do backend template.  
Última atualização: 06/08/2026.

---

## Resumo atual

| Métrica | Auditoria inicial | Situação atual |
|---|---|---|
| Módulos de API | 5 | **7** (`users`, `roles`, `meta`, `auth`, `api-keys`, `messaging`, `health`) |
| Rotas de negócio | ~35 | **29** |
| Rotas de infra | — | **3** (`/health`, `/health/live`, `/health/ready`) |
| **Total de rotas** | — | **32** |
| Entidades ORM | 6 | **6** (`Users`, `Roles`, `Sessions`, `ApiKeys`, `RevokedTokens` + messaging externo) |
| Arquivos Python (`src/`) | — | **~81** |
| Testes automatizados | 0 | **48** (cobertura **~87%**) |
| CI/CD | Não | **Não** (deliberado) |
| `print()` no backend | Vários | **0** |

---

## Visão geral do backend

- [x] Inventário técnico completo realizado (fase de análise)
- [x] Backend reorganizado em `src/` (entrypoint `main.py` na raiz)
- [x] Escopo reduzido para **users + roles** (rotinas, clientes e users-clients removidos)
- [x] **Frontend removido** — template backend-only
- [x] Camada de **repositórios** (SQLAlchemy + mocks via `ENVIRONMENT`)
- [x] **Clean Architecture / DDD** — `domain/` (entities, ports, exceptions) + `application/` (use cases, container)
- [x] Arquitetura endpoint → use case → repository
- [x] Autenticação JWT Access Token + Refresh Token
- [x] **Sessões server-side** — cookie HttpOnly + tabela `sessions`
- [x] **OAuth Google** — `/v1/auth/google/url` e `/v1/auth/google/callback`
- [x] **API Key** — header `X-API-Key` + CRUD em `/v1/api-keys/`
- [x] **Pronto para frontend** — CORS, login JSON, refresh token, meta bootstrap

---

## Arquitetura (Clean Architecture)

```
src/
├── domain/           # entities, ports (interfaces), exceptions
├── application/      # use cases, container (DI), services
├── infrastructure/   # google oauth, token utils, mappers
├── api/              # endpoints HTTP (finos)
├── repositories/     # implementações SQLAlchemy + mocks
├── models/           # ORM (infra persistence)
├── schemas/          # contratos HTTP (Pydantic)
└── services/         # session_service, utils (legado fino)
```

### Use cases principais

| Use case | Responsabilidade |
|---|---|
| `LoginUserUseCase` | Login CPF/senha + cria sessão server-side + JWT |
| `LogoutUserUseCase` | Revoga sessão no banco |
| `RefreshTokenUseCase` | Renova JWT + nova sessão |
| `GoogleOAuthUseCase` | Login/cadastro via Google |
| `CreateApiKeyUseCase` | Gera API Key (admin) |
| `RegisterUserUseCase` | Cadastro local |
| `ListUsersUseCase` / `GetUserUseCase` / `UpdateUserUseCase` / `DeleteUserUseCase` | CRUD users |
| `CreateRoleUseCase` / `UpdateRoleUseCase` / `DeleteRoleUseCase` | CRUD roles |
| `GoogleLinkAccountUseCase` | Vincular Google a conta local (CPF + senha) |
| `ForgotPasswordUseCase` / `ResetPasswordUseCase` | Recuperação de senha |

---

## Autenticação (3 métodos)

| Método | Como usar |
|---|---|
| **JWT Bearer** | `Authorization: Bearer <access_token>` |
| **Sessão server-side** | Cookie `session_token` (HttpOnly, setado no login) |
| **API Key** | Header `X-API-Key: ltk_<prefix>_<secret>` |

Prioridade no `get_current_user`: API Key → Cookie → JWT.

### OAuth Google

```env
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/google/callback
```

Em `development`, use `id_token: "dev-google-mock"` no callback **com `state` válido** (obtido em `GET /v1/auth/google/url`).

Em **production**, `id_token` direto no callback é **rejeitado** — use fluxo `code`.

Conta local com mesmo e-mail Google exige **`POST /v1/auth/google/link`** antes do callback.

### API Keys (admin)

- `POST /v1/api-keys/` — cria key (retornada **uma vez**)
- `GET /v1/api-keys/` — lista keys do admin
- `DELETE /v1/api-keys/{id}` — revoga

### Sessões

```env
SESSION_EXPIRE_DAYS=7
SESSION_COOKIE_NAME=session_token
SESSION_COOKIE_SECURE=false
SESSION_COOKIE_SAMESITE=lax
```

---

## Integração com frontend

### CORS

Origens permitidas via `.env`:

```env
FRONTEND_URL=http://localhost:3000
# ou múltiplas origens:
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:5173
```

Em `development`, se nenhuma origem for definida, usa `localhost:3000` e `127.0.0.1:3000`.

### Fluxo de autenticação (SPA)

1. **Bootstrap** — `GET /v1/meta` → URLs de auth, ambiente, docs
2. **Login** — `POST /v1/users/login/json` com `{ "cpf": "...", "password": "..." }`
3. **Resposta** — `TokenResponse` com `access_token`, `refresh_token`, `expires_in` e `user` (perfil + role)
4. **Requisições autenticadas** — header `Authorization: Bearer <access_token>`
5. **Renovar sessão** — `POST /v1/users/refresh` com `{ "refresh_token": "..." }`
6. **Perfil atual** — `GET /v1/users/logged` → `UserSession` (sem senha)

### Exemplo de login (fetch)

```javascript
const res = await fetch("http://localhost:8000/v1/users/login/json", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  credentials: "include",
  body: JSON.stringify({ cpf: "22222222222", password: "admin123" }),
});
const { access_token, refresh_token, expires_in, user } = await res.json();
localStorage.setItem("access_token", access_token);
localStorage.setItem("refresh_token", refresh_token);
```

### Rotas pensadas para SPA

| Método | Endpoint | Uso no front |
|---|---|---|
| GET | `/v1/meta` | Descobrir URLs e ambiente na inicialização |
| POST | `/v1/users/login/json` | Login com JSON (recomendado para SPA) |
| POST | `/v1/users/login` | Login OAuth2 form (Swagger / Postman) |
| POST | `/v1/users/refresh` | Renovar access token sem relogar |
| GET | `/v1/users/logged` | Hidratar estado do usuário logado |
| POST | `/v1/users/reset-password` | Body JSON `{ "token", "password" }` |

---

## Ambiente (`ENVIRONMENT`)

| Valor | Comportamento |
|---|---|
| `development` | Repositórios **mockados** (in-memory). PostgreSQL **não** é exigido. `/health/ready` retorna `"database": "mocked"`. E-mail de reset **logado** no stdout (sem SMTP). |
| `production` (padrão) | Repositórios **SQLAlchemy** + PostgreSQL. Readiness verifica `SELECT 1`. |

### Credenciais mock (development)

| Papel | CPF | Senha |
|---|---|---|
| Operador | `11111111111` | `dev123` |
| Administrador | `22222222222` | `admin123` |

```env
ENVIRONMENT=development
SECRET=<qualquer valor para JWT>
```

---

## Módulos e APIs

### Módulos ativos

| Módulo | Prefixo | Rotas | Autenticação |
|---|---|---|---|
| **Health** | `/health` | 3 | Nenhuma |
| **Meta** | `/v1/meta` | 1 | Nenhuma |
| **Users** | `/v1/users` | 11 | JWT (exceto signup, login, refresh, forgot/reset) |
| **Roles** | `/v1/roles` | 5 | JWT |

### Rotas disponíveis

| Método | Endpoint | Finalidade |
|---|---|---|
| GET | `/health` | Health check (alias liveness) |
| GET | `/health/live` | Liveness — processo vivo |
| GET | `/health/ready` | Readiness — app + banco OK (503 se DB indisponível) |
| GET | `/v1/meta` | Bootstrap do frontend (URLs auth, ambiente) |
| POST | `/v1/users/signup` | Cadastro |
| POST | `/v1/users/login` | Login (OAuth2 form — Swagger) |
| POST | `/v1/users/login/json` | Login JSON (SPA) |
| POST | `/v1/users/refresh` | Renovar access token |
| GET | `/v1/users/logged` | Usuário autenticado + role |
| GET | `/v1/users/` | Listar usuários |
| GET | `/v1/users/{id}` | Buscar usuário |
| PUT | `/v1/users/{id}` | Atualizar usuário |
| DELETE | `/v1/users/{id}` | Soft delete |
| POST | `/v1/users/forgot-password/{email}` | Enviar e-mail de reset |
| POST | `/v1/users/reset-password` | Redefinir senha |
| POST | `/v1/roles/` | Criar role |
| GET | `/v1/roles/` | Listar roles |
| GET | `/v1/roles/{id}` | Buscar role |
| PUT | `/v1/roles/{id}` | Atualizar role |
| DELETE | `/v1/roles/{id}` | Soft delete |

Documentação interativa: `/docs`, `/redoc`.

### Módulos removidos (fora do escopo atual)

- [x] ~~Routines~~
- [x] ~~Clients~~
- [x] ~~Users_update~~ — removido (auditoria via logging da aplicação)

### Infraestrutura de API

- [x] Documentação OpenAPI/Swagger automática
- [x] Health check (`GET /health`) — alias de liveness; ignorado no access log
- [x] Liveness (`GET /health/live`) — processo vivo; falha → reinício do container
- [x] Readiness (`GET /health/ready`) — verifica PostgreSQL (`SELECT 1`); em `development` retorna `"database": "mocked"`

---

## Logging e observabilidade

Implementação portada e adaptada do projeto `Machine-Learning`.

### Concluído

- [x] `src/core/logging_setup.py` — logger raiz → stdout (Docker/`docker logs`)
- [x] `src/core/logging_api_request.py` — JSONL rotacionado de access logs
- [x] `src/core/middleware/request_record.py` — latência, status, client IP, `request_id`, header `X-Request-ID`
- [x] Inicialização no `main.py` antes do app FastAPI
- [x] Variáveis de ambiente em `.env-sample` e `Example file.txt`
- [x] Volumes Docker (`./logs`, `./reports`)
- [x] Script `src/scripts/maintenance/latency_report.py`
- [x] `logger = logging.getLogger(__name__)` em todos os endpoints e services
- [x] Todos os `print()` substituídos por logging
- [x] `.gitignore` ignora arquivos de log, preserva estrutura de pastas

### Onde os logs são salvos

| Tipo | Local padrão | Formato |
|---|---|---|
| Console / stdout | terminal ou `docker logs api_login` | Texto legível |
| Access log HTTP | `logs/api_requests/access.jsonl` | JSONL (1 linha por request) |
| Rotação | `logs/api_requests/access.jsonl.1`, `.2`… | ~5 MiB, 5 backups |
| Relatório de latência | `reports/maintenance/latency_summary_*.csv` | CSV (p50/p90/p95/p99) |

### Variáveis de ambiente (logging)

```env
DEBUG=false
LOG_HTTP_REQUESTS=true
LOG_HTTP_REQUESTS_FILE=true
PATH_API_REQUEST_LOGS=logs/api_requests
LOG_HTTP_REQUESTS_MAX_BYTES=5242880
LOG_HTTP_REQUESTS_BACKUP_COUNT=5
PATH_MAINTENANCE_REPORTS=reports/maintenance
```

### Relatório de latência

```bash
python3 src/scripts/maintenance/latency_report.py
python3 src/scripts/maintenance/latency_report.py --slo-ms 300
```

### Pendente (logging)

- [ ] Testes automatizados do middleware e do script de latência

---

## Modelo de dados

### Entidades ativas

- [x] `Users` — autenticação, perfil, reset de senha
- [x] `Roles` — papéis de acesso

> **Observabilidade:** auditoria de alterações de usuário é coberta pelo logging da aplicação (`access.jsonl` + stdout). A tabela/model `Users_update` foi removida para evitar duplicidade de mecanismos.

### Banco de dados

Gestão **autônoma via SQL** — sem Alembic. Fonte da verdade: `init_db/database.sql` (aplicado na primeira subida do Docker). Ver `init_db/README.md`.

- [x] `init_db/database.sql` alinhado com models ORM (`Users`, `Roles`)
- [x] Seed de roles com 2 papéis (Operador=1, Administrador=2)
- [x] Índices em `users.email`, `users.role_id`, `users.reset_password_token`, `roles.active`
- [x] Remoção de `createdb.py` (legado — schema criado pelo Docker + `init_db/`)
- [x] Remoção de `DB_BaseModel` em `configs.py` (não utilizado)
- [x] Decisão explícita: **sem migrations Alembic** — versões de schema via Git + SQL manual

### Diagrama (schema v1.4.0)

```
roles                          users
├── id (PK)                    ├── id (PK)
├── description                ├── password (nullable — OAuth)
├── active                     ├── name, email (UNIQUE), phone
├── created_at                 ├── cpf (UNIQUE), google_id
                               ├── role_id (FK → roles.id)
                               ├── auth_provider
                               ├── reset_password_token
                               ├── reset_password_expires
                               ├── active
                               └── created_at

sessions                       api_keys                    revoked_tokens
├── id (PK)                    ├── id (PK)                 ├── id (PK)
├── user_id (FK)               ├── user_id (FK)            ├── jti (UNIQUE)
├── token_hash                 ├── prefix, key_hash        ├── expires_at
├── expires_at                 ├── scopes                  └── created_at
├── ip_address                 ├── active
├── user_agent                 └── created_at
└── created_at
```

---

## Autenticação e segurança

- [x] JWT Access Token + **Refresh Token** (OAuth2 Password Flow — CPF + senha)
- [x] Hash de senha com bcrypt (passlib)
- [x] Middleware de validação de body no signup (path dinâmico via `PROJECT_VERSION`)
- [x] CORS configurado
- [x] Credenciais SMTP externalizadas para `.env`
- [x] CORS configurável (`FRONTEND_URL` / `CORS_ORIGINS`)
- [x] Rotação/revogação de tokens — blacklist por `jti` (`revoked_tokens`); refresh revoga o token anterior; logout revoga sessão + tokens informados
- [x] Proteção de login — bloqueio automático (`active=false`) após **3** tentativas incorretas (`MAX_FAILED_LOGIN_ATTEMPTS`); admin reativa via `PUT /users/{id}` com `active=true`
- [x] Rate limiting básico em signup e login (in-memory, 30 req/min por IP)
- [x] Guard `ALLOW_MOCK_REPOS` — impede `ENVIRONMENT=development` com DB remoto sem flag explícita
- [x] Credenciais removidas dos Dockerfiles (`db.dockerfile`, `pgadmin.dockerfile`, `api.dockerfile`)

### Variáveis de ambiente (SMTP)

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM_NAME=Cod3Bit Dev Team
SMTP_USE_SSL=true
FRONTEND_RESET_PASSWORD_URL=http://127.0.0.1:3000/resetpassword
```

Retorna **503** se `SMTP_USER` ou `SMTP_PASSWORD` não estiverem configurados.

---

## Controle de acesso (RBAC)

- [x] Papéis: **Operador** (1) e **Administrador** (2) — User e User_client removidos
- [x] Verificação de admin corrigida via `require_admin` / `require_operator` (`src/core/permissions.py`)
- [x] Dependencies reutilizáveis: `require_role`, `require_operator`, `require_admin`
- [x] Matriz role × endpoint documentada em `docs/RBAC.md`

---

## Repositórios

- [x] Contratos em `src/repositories/base.py` (`UsersRepository`, `RolesRepository`)
- [x] Implementação SQLAlchemy em `src/repositories/sqlalchemy/`
- [x] Implementação mock em `src/repositories/mocks/` (store in-memory compartilhado)
- [x] Factory em `src/repositories/factory.py` — escolhe mock vs SQLAlchemy via `ENVIRONMENT`
- [x] Services legados `users_services.py` / `roles_services.py` **removidos** — use cases + container
- [x] `deps.py` usa `AppContainer` (sem factories diretas)

## Integrações

### Twilio / WhatsApp (DDD)

- [x] Porta `WhatsAppMessagingPort` em `domain/ports/messaging.py`
- [x] Repositório Twilio `repositories/twilio/whatsapp_repository.py` — [docs oficiais](https://www.twilio.com/docs/whatsapp/api)
- [x] Mock em `development` (`repositories/mocks/whatsapp_repository.py`)
- [x] Use cases: enviar mensagem, template, status, lookup, `notify_admin`
- [x] Factory `WhatsAppMessagingRepositoryFactory` — live se credenciais + `TWILIO_ENABLED` (dev) ou credenciais (prod)
- [x] Endpoints admin em `/v1/messaging/` (JWT admin)

| Método | Endpoint | Finalidade |
|---|---|---|
| POST | `/v1/messaging/whatsapp` | Enviar mensagem freeform |
| POST | `/v1/messaging/whatsapp/template` | Enviar Content Template |
| GET | `/v1/messaging/whatsapp/{sid}` | Status da mensagem |
| POST | `/v1/messaging/whatsapp/notify-admin` | Feedback ao admin (`TWILIO_ADMIN_PHONE`) |
| GET | `/v1/messaging/phone/{phone}/lookup` | Validar número (Lookup API) |

```env
TWILIO_ENABLED=false          # dev: true + credenciais → Twilio live
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
TWILIO_ADMIN_PHONE=5511999990002
```

Uso interno (alertas futuros):

```python
container = get_container(db)
await container.notify_admin_whatsapp.execute("Novo usuário cadastrado: ...")
```

## Qualidade e maturidade

- [x] Testes unitários + integração (**48** testes, **~87%** cobertura)
- [x] Cobertura mínima definida (70% — `pyproject.toml`, `make coverage`)
- [ ] Pipeline CI/CD (lint, test, build Docker) — **pendente**
- [x] README do backend (`README.md`)
- [x] Pre-commit hooks (ruff; mypy em `pyproject.toml`)
- [x] Makefile (`docker-fresh`, `coverage`, `install-dev`, etc.)
- [x] Checklist de correções pós-auditoria ([`docs/CHECKLIST_CORRECOES.md`](docs/CHECKLIST_CORRECOES.md) v2.0)

---

## Estrutura do projeto

```
LogIn/
├── main.py                              # entrypoint (sys.path → src/)
├── Makefile                             # install-dev, test, coverage, docker-fresh, …
├── pyproject.toml                       # pytest, coverage 70%, ruff, mypy
├── requirements-dev.txt
├── README.md
├── BACKEND_STATUS.md
├── .env-sample
├── .pre-commit-config.yaml
├── requirements.txt
├── docker-compose.yaml
├── tests/                               # unit + integration (ENVIRONMENT=development)
├── src/
│   ├── api/v1/
│   │   ├── api.py                       # router users + roles
│   │   ├── middleware.py                # validação body signup
│   │   └── endpoints/
│   │       ├── health.py                # GET /health
│   │       ├── users.py
│   │       └── roles.py
│   ├── core/
│   │   ├── configs.py
│   │   ├── permissions.py             # require_role, require_admin, require_operator
│   │   ├── auth.py / deps.py / security.py / database.py
│   │   ├── logging_setup.py
│   │   ├── logging_api_request.py
│   │   └── middleware/request_record.py
│   ├── models/                          # users, roles
│   ├── repositories/                    # base, factory, sqlalchemy, mocks, twilio
│   ├── schemas/
│   ├── services/                        # session_service, utils
│   └── scripts/maintenance/latency_report.py
├── docs/RBAC.md                         # matriz role × endpoint
├── init_db/
│   ├── database.sql                     # schema v1.4.0 (fonte da verdade)
│   └── README.md                        # gestão autônoma do banco
├── logs/api_requests/                   # access.jsonl (runtime)
├── reports/maintenance/                 # CSVs de latência (runtime)
└── docker/
```

---

## Prioridades sugeridas

1. Pipeline CI/CD (lint, test, build Docker)
2. Testes de integração com PostgreSQL (testcontainers ou compose)
3. OAuth production: substituir `tokeninfo` + PKCE completo
4. Lint zero (E501 legado) ou relaxar regra no `pyproject.toml`

---

## Histórico de entregas

| Data | Entrega |
|---|---|
| Ago/2026 | Auditoria técnica completa (inventário factual) |
| Ago/2026 | Reestruturação do backend em `src/` |
| Ago/2026 | Logging (stdout + JSONL + middleware + latency report) |
| Ago/2026 | Remoção de rotinas, clientes e users-clients |
| Ago/2026 | Health check `/health`, SMTP via env, loggers padronizados, prints removidos |
| Ago/2026 | Liveness `/health/live` e readiness `/health/ready` com verificação de banco |
| Ago/2026 | Remoção de `Users_update` — observabilidade unificada via logging |
| Ago/2026 | Schema SQL v1.0.0 alinhado aos models; remoção de `createdb.py`; gestão autônoma sem Alembic |
| Ago/2026 | RBAC: Operador + Administrador, `require_admin`/`require_operator`, `docs/RBAC.md` |
| Ago/2026 | Remoção do frontend; camada de repositórios; `ENVIRONMENT=development` com mocks |
| Ago/2026 | Pronto para frontend: CORS, login JSON, refresh token, `/meta`, `UserSession` |
| Ago/2026 | Clean Architecture, sessões server-side, OAuth Google, API Key |
| Ago/2026 | Checklist v2.0: use cases, OAuth link, revogação unificada, 48 testes, ~87% cobertura |
