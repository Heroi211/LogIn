# Catálogo de funcionalidades

Referência única do que está implementado no backend **Identity & Access**.  
Atualize este arquivo sempre que adicionar módulo, permissão, rota ou use case.

---

## Convenção de permissões

Formato: `{módulo}:{ação}`

| Ação | Uso típico | HTTP |
|------|------------|------|
| `read` | Listar / visualizar | GET |
| `create` | Cadastrar | POST |
| `update` | Editar | PUT / PATCH |
| `delete` | Desativar / remover | DELETE |

Cada **ação de negócio** = uma linha no catálogo `permissions` (banco) + `require_permission(...)` na rota e, quando aplicável, no use case.

---

## Permissões cadastradas (seed inicial)

| Code | Módulo | Descrição |
|------|--------|-----------|
| `users:read` | users | Listar e visualizar usuários |
| `users:create` | users | Cadastrar usuários |
| `users:update` | users | Atualizar usuários |
| `users:delete` | users | Desativar usuários |
| `users:block` | users | Bloquear usuários |
| `users:unblock` | users | Desbloquear usuários |
| `roles:read` | roles | Listar e visualizar papéis |
| `roles:create` | roles | Cadastrar papéis |
| `roles:update` | roles | Atualizar papéis e associar permissões |
| `roles:delete` | roles | Desativar papéis |
| `permissions:read` | permissions | Listar catálogo de permissões |
| `permissions:create` | permissions | Cadastrar nova permissão no catálogo |

Fonte: `init_db/database.sql`. Novas permissões entram via `POST /v1/permissions` ou alteração do SQL + `make docker-fresh`.

---

## Papéis (roles) — seed inicial

| ID | Papel | Permissões no banco (seed) | Observação |
|----|-------|----------------------------|------------|
| 1 | User | — | Sem permissões padrão |
| 2 | Operator | `users:read` | |
| 3 | Administrator | Todas do catálogo | Bypass em `require_permission` (role_id=3) |
| 4 | User_client | — | Sem permissões padrão |

Papéis criados via API (`POST /v1/roles`) começam **sem permissões** até `PUT /v1/roles/{id}/permissions`.

---

## API — Autenticação e sessão

| Método | Rota | Permissão | Use case | Descrição |
|--------|------|-----------|----------|-----------|
| POST | `/v1/users/signup` | Pública* | `RegisterUser` | Cadastro (`SIGNUP_PUBLIC` ou `users:create`) |
| POST | `/v1/users/login` | Pública | `AuthenticateUser` | Login → access + refresh token |
| POST | `/v1/users/refresh` | Pública | — | Renova tokens (JWT refresh) |
| GET | `/v1/users/logged` | JWT | — | Dados do usuário autenticado |
| GET | `/v1/users/me/permissions` | JWT | `GetMyPermissions` | Permissões do papel (frontend) |
| POST | `/v1/users/forgot-password/{email}` | Pública | `RequestPasswordReset` | Solicita reset (rate limit) |
| POST | `/v1/users/reset-password` | Pública | `ResetPassword` | Redefine senha com token |

\* Ver `SIGNUP_PUBLIC` em `.env-sample`.

---

## API — Usuários

| Método | Rota | Permissão | Use case |
|--------|------|-----------|----------|
| GET | `/v1/users/` | `users:read` | `ListUsers` |
| GET | `/v1/users/{id}` | `users:read` | `GetUserById` |
| PUT | `/v1/users/{id}` | `users:update` | `UpdateUser` |
| DELETE | `/v1/users/{id}` | `users:delete` | `DeactivateUser` |
| POST | `/v1/users/{id}/block` | `users:block` | `BlockUser` |
| POST | `/v1/users/{id}/unblock` | `users:unblock` | `UnblockUser` |

---

## API — Papéis

