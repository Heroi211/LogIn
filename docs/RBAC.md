# RBAC — Matriz de permissões

Papéis ativos: **Operador** (`role_id=1`) e **Administrador** (`role_id=2`).

Novos usuários cadastrados via signup recebem `role_id=1` (Operador) por padrão.

## Dependencies (`src/core/permissions.py`)

| Dependency | Papéis permitidos | Uso |
|---|---|---|
| `require_operator` | Operador, Administrador | Leitura e perfil autenticado |
| `require_admin` | Administrador | Escrita de usuários e CRUD de roles |
| `require_role(1, 2)` | Customizável | Factory para regras específicas |

Resposta quando o papel não é suficiente: **403 Forbidden**.

## Matriz role × endpoint

| Endpoint | Público | Operador | Administrador |
|---|---|---|---|
| `GET /health` | ✓ | ✓ | ✓ |
| `GET /health/live` | ✓ | ✓ | ✓ |
| `GET /health/ready` | ✓ | ✓ | ✓ |
| `POST /v1/users/signup` | ✓ | | |
| `POST /v1/users/login` | ✓ | | |
| `POST /v1/users/forgot-password/{email}` | ✓ | | |
| `POST /v1/users/reset-password` | ✓ | | |
| `GET /v1/users/logged` | | ✓ | ✓ |
| `GET /v1/users/` | | ✓ | ✓ |
| `GET /v1/users/{id}` | | ✓ | ✓ |
| `PUT /v1/users/{id}` | | | ✓ |
| `DELETE /v1/users/{id}` | | | ✓ |
| `POST /v1/roles/` | | | ✓ |
| `GET /v1/roles/` | | | ✓ |
| `GET /v1/roles/{id}` | | | ✓ |
| `PUT /v1/roles/{id}` | | | ✓ |
| `DELETE /v1/roles/{id}` | | | ✓ |

## Limitação atual — roles dinâmicas

Roles criadas via `POST /v1/roles/` **não** entram automaticamente no RBAC. Apenas `role_id=1` (Operador) e `role_id=2` (Administrador) são reconhecidos em `require_operator` / `require_admin`. Novas roles servem para catalogação futura ou extensão manual do código de permissões.

## API Keys — scopes

| Scope | Comportamento |
|---|---|
| `read` | Apenas métodos GET |
| `write` | Métodos mutantes (POST/PUT/PATCH/DELETE) |
| `admin` | RBAC normal do usuário dono da key |

Prioridade de autenticação: **API key > cookie > JWT**.

## Hierarquia

```
Administrador (2)
    └── herda tudo de Operador + gestão de usuários (escrita) e roles (CRUD)

Operador (1)
    └── leitura de usuários + perfil autenticado
```
