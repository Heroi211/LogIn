# Mapa de migração — histórico

Migração para Clean Architecture + DDD **concluída** para o contexto Identity & Access.

## Origem → destino (referência)

| Antigo | Atual |
|---|---|
| `api/v1/` | `contexts/identity_access/presentation/api/v1/` |
| `schemas/` | `contexts/identity_access/presentation/schemas/` |
| `services/*_services.py` | `application/use_cases/` |
| `models/` | `infrastructure/persistence/models/` |
| `core/permissions.py` | `domain/permission.py` + `infrastructure/security/authorization.py` |
| `core/auth.py` | `infrastructure/security/jwt_token_service.py` |
| `core/deps.py` | `bootstrap/session.py` + `infrastructure/security/deps.py` |
| `core/audit.py` | `infrastructure/audit/sqlalchemy_audit_logger.py` |
| `core/database.py` | `infrastructure/persistence/database.py` |
| `core/generic.py` | `infrastructure/persistence/base.py` |
| `services/utils.py` | `shared/utils.py` |
| `main.py` (app inline) | `bootstrap/app.py` + `main.py` fino |

## Removido (shims legado)

As pastas/arquivos acima na raiz foram **deletados** após confirmação de que nenhum código ativo os referenciava.

## Pendente

| Item | Fase |
|---|---|
| `core/configs.py`, `core/security.py` → `shared/` ou `infrastructure/` | Opcional |
| `contexts/ticket_management/` | 7 |
| Testes + CI de camadas | 8 |