| Método | Rota | Permissão | Use case |
|--------|------|-----------|----------|
| POST | `/v1/roles/` | `roles:create` | `CreateRole` |
| GET | `/v1/roles/` | `roles:read` | `ListRoles` |
| GET | `/v1/roles/{id}` | `roles:read` | `GetRoleById` |
| PUT | `/v1/roles/{id}` | `roles:update` | `UpdateRole` |
| PUT | `/v1/roles/{id}/permissions` | `roles:update` | `SetRolePermissions` |
| DELETE | `/v1/roles/{id}` | `roles:delete` | `DeactivateRole` |

Resposta de papel inclui campo `permissions` (lista de codes).

---

## API — Catálogo de permissões

| Método | Rota | Permissão | Use case |
|--------|------|-----------|----------|
| GET | `/v1/permissions/` | `permissions:read` | `ListPermissions` |
| POST | `/v1/permissions/` | `permissions:create` | `CreatePermission` |

---

## API — Health e operação

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| GET | `/health` | Pública | Liveness |
| GET | `/health/ready` | Pública | Readiness (API + PostgreSQL) |
| GET | `/metrics` | Pública | Métricas básicas (Prometheus-style) |

---

## Segurança implementada (Fase B)

| Recurso | Config / rota | Detalhe |
|---------|---------------|---------|
| Bloqueio por login | `LOGIN_MAX_FAILED_ATTEMPTS` | Auto-block + rotas block/unblock |
| Reset de senha | `PASSWORD_RESET_*` | Token SHA-256 no banco; limite 3× / 30 dias |
| Rate limit | `RATE_LIMIT_*_PER_MINUTE` | login, signup, forgot-password |
| CORS | `CORS_ORIGINS` | Configurável por env |
| Política de senha | `PASSWORD_MIN_LENGTH` | Signup e reset |

Documentação: [`SECURITY.md`](SECURITY.md).

---

## Observabilidade (Fase C)

| Recurso | Config / header | Descrição |
|---------|-----------------|-----------|
| Correlation ID | `X-Request-ID` | Request + audit + logs |
| Logs JSON | `LOG_FORMAT=json` | Saída estruturada |
| Métricas | `GET /metrics` | Contadores in-process |
| Graceful shutdown | lifespan em `bootstrap/app.py` | Dispose do pool PostgreSQL |

Documentação: [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md).

---

## Extensibilidade (Fase D)

| Ferramenta | Comando / caminho |
|------------|-------------------|
| Template de bounded context | `contexts/_template/README.md` |
| Gerar novo contexto | `make new-context NAME=meu_modulo` |
| Validar imports em domain | `make check-arch` |

---

## Identidade configurável (Fase E)

| Recurso | Config | Descrição |
|---------|--------|-----------|
| Signup público | `SIGNUP_PUBLIC=true/false` | Cadastro aberto ou exige `users:create` |
| Refresh token | `REFRESH_TOKEN_EXPIRE_DAYS` | Par login + `/v1/users/refresh` |
| RBAC dinâmico | Banco + API | Matriz papel→permissão no PostgreSQL |

---

## Checklist ao adicionar funcionalidade

1. [ ] Definir permissões `{modulo}:{acao}` e registrar em `permissions` (SQL seed ou `POST /v1/permissions`)
2. [ ] Atualizar **este catálogo** (tabelas acima)
3. [ ] Implementar use case(s) em `application/use_cases/`
4. [ ] Proteger rota(s) com `require_permission(...)`
5. [ ] Associar permissões aos papéis via `PUT /v1/roles/{id}/permissions`
6. [ ] Frontend: usar `GET /v1/users/me/permissions`
7. [ ] Auditoria nos use cases críticos (`AuditAction`)

Guia detalhado: [`RBAC.md`](RBAC.md).

---

## Template — novo módulo (ex.: products)

Ao implementar, adicione seção neste arquivo:

```markdown
## API — Produtos

| Método | Rota | Permissão | Use case |
|--------|------|-----------|----------|
| GET | `/v1/products/` | `products:read` | `ListProducts` |
| ... | ... | ... | ... |

### Permissões do módulo products

| Code | Descrição |
|------|-----------|
| `products:read` | ... |
```
