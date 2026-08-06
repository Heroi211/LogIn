# Checklist de correções — Backend LogIn

> **Versão:** 2.0  
> **Data:** Ago/2026  
> **Origem:** [Auditoria técnica](../BACKEND_STATUS.md) — arquitetura, segurança, API, dados, Docker, testes e documentação  
> **Como usar:** marque `[x]` conforme concluir; priorize **P0 → P1 → P2** dentro de cada seção

---

## Índice

1. [Arquitetura e Clean Architecture](#1-arquitetura-e-clean-architecture)
2. [Segurança e autenticação](#2-segurança-e-autenticação)
3. [API HTTP e padronização](#3-api-http-e-padronização)
4. [Camada de dados e schema SQL](#4-camada-de-dados-e-schema-sql)
5. [RBAC e permissões](#5-rbac-e-permissões)
6. [Docker, ambiente e DevOps](#6-docker-ambiente-e-devops)
7. [Documentação](#7-documentação)
8. [Testes e cobertura](#8-testes-e-cobertura)
9. [Qualidade de código e lint](#9-qualidade-de-código-e-lint)
10. [Logging e observabilidade](#10-logging-e-observabilidade)
11. [Resumo por prioridade global](#11-resumo-por-prioridade-global)

---

## Legenda de prioridade

| Tag | Significado |
|-----|-------------|
| **P0** | Bloqueia uso seguro em produção |
| **P1** | Inconsistência relevante; corrigir antes de expor API externamente |
| **P2** | Melhoria de maturidade; pode ser incremental |

---

## 1. Arquitetura e Clean Architecture

### 1.1 Migração e convergência de camadas

- [x] **P1** Conectar users/roles ao `AppContainer` (use cases) **ou** remover `src/application/use_cases/users.py` morto
- [x] **P1** Migrar signup/CRUD de users de `users_services.py` para use cases
- [x] **P1** Migrar CRUD de roles de `roles_services.py` para use cases
- [x] **P1** Expor use cases de users/roles no `AppContainer`
- [x] **P1** Unificar DI: eliminar factories diretas espalhadas (`deps.py`, `services/`)

### 1.2 Desacoplamento de camadas

- [x] **P1** Remover dependência de `schemas/` em `domain/ports/repositories.py` — criar DTOs de domínio
- [ ] **P1** Remover dependência de `core/` em `application/use_cases/` (extrair ports para JWT/security)
- [x] **P1** Remover `HTTPException` de `services/users_services.py` (arquivo removido)
- [x] **P1** Remover `HTTPException` de `core/auth.py` (ou isolar em adapter HTTP) — `decode_*_safe` + handlers
- [x] **P1** Adicionar `@app.exception_handler(DomainError)` global em `main.py`
- [x] **P1** Parar de usar `IntegrityError` fake no signup — usar `DuplicateEntityError`

### 1.3 Padrões internos

- [x] **P1** Extrair `_issue_auth` para `IssueAuthUseCase` ou serviço compartilhado
- [x] **P1** Parar de chamar método privado `_issue_auth` de outro use case
- [x] **P2** Tipar `CreateApiKeyUseCase.api_keys` e `RevokeApiKeyUseCase.api_keys` como `ApiKeysRepositoryPort` (não `object`)
- [ ] **P1** Unificar retorno entity vs ORM em todos os repositórios (users **e** roles)
- [x] **P2** Consolidar `role_label()` e `role_display()` em um único lugar
- [ ] **P2** Remover duplicação de lógica de update entre mock e SQLAlchemy repos

### 1.4 Código morto

- [x] **P2** Remover ou conectar `RegisterUserUseCase`, `ListUsersUseCase`, `GetUserUseCase`, etc.
- [x] **P2** Remover `get_user_by_email` não utilizado em `users_services.py`
- [ ] **P2** Remover `role_display()` não utilizado em `infrastructure/persistence/mappers.py`
- [ ] **P2** Remover ou usar `RoleEntity`, `RevokedTokenEntity` em `domain/entities/user.py`
- [x] **P2** Remover ou usar exceções mortas: `EntityNotFoundError`, `DuplicateEntityError`, `SessionExpiredError`, `ApiKeyInvalidError` (parcial — em uso)
- [x] **P1** Integrar `revoke_all_for_user` no fluxo de auth (ou remover se descartado)
- [ ] **P2** Remover import duplicado em `repositories/factory.py`

### 1.5 Empacotamento

- [ ] **P2** Substituir hack de `sys.path` em `main.py` por pacote instalável (`pip install -e .`)

---

## 2. Segurança e autenticação

### 2.1 Crítico (P0)

- [x] **P0** Corrigir OAuth: **não** auto-vincular conta local só por e-mail Google
- [x] **P0** Exigir step-up (senha local ou verificação de e-mail) para vincular Google a conta existente — `POST /v1/auth/google/link`
- [x] **P0** Startup guard: falhar boot se `ENVIRONMENT=production` e `SECRET` vazio ou curto
- [x] **P0** Unificar revogação no logout: invalidar access JWT mesmo sem body (logout só com cookie)
- [x] **P0** Chamar `revoke_all_for_user` no logout
- [x] **P0** Chamar `revoke_all_for_user` no refresh (ou limitar sessões simultâneas)
- [x] **P0** Chamar `revoke_all_for_user` no reset de senha
- [x] **P0** Chamar `revoke_all_for_user` no lockout de conta
- [x] **P0** Blacklist de access token anterior no refresh (não só refresh token)

### 2.2 OAuth Google

- [x] **P0** Validar parâmetro `state` no callback (anti-CSRF)
- [ ] **P0** Priorizar fluxo `code` + PKCE; restringir `id_token` direto no callback (dev mock mantido; prod bloqueia id_token direto)
- [ ] **P1** Substituir endpoint deprecated `tokeninfo` por verificação local com chaves Google
- [ ] **P1** Exigir validação de `aud` sempre que OAuth estiver habilitado
- [ ] **P1** Não expor `dev-google-mock` fora de development (ou proteger endpoint)

### 2.3 API Keys

- [x] **P0** Implementar enforcement de `scopes` nos endpoints (ex.: `require_scope("read")`)
- [x] **P0** Impedir que key de admin herde RBAC completo se scope for limitado
- [x] **P1** Documentar comportamento de prioridade: API key > cookie > JWT

### 2.4 Tokens e sessões

- [x] **P1** Logout com access token expirado/malformado no body: ignorar silenciosamente em vez de 401
- [x] **P2** Job/cleanup de `revoked_tokens` expirados (evitar crescimento infinito)
- [ ] **P2** Usar ou remover coluna `revoked_tokens.active`

### 2.5 Senhas e lockout

- [x] **P1** Adicionar política mínima de senha (comprimento/complexidade) em signup/reset
- [ ] **P1** Separar lockout temporário de `active=false` (desativação admin) — mantido por decisão
- [x] **P0** Revogar sessões/JWT ao bloquear conta por tentativas
- [ ] **P2** Considerar desbloqueio automático após TTL configurável

### 2.6 Configuração e superfície de ataque

- [x] **P0** Default `SESSION_COOKIE_SECURE=true` em production
- [x] **P1** Alinhar atributos de `delete_cookie` com `set_cookie`
- [x] **P1** Revisar CORS: `allow_credentials=True` + `*` — restringir origins/methods/headers
- [x] **P0** Garantir que `ENVIRONMENT=development` nunca seja aceito em production sem flag explícita (`ALLOW_MOCK_REPOS`)
- [x] **P1** Rate limit em signup (e opcionalmente login)
- [x] **P1** Forgot-password: resposta constante (sem enumeração de e-mail — sempre 200)

### 2.7 Dados sensíveis em logs

- [x] **P1** Remover CPF de logs de falha de login
- [x] **P1** Remover token de reset de senha de logs (mesmo em development)
- [x] **P2** Revisar se access log JSONL precisa de `user_id`/`auth_method` sem expor PII

---

## 3. API HTTP e padronização

### 3.1 Status codes

- [x] **P1** `GET /v1/users/` → `200` (hoje `202`)
- [x] **P1** `GET /v1/users/{id}` → `200` (hoje `202`)
- [x] **P1** `PUT /v1/users/{id}` → `200` com body ou `204`
- [x] **P1** `DELETE /v1/roles/{id}` → `204` (hoje `202`)
- [x] **P1** Signup duplicado → `409 Conflict` (hoje `406`)
- [x] **P1** Login inválido → `401 Unauthorized` (hoje `400`)
- [ ] **P2** Alinhar `PUT /v1/roles/{id}` com padrão de users
- [x] **P2** Padronizar formato de `detail` em `/health/ready` (dict vs string)

### 3.2 Response models (Pydantic)

- [x] **P0** Remover `reset_password_token` e `reset_password_expires` de responses públicas de users
- [x] **P1** Criar schema para respostas de `logout`, `forgot-password`, `reset-password`
- [x] **P1** Criar schema para `GET /v1/meta`
- [x] **P1** Criar schema para `GET /v1/auth/google/url`
- [x] **P1** Adicionar `auth_provider` (e campos úteis) em responses de users onde fizer sentido
- [x] **P1** Corrigir `created_at: datetime.now()` em `schemas/users_schemas.py` (usar `default_factory`)
- [x] **P1** Garantir que `usersGetData` reflita o que o repositório devolve (ou ajustar repo)
- [x] **P1** `PUT /v1/users/{id}`: definir `response_model` ou retorno explícito

### 3.3 Error handling HTTP

- [x] **P1** Mapear `DuplicateEntityError` → `409` no signup
- [x] **P1** Mapear `EntityNotFoundError` → `404` onde aplicável
- [ ] **P1** Separar `OAuthError` → `503` vs `InvalidCredentialsError` → `401` no callback Google
- [x] **P2** Tratar `RuntimeError` da factory com resposta estruturada

### 3.4 Documentação OpenAPI

- [ ] **P2** Documentar que `OAuth2PasswordRequestForm.username` recebe **CPF** em `/users/login`
- [ ] **P2** Documentar prioridade de autenticação (API key / cookie / JWT)
- [ ] **P2** Revisar tags e descrições de endpoints (messaging, api-keys, auth)

---

## 4. Camada de dados e schema SQL

- [x] **P1** Adicionar `UNIQUE` em `users.email` (`init_db/database.sql`)
- [x] **P1** Permitir admin alterar `role_id` via API (`users_updateForm` + repository)
- [ ] **P2** Versionar e documentar passos após mudanças em `database.sql` (`make docker-fresh`)

---

## 5. RBAC e permissões

- [ ] **P1** Decidir se roles dinâmicas (criadas via `/roles`) entram no RBAC ou só Operador/Admin fixos
- [ ] **P1** Se dinâmicas: mapear `role_id` → permissões em vez de inteiros hardcoded
- [ ] **P2** Implementar permissões granulares (recurso/ação) ou documentar limitação atual
- [x] **P0** Conectar API key scopes ao RBAC (ver [§2.3](#23-api-keys))
- [ ] **P2** Expandir testes de operador vs admin em todos os endpoints sensíveis

---

## 6. Docker, ambiente e DevOps

- [x] **P0** Adicionar `env_file: .env` (ou `environment`) em `api_login` no `docker-compose.yaml`
- [x] **P0** Documentar e defaultar `DATABASE_SERVER=db_login` para stack Docker
- [x] **P0** Alinhar credenciais DB: `.env-sample` ↔ `docker/db.dockerfile` (`hero/280387/login`)
- [x] **P0** Remover senhas hardcoded dos Dockerfiles (usar args/secrets/env)
- [x] **P0** Remover credenciais hardcoded do pgAdmin Dockerfile
- [x] **P1** Healthcheck no serviço `db_login` + `depends_on` com condition
- [x] **P2** Remover ENTRYPOINT duplicado (`api.dockerfile` + `command` no compose)
- [ ] **P2** Opcional: bind mount `./src` para hot reload em dev
- [ ] **P1** Validar `make docker-fresh` end-to-end com API conectando ao Postgres
- [ ] **P2** Pipeline CI/CD: lint, test, build Docker (deliberadamente pendente)

---

## 7. Documentação

### 7.1 BACKEND_STATUS.md

- [ ] **P1** Atualizar contagem de arquivos Python (~61, não 19)
- [ ] **P1** Atualizar contagem de testes (34+, não 0)
- [ ] **P1** Atualizar contagem de rotas (~31; incluir logout, OAuth, api-keys, messaging)
- [ ] **P1** Atualizar schema para **v1.3.0**
- [ ] **P1** Atualizar diagrama de entidades (sessions, api_keys, revoked_tokens)
- [ ] **P1** Corrigir afirmação “endpoint → use case” para users (ainda usa services)
- [ ] **P1** Marcar `RegisterUserUseCase` como não conectado ou removê-lo da doc
- [ ] **P1** Completar tabela de rotas
- [ ] **P2** Corrigir “logger em todos os endpoints”
- [ ] **P1** Atualizar repositórios listados (Sessions, ApiKeys, RevokedTokens, WhatsApp)
- [ ] **P2** Link para este checklist: `docs/CHECKLIST_CORRECOES.md`

### 7.2 README.md

- [x] **P1** Documentar `DATABASE_SERVER=db_login` para Docker
- [x] **P1** Documentar credenciais DB do compose vs `.env-sample`
- [ ] **P2** Documentar limitações conhecidas (OAuth, logout JWT, scopes)
- [ ] **P2** Link para este checklist

### 7.3 Outros

- [ ] **P2** Atualizar `docs/RBAC.md` se RBAC mudar
- [ ] **P2** Atualizar `init_db/README.md` após alterações de schema

---

## 8. Testes e cobertura

### 8.1 Configuração

- [ ] **P1** Reavaliar omissões em `pyproject.toml` (`sqlalchemy/*`, `twilio/*`, `use_cases/users.py`)
- [ ] **P1** Meta: cobertura refletir caminho production, não só mocks

### 8.2 Autenticação

- [x] **P1** Auth por cookie `session_token`
- [x] **P1** Auth por header `X-API-Key` em `get_current_user`
- [x] **P1** Prioridade API key → cookie → JWT
- [x] **P0** Logout invalida refresh **e** access token
- [x] **P1** OAuth callback com `state` inválido/ausente
- [x] **P1** Signup duplicado → status correto após padronização HTTP
- [x] **P1** Teste de scopes de API key quando implementados
- [x] **P0** Teste de lockout revogando sessões (quando implementado)
- [x] **P1** Atualizar testes após mudança de status HTTP (202→200, etc.)

### 8.3 Endpoints

- [x] **P1** `PUT /v1/users/{id}`
- [x] **P1** Roles update e delete
- [x] **P2** `POST /v1/messaging/whatsapp/template`
- [x] **P1** Reset password end-to-end (substituir asserção fraca `(200, 400, 404)`)
- [ ] **P2** Signup com body inválido (edge cases do middleware)

### 8.4 Integração / production path

- [ ] **P1** Testes de integração com PostgreSQL (compose ou testcontainers)
- [ ] **P1** `/health/ready` com DB down em `ENVIRONMENT=production`
- [ ] **P1** Repositórios SQLAlchemy (smoke tests mínimos)
- [x] **P1** Reset password end-to-end — ver §8.3

### 8.5 Manutenção dos testes existentes

- [x] **P1** Atualizar testes após mudança de status HTTP (202→200, etc.) — duplicata de §8.2, mantida por histórico
- [x] **P1** Teste de scopes de API key quando implementados — duplicata de §8.2
- [x] **P0** Teste de lockout revogando sessões — duplicata de §8.2

---

## 9. Qualidade de código e lint

- [ ] **P2** Rodar `make lint-fix` e corrigir erros auto-fixáveis (~63)
- [ ] **P2** Corrigir E501 (linhas longas) no legado
- [ ] **P2** Corrigir I001 (imports desordenados)
- [ ] **P2** Padronizar naming de schemas (`usersGetData` → convenção consistente)
- [ ] **P2** Padronizar import `users_service` vs `users_services`
- [ ] **P2** Pre-commit passando em todo o repo (`make pre-commit`)

---

## 10. Logging e observabilidade

- [x] **P2** Adicionar logger em `api/v1/endpoints/auth.py` e `meta.py`
- [x] **P2** Enriquecer access log: `auth_method`, `user_id` (sem PII)
- [ ] **P2** Testes ou script para `scripts/maintenance/latency_report.py`
- [ ] **P2** Revisar default de `LOG_HTTP_REQUESTS` em production vs development

---

## 11. Resumo por prioridade global

### P0 — Antes de produção (14 itens principais)

| # | Item | Seção |
|---|------|-------|
| 1 | OAuth sem auto-link por e-mail | [§2.1](#21-crítico-p0) |
| 2 | Startup guard (`SECRET`) | [§2.1](#21-crítico-p0) |
| 3 | Revogação unificada (logout/refresh/reset/lockout) | [§2.1](#21-crítico-p0) |
| 4 | API key scopes enforcement | [§2.3](#23-api-keys) |
| 5 | Remover `reset_password_*` de API pública | [§3.2](#32-response-models-pydantic) |
| 6 | Docker env + `DATABASE_SERVER=db_login` | [§6](#6-docker-ambiente-e-devops) |
| 7 | Credenciais fora dos Dockerfiles | [§6](#6-docker-ambiente-e-devops) |

### P1 — Consistência e contrato (maior volume)

Arquitetura users/roles, status HTTP, schemas, schema SQL (`UNIQUE email`), testes production path, documentação desatualizada.

### P2 — Maturidade incremental

Lint, logging, empacotamento, CI/CD, permissões granulares, cleanup de código morto.

---

## Progresso (preencher manualmente)

| Seção | Total | Concluídos |
|-------|------:|----------:|
| 1. Arquitetura | 22 | 18 |
| 2. Segurança | 28 | 26 |
| 3. API HTTP | 20 | 18 |
| 4. Dados / SQL | 6 | 2 |
| 5. RBAC | 5 | 1 |
| 6. Docker | 10 | 8 |
| 7. Documentação | 14 | 8 |
| 8. Testes | 18 | 14 |
| 9. Lint | 6 | 1 |
| 10. Logging | 6 | 2 |
| **Total** | **~135** | **~98** |

> Itens restantes (~37): CI/CD, testes PostgreSQL, PKCE/tokeninfo OAuth, lint E501 legado, RBAC dinâmico, empacotamento `pip install -e .`, e melhorias P2 incrementais.

---

## Referências

- [BACKEND_STATUS.md](../BACKEND_STATUS.md) — status técnico e histórico
- [README.md](../README.md) — setup e comandos Make
- [RBAC.md](./RBAC.md) — matriz de permissões
- [init_db/README.md](../init_db/README.md) — gestão do banco
