# Bounded Context: Identity & Access

Contexto responsável por **identidade, autenticação, autorização e gestão de papéis**.

## Responsabilidade

| Inclui | Não inclui |
|---|---|
| Cadastro e perfil de usuários | Ciclo de vida de tickets |
| Login e tokens JWT | Notificações genéricas |
| RBAC por permissões | Regras de SLA |
| Auditoria de segurança | Domínio de clientes externos |

## Camadas

```
presentation/   → HTTP (FastAPI), schemas Pydantic, ACL
application/    → use cases, ports, DTOs
domain/         → User, Role, VOs, Permission, AuditAction
infrastructure/ → SQLAlchemy, JWT, SMTP, audit DB
```

## Agregados

| Agregado | Raiz | Invariantes |
|---|---|---|
| **User** | `domain/entities/user.py` | Inativo não autentica; token expirado invalida reset |
| **Role** | `domain/entities/role.py` | Soft delete via `active=False` |

## Use cases (application/use_cases/)

- **Users:** Register, Authenticate, List, Get, Update, Deactivate, RequestPasswordReset, ResetPassword
- **Roles:** Create, List, Get, Update, Deactivate

## Adapters (infrastructure/)

| Port | Adapter |
|---|---|
| `UserRepository` | `SqlAlchemyUserRepository` |
| `RoleRepository` | `SqlAlchemyRoleRepository` |
| `PasswordHasher` | `BcryptPasswordHasher` |
| `EmailSender` | `SmtpEmailSender` |
| `TokenService` | `JwtTokenService` |
| `AuditLogger` | `SqlAlchemyAuditLogger` |

## Auditoria integrada

Eventos registrados nos use cases críticos via `AuditLogger`:

- Login success/failure
- CRUD user/role
- Reset de senha requested/completed

## API pública para outros contextos

Ver [public_api.md](./public_api.md) e `domain/public_api.py`.

## Context map

Ver [context_map.md](./context_map.md).
