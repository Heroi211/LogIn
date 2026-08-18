# init_db — banco de dados

**Fonte única** de schema e dados iniciais deste starter.

## Como é aplicado

O `docker-compose.yaml` monta esta pasta em `/docker-entrypoint-initdb.d/` do PostgreSQL.
O script `database.sql` roda **automaticamente no primeiro start** do volume `pgdata`.

Para reaplicar (apaga dados):

```bash
make docker-fresh
```

## Conteúdo padrão

- Tabelas: `roles`, `users`, `audit_events`
- Tabelas: `roles`, `permissions`, `role_permissions`, `users`, `audit_events`
- Papéis: User (1), Operator (2), Administrator (3), User_client (4)
- Usuário admin: CPF `00000000000`, senha `Admin@123456`, e-mail `admin@example.com`

## Customizar por projeto

Edite `database.sql` (papéis, admin, dados de exemplo).  
Não usamos migrations — você gerencia evolução do schema aqui ou via SQL manual.

## Desenvolvimento local sem Docker

Execute `database.sql` no PostgreSQL manualmente (psql ou pgAdmin).
