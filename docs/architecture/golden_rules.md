# Regras de ouro — checklist de conformidade

Use este checklist em code review e antes de merge.

## Domínio (`contexts/*/domain/`)

- [ ] Zero imports de FastAPI, Starlette, SQLAlchemy, Pydantic, smtplib, jose
- [ ] Regras de negócio expressas em entidades, VOs ou funções puras (`rbac.py`)
- [ ] Enums de negócio (`RoleType`, `Permission`) vivem no domínio, não no ORM
- [ ] Sem dependência de `request`, `db`, `settings` ou env vars

## Aplicação (`contexts/*/application/`)

- [ ] Use cases orquestram ports — não executam SQL
- [ ] Input/output são DTOs da aplicação, não schemas HTTP nem modelos ORM
- [ ] Um use case = um fluxo de negócio nomeado (`RegisterUser`, `ResetPassword`)

## Infraestrutura (`contexts/*/infrastructure/`)

- [ ] Único lugar com SQLAlchemy queries e modelos ORM (após Fase 2)
- [ ] Adapters implementam ports definidos em `application/ports/`
- [ ] JWT, bcrypt, SMTP, Twilio ficam aqui — nunca em use cases como import direto

## Apresentação (`contexts/*/presentation/`)

- [ ] Endpoints finos: validar HTTP → chamar use case → mapear resposta
- [ ] Mutação sensível: `require_permission(...)` na rota; use case + `AuthorizationService` se houver múltiplos entrypoints
- [ ] Sem `db.add()`, `db.commit()` ou `select()` em endpoints (meta Fase 3)
- [ ] Schemas Pydantic só na borda HTTP — não vazam para domínio

## Geral

- [ ] Dependências apontam para dentro (regra de dependência da Clean Architecture)
- [ ] Novo papel/permissão: cadastrar em `permissions` + associar via `PUT /v1/roles/{id}/permissions` — rotas intactas (ver `docs/RBAC.md`)
- [ ] Administrator sempre autorizado via política centralizada
- [ ] Contexto Ticket não importa `models.users` — usa `UserId` / port
- [ ] Eventos de auditoria registrados nos use cases críticos (Fase 5)
- [ ] Feature nova documentada em `docs/FUNCTIONALITY_CATALOG.md`

## Comandos úteis (verificação manual)

```bash
make check-arch   # preferido — scripts/check_domain_imports.py

# Domínio limpo (manual)
rg "fastapi|sqlalchemy|pydantic" contexts/*/domain/
```

Quando Fase 8 estiver ativa, estes checks devem virar job de CI.
