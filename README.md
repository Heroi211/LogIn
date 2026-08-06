# LogIn — Backend Template (FastAPI)

Backend reutilizável para autenticação, usuários, papéis (RBAC), OAuth Google, API Keys, sessões server-side e mensagens WhatsApp (Twilio).

## Requisitos

- Python 3.10+
- Docker + Docker Compose (para stack completa)
- Make (opcional, recomendado)

## Início rápido

### Desenvolvimento local (sem Docker)

Usa repositórios **mock** — não precisa de PostgreSQL.

```bash
cp .env-sample .env
make install-dev
make run
```

API: http://localhost:8000/docs

### Stack Docker do zero

Sobe PostgreSQL, API e pgAdmin — instala dependências dentro da imagem, aplica `init_db/database.sql` automaticamente.

```bash
cp .env-sample .env   # se ainda não existir
make docker-fresh
```

O alvo `docker-fresh` (inspirado no projeto Machine-Learning):

1. Para containers, remove volumes e imagens locais do compose
2. Limpa cache de build (`docker builder prune -af`)
3. Rebuild completo (`--no-cache --pull`)
4. Sobe stack limpa (`up -d --force-recreate`)

| Serviço | URL |
|---------|-----|
| API | http://localhost:8000/docs |
| pgAdmin | http://localhost:5050 |
| PostgreSQL | localhost:5432 |

Acompanhar logs: `make docker-logs`

## Comandos Make

| Comando | Descrição |
|---------|-----------|
| `make install-dev` | Instala `requirements.txt` + `requirements-dev.txt` |
| `make run` | Uvicorn local (porta 8000) |
| `make lint` | Ruff check |
| `make format` | Ruff format |
| `make test` | Pytest com cobertura mínima 70% |
| `make test-fast` | Pytest sem cobertura |
| `make coverage` | Relatório completo (terminal + HTML em `htmlcov/`) |
| `make check` | lint + test-fast |
| `make docker-up` | Sobe stack Docker |
| `make docker-down` | Para stack |
| `make docker-fresh` | Reset total e stack limpa |
| `make pre-commit` | Instala e executa hooks |
| `make clean` | Remove artefatos de teste e cache |

## Credenciais mock (`ENVIRONMENT=development`)

| Papel | CPF | Senha |
|-------|-----|-------|
| Operador | `11111111111` | `dev123` |
| Administrador | `22222222222` | `admin123` |

OAuth Google em dev: use `id_token` = `dev-google-mock` em `POST /v1/auth/google/callback`.

## Variáveis de ambiente

Copie `.env-sample` para `.env`. Principais:

| Variável | Descrição |
|----------|-----------|
| `ENVIRONMENT` | `development` (mocks) ou `production` (PostgreSQL) |
| `SECRET` | Chave JWT |
| `FRONTEND_URL` / `CORS_ORIGINS` | CORS para frontend |
| `MAX_FAILED_LOGIN_ATTEMPTS` | Bloqueio após N tentativas (padrão: 3) |
| `GOOGLE_CLIENT_*` | OAuth Google |
| `TWILIO_*` | WhatsApp (mock em development) |

Detalhes completos: `.env-sample` e `BACKEND_STATUS.md`.

## Testes

```bash
make install-dev
make coverage
```

- **Unitários:** security, JWT, lockout de login, messaging, domínio
- **Integração:** health, users, roles, middleware, API keys, OAuth mock
- **Cobertura mínima:** 70% (configurado em `pyproject.toml`)
- Relatório HTML: `htmlcov/index.html`

## Pre-commit

```bash
make pre-commit
```

Hooks: **ruff** (lint + format). Mypy configurado em `pyproject.toml` (`make lint` / IDE).

## Arquitetura

```
src/
├── domain/          # entidades, ports, exceções
├── application/     # use cases, container, DTOs
├── infrastructure/  # auth, messaging, mappers
├── repositories/    # SQLAlchemy, mocks, Twilio
├── api/v1/          # endpoints FastAPI
├── core/            # config, deps, security, middleware
├── models/          # SQLAlchemy ORM
├── schemas/         # Pydantic
└── services/        # camada de serviço legada (users, roles)
```

## Endpoints principais

| Área | Prefixo |
|------|---------|
| Health | `/health`, `/health/live`, `/health/ready` |
| Meta (bootstrap frontend) | `/v1/meta` |
| Users / Auth | `/v1/users/*` |
| Roles | `/v1/roles/*` |
| OAuth Google | `/v1/auth/google/*` |
| API Keys | `/v1/api-keys/*` |
| WhatsApp | `/v1/messaging/*` |

RBAC: ver `docs/RBAC.md`.

## Banco de dados

Schema em `init_db/database.sql` (sem Alembic). Após alterações no SQL:

```bash
make docker-fresh
```

Ou manualmente: `docker compose down -v && docker compose up --build`.

## Documentação adicional

- `BACKEND_STATUS.md` — status técnico e histórico de entregas
- `init_db/README.md` — gestão do banco
- `docs/RBAC.md` — matriz de permissões
- `docs/CHECKLIST_CORRECOES.md` — checklist de correções (auditoria v2.0)
