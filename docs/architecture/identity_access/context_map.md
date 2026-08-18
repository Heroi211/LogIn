# Context Map — Identity & Access

## Diagrama

```
┌──────────────────────────────────────────────────────────┐
│                  Identity & Access                        │
│  [User AR] [Role] [Permission] [AuditEvent]               │
│  Use Cases · JWT · RBAC · SMTP                            │
└─────────────────────────┬────────────────────────────────┘
                          │
              publica (Customer-Supplier)
              UserId, RoleType, Permission
                          │
                          ▼
┌──────────────────────────────────────────────────────────┐
│              Ticket Management (planejado)                  │
│  consome UserId + verificação de permissão via port       │
│  NÃO importa entidade User nem ORM                         │
└──────────────────────────────────────────────────────────┘
```

## Relações

| De | Para | Tipo | Descrição |
|---|---|---|---|
| Ticket Management | Identity & Access | **Customer-Supplier** | Tickets depende de identidade; Identity não conhece Tickets |
| Identity (presentation) | Identity (domain) | **Conformist** interno | ACL HTTP traduz schemas → use cases |
| Identity (infrastructure) | PostgreSQL | **Technical** | Persistência via SQLAlchemy |

## Shared Kernel

| Item | Local | Compartilhado com |
|---|---|---|
| `shared/utils.py` (`utcnow`) | Monólito | Todos os contextos futuros |
| `bootstrap/session.py` | Monólito | Infra compartilhada de sessão DB |

**Não** compartilhar entidades de domínio entre contextos.

## Linguagem ubíqua (Identity)

| Termo | Definição |
|---|---|
| User | Pessoa autenticável com perfil e papel |
| Role | Papel nomeado (Operador, Administrador…) |
| Permission | Capacidade `recurso:ação` |
| AuditEvent | Registro append-only de ação relevante |
| Session | Token JWT de acesso |

## Milestones deste contexto

| Marco | Status |
|---|---|
| M1 Fundação | ✅ |
| M2 Repositórios | ✅ |
| M3 Use Cases | ✅ |
| M4 Domínio rico | ✅ |
| M5 Adapters + Audit | ✅ |
| M6 Contexto formalizado | ✅ |
| M7 Fronteira Tickets | Pendente |
