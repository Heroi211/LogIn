# Troubleshooting

## API não sobe

1. Verifique `.env` (`DATABASE_*`, `SECRET` com 32+ chars em prod).
2. `make health` — `/health` (API) e `/health/ready` (PostgreSQL).
3. Logs: `make docker-logs` ou `make run` local.

## Login falha

| Sintoma | Causa provável |
|---------|----------------|
| `Dados incorretos` | CPF/senha errados |
| `Usuário bloqueado` | 3 logins falhos ou admin bloqueou — `POST /v1/users/{id}/unblock` |
| `Usuário inativo` | Conta desativada |
| `429` | Rate limit — aguarde 1 minuto |

Admin padrão: CPF `00000000000`, senha `Admin@123456` (`init_db/database.sql`).

## 403 em rota protegida

1. `GET /v1/users/me/permissions` — confirme se o papel tem a permissão.
2. `GET /v1/roles/{id}` — veja `permissions` do papel.
3. `PUT /v1/roles/{id}/permissions` — associe a permissão (admin).
4. Cache TTL 60s — aguarde ou reinicie a API após mudança.

## Cadastro (signup) bloqueado

`SIGNUP_PUBLIC=false` exige token com `users:create`.

## Reset de senha

- Máx. 3 solicitações / 30 dias por usuário.
- SMTP deve estar configurado (`SMTP_*` no `.env`).

## Correlation ID

Toda resposta inclui header `X-Request-ID`. Use o mesmo valor nos logs e em `audit_events.request_id`.

## Métricas

`GET /metrics` — contadores Prometheus-style (requests, erros, latência média).

## Banco desatualizado

Schema evolui em `init_db/database.sql`. Reset completo:

```bash
make docker-fresh
```
