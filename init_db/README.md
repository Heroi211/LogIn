# Banco de dados — gestão autônoma

O schema é definido **manualmente** em `database.sql` e aplicado pelo PostgreSQL na **primeira inicialização** do volume Docker (`./init_db` → `/docker-entrypoint-initdb.d/`).

**Não usamos Alembic** nem ferramentas de migration automática.

## Fonte da verdade

| Artefato | Função |
|---|---|
| `init_db/database.sql` | DDL + seeds + índices (versionado no Git) |
| `src/models/*.py` | Models ORM — devem refletir o mesmo schema |
| `docker-compose.yaml` | Monta `init_db/` no container `db_login` |

## Alterar o schema

1. Edite `database.sql` (incremente o comentário `-- Schema version:`).
2. Alinhe os models ORM em `src/models/`.
3. Recrie o volume do banco (ambiente de dev):

```bash
make docker-fresh
# ou manualmente:
docker compose down -v && docker compose up --build
```

Schema atual: **v1.4.0** (`UNIQUE` em `users.email`, tabelas sessions/api_keys/revoked_tokens).

> O script em `/docker-entrypoint-initdb.d/` **só roda quando o volume `pgdata` está vazio**.

## Produção

Aplique o SQL manualmente (psql, pgAdmin, pipeline interno) ou recrie o ambiente conforme sua política de deploy. Documente cada versão do schema no histórico do Git.

## Script legado

`createdb.py` foi **removido**. A construção da base ocorre exclusivamente via Docker + `init_db/database.sql`.
