# Prompt para agentes — novas implementações

Copie o bloco **Prompt (copiar e colar)** abaixo ao iniciar uma tarefa de implementação neste repositório.  
Objetivo: forçar contextualização, respeito às camadas e fluxos obrigatórios.

---

## Prompt (copiar e colar)

```
Você está no repositório LogIn API — backend Identity & Access (Clean Architecture + DDD).

ANTES DE ESCREVER CÓDIGO, leia nesta ordem (obrigatório):
1. README.md (seção "Sumário" e "Guia rápido para agentes")
2. docs/FUNCTIONALITY_CATALOG.md — o que já existe; não duplicar
3. docs/RBAC.md — se envolver acesso, papéis ou novas telas/funcionalidades
4. docs/architecture/golden_rules.md — regras de camada

Arquitetura (dependência unidirecional):
  presentation → application → domain
  infrastructure → application → domain
  domain/ NÃO importa FastAPI, SQLAlchemy, Pydantic ou Starlette.

Onde implementar (não inventar outro lugar):
  - Regras de negócio puras     → contexts/identity_access/domain/
  - Use cases + auditoria       → contexts/identity_access/application/use_cases/
  - Ports (Protocol)            → contexts/identity_access/application/ports/
  - ORM + repositórios          → contexts/identity_access/infrastructure/persistence/
  - JWT, RBAC, rate limit       → contexts/identity_access/infrastructure/security/
  - Rotas HTTP (finas)          → contexts/identity_access/presentation/api/v1/endpoints/
  - Schemas Pydantic            → contexts/identity_access/presentation/schemas/
  - Injeção de dependências     → bootstrap/deps.py
  - App / middlewares           → bootstrap/app.py
  - Schema + seed SQL           → init_db/database.sql (SEM Alembic/migrations)
  - Config env                  → core/configs.py + .env-sample

RBAC dinâmico (obrigatório entender):
  - Catálogo: tabela permissions (code = "modulo:acao", ex. products:read)
  - Matriz: role_permissions (papel ↔ permissão) — NO BANCO, não no código Python
  - Usuário herda via users.role_id — NÃO existe permissão direta por usuário
  - Rotas: require_permission("modulo:acao") em infrastructure/security/authorization.py
  - Checagem DB: DbAuthorizationService (cache TTL)
  - Admin role_id=3: bypass em require_permission
  - NÃO recriar ROLE_PERMISSIONS ou matriz estática em domain/permission.py

Fluxo obrigatório para NOVA funcionalidade:
  1. Definir permissões por ação (read/create/update/delete) — formato modulo:acao
  2. Registrar em init_db/database.sql (seed) e/ou documentar POST /v1/permissions
  3. Criar use case(s) em application/use_cases/ — receber actor_role_id quando mutação
  4. Se múltiplos entrypoints (PUT, PATCH, job): AuthorizationService no use case
  5. NÃO chamar repositório direto em endpoint para mutação — sempre use case
  6. Port + repositório + mapper se persistência nova
  7. Endpoint fino + require_permission(...) por rota/ação
  8. Registrar DI em bootstrap/deps.py
  9. Router em presentation/api/v1/api.py se módulo novo
  10. Auditoria nos use cases críticos (AuditAction + record_audit)
  11. Atualizar docs/FUNCTIONALITY_CATALOG.md (obrigatório na entrega)
  12. Validar: PYTHONPATH=. python3 -c "from main import app"
  13. Validar: make check-arch (domain/ limpo)

Proibido (não faça):
  - SQLAlchemy/FastAPI/Pydantic dentro de domain/
  - db.add/commit/select em endpoints
  - Lógica de negócio pesada em endpoints ou repositórios
  - Matriz RBAC hardcoded no Python
  - Alembic, migrations, createdb.py, scripts/seed.py (legado removido)
  - Permissão por usuário individual (só via papel)
  - Esquecer de atualizar FUNCTIONALITY_CATALOG.md
  - Commits unless explicitly requested by user

Novo bounded context (módulo separado):
  - make new-context NAME=nome_modulo
  - Seguir contexts/_template/README.md
  - Integrar Identity via docs/architecture/identity_access/public_api.md
  - NÃO importar ORM de users de outro contexto

Definition of done:
  [ ] Código nas camadas corretas
  [ ] Permissões registradas (SQL e/ou catálogo API)
  [ ] require_permission em rotas protegidas
  [ ] Use case com auditoria se mutação sensível
  [ ] bootstrap/deps.py atualizado
  [ ] docs/FUNCTIONALITY_CATALOG.md atualizado
  [ ] .env-sample atualizado se nova variável
  [ ] App importa sem erro
  [ ] make check-arch passa

Agora execute a tarefa: [DESCREVA A TAREFA AQUI]
```

