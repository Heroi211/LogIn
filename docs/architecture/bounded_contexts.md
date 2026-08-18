# Bounded Contexts

## Context Map (visão atual)

```
┌─────────────────────────────────────┐
│     Identity & Access (ativo)       │
│  Users · Roles · Auth · RBAC · Audit│
└─────────────────┬───────────────────┘
                  │ publica (futuro)
                  │ UserId, RoleType, Permission
                  ▼
┌─────────────────────────────────────┐
│   Ticket Management (planejado)     │
│  Tickets · Status · Atribuição      │
└─────────────────────────────────────┘
```

Relação futura: **Customer-Supplier** — Tickets consome identidade via port/API interna; Identity não conhece Tickets.

---

## Identity & Access

**Responsabilidade:** autenticação, autorização, gestão de usuários e papéis, auditoria de segurança.

### Agregados (alvo)

| Agregado | Raiz | Notas |
|---|---|---|
| User | `User` | Referencia `RoleType` por id; senha hasheada |
| Role | `Role` | CRUD administrativo; descrição + active |

### Linguagem ubíqua

- User, Role, RoleType, Permission, Session, AuditEvent
- Ações: register, authenticate, assign_role, deactivate, reset_password

### API pública do contexto (para outros contextos)

Quando Ticket Management entrar, Identity expõe apenas:

- `UserId` (value object / int validado)
- `RoleType` / verificação de permissão via port `AuthorizationService`
- **Não** expor entidade ORM `Users` nem sessão SQLAlchemy

### Pacote no código

```
contexts/identity_access/
├── domain/
├── application/
├── infrastructure/
└── presentation/
```

---

## Ticket Management (planejado)

**Responsabilidade:** ciclo de vida de tickets, status, atribuição a operadores.

### Fronteiras

- Referencia `UserId` do contexto Identity — **nunca** importa `models.users`
- Permissões via port (`can(user_id, "tickets:assign")`) ou ACL na borda HTTP
- Próprio pacote: `contexts/ticket_management/`

### Status

Pasta placeholder em `contexts/ticket_management/README.md`. Implementação na Fase 7.
