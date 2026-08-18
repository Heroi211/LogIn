# Arquitetura — LogIn Backend

Monólito modular com **Clean Architecture** e **DDD estratégico** (bounded contexts).

## Estrutura atual

```
LogIn/
├── bootstrap/                          # Composition root (DI, create_app)
├── contexts/
│   ├── identity_access/                # Bounded Context: Identity & Access
│   │   ├── domain/                     # Entidades, VOs, enums, políticas puras
│   │   ├── application/                # Use cases + ports
│   │   ├── infrastructure/             # ORM, JWT, e-mail, adapters HTTP
│   │   └── presentation/               # API FastAPI + schemas Pydantic
│   └── ticket_management/              # Bounded Context futuro (Tickets)
├── core/                               # Config, logging, bcrypt, middleware HTTP
├── shared/                             # Kernel compartilhado (utils)
└── docs/architecture/                  # Esta documentação
```

Pastas legado **removidas** (migração concluída): `api/`, `schemas/`, `services/`, `models/`, shims em `core/permissions`, `core/deps`, etc.

## Regra de dependência

```
presentation → application → domain
infrastructure → application → domain
```

**Proibido:** `domain/` importar FastAPI, SQLAlchemy ou Pydantic.

## Bounded contexts

| Contexto | Responsabilidade | Status |
|---|---|---|
| **Identity & Access** | Users, Roles, Auth, RBAC, Audit | **Ativo** |
| **Ticket Management** | Tickets, status, SLA | Planejado |

Ver [bounded_contexts.md](./bounded_contexts.md) e [identity_access/](./identity_access/README.md).

## Milestones

| Marco | Fases | Status |
|---|---|---|
| M1 — Fundação | 0 + 1 | Concluído |
| M2 — Repositórios | 2 | Concluído |
| M3 — Use Cases | 3 | Concluído |
| M4 — Domínio rico | 4 | Concluído |
| M5 — Adapters + Audit | 5 | Concluído |
| M6 — Contexto Identity | 6 | Concluído |
| M7 — Ticket Management | 7 | Pendente |
| M8 — Testes + CI | 8 | Pendente |

## Documentos

- [**SYSTEM_OVERVIEW.md**](./SYSTEM_OVERVIEW.md) — diagramas visuais (alto nível + organização)
- [identity_access/README.md](./identity_access/README.md)
- [identity_access/public_api.md](./identity_access/public_api.md)
- [identity_access/context_map.md](./identity_access/context_map.md)
- [golden_rules.md](./golden_rules.md)
- [migration_map.md](./migration_map.md) — histórico da migração