---

## Leitura obrigatória por tipo de tarefa

| Tarefa | Arquivos |
|--------|----------|
| Qualquer implementação | `README.md`, `docs/FUNCTIONALITY_CATALOG.md`, `docs/architecture/golden_rules.md` |
| Rotas, CRUD, módulo novo | + `docs/RBAC.md`, `bootstrap/deps.py`, endpoints existentes em `presentation/api/v1/endpoints/` |
| Permissões / papéis | + `docs/RBAC.md`, `init_db/database.sql`, `db_authorization_service.py` |
| Auth / JWT / bloqueio | + `docs/SECURITY.md`, `infrastructure/security/` |
| Novo bounded context | + `contexts/_template/README.md`, `docs/architecture/identity_access/public_api.md` |
| Bug / produção | + `docs/TROUBLESHOOTING.md` |
| Nova env var | + `.env-sample`, `core/configs.py` |

---

## Fluxo visual (nova feature)

```
┌─────────────────────────────────────────────────────────────┐
│ 1. PERMISSÕES (modulo:acao)                                   │
│    init_db/database.sql  OU  POST /v1/permissions             │
└───────────────────────────────┬─────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. DOMAIN — entidades, VOs, exceções, regras puras          │
└───────────────────────────────┬─────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. APPLICATION — port, DTO, use case (+ audit, + authz)     │
└───────────────────────────────┬─────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. INFRASTRUCTURE — ORM, repository, mapper                 │
└───────────────────────────────┬─────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. PRESENTATION — schema Pydantic, endpoint, require_permission│
└───────────────────────────────┬─────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. BOOTSTRAP — deps.py (DI), api.py (router)                │
└───────────────────────────────┬─────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. DOCS — FUNCTIONALITY_CATALOG.md (+ RBAC.md se aplicável)  │
└───────────────────────────────┬─────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────┐
│ 8. VALIDAR — import app + make check-arch                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Checklist de conformidade (preencher na entrega)

```markdown
### Conformidade arquitetural
- [ ] Li FUNCTIONALITY_CATALOG.md antes de implementar
- [ ] domain/ sem imports de FastAPI/SQLAlchemy/Pydantic
- [ ] Endpoint fino — lógica no use case
- [ ] DI registrado em bootstrap/deps.py

### RBAC (se aplicável)
- [ ] Permissões no formato modulo:acao
- [ ] require_permission em cada rota protegida
- [ ] Matriz no banco (role_permissions), não no código
- [ ] Use case valida AuthorizationService se >1 entrypoint

### Entrega
- [ ] docs/FUNCTIONALITY_CATALOG.md atualizado
- [ ] init_db/database.sql atualizado (se schema/seed)
- [ ] .env-sample atualizado (se config nova)
- [ ] `PYTHONPATH=. python3 -c "from main import app"` OK
- [ ] `make check-arch` OK
```

---

## Referência cruzada

| Documento | Caminho |
|-----------|---------|
| Manual / fluxos | [`README.md`](README.md) |
| Catálogo oficial | [`docs/FUNCTIONALITY_CATALOG.md`](docs/FUNCTIONALITY_CATALOG.md) |
| RBAC | [`docs/RBAC.md`](docs/RBAC.md) |
| Regras de camada | [`docs/architecture/golden_rules.md`](docs/architecture/golden_rules.md) |
| API entre contextos | [`docs/architecture/identity_access/public_api.md`](docs/architecture/identity_access/public_api.md) |
| Segurança | [`docs/SECURITY.md`](docs/SECURITY.md) |
| Template novo módulo | [`contexts/_template/README.md`](contexts/_template/README.md) |
