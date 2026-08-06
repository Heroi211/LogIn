# Guia completo — LogIn Backend

Documento passo a passo para subir o projeto do zero, acessar cada painel e testar cada funcionalidade.

**Última atualização:** Ago/2026  
**Relacionados:** [README.md](../README.md) · [BACKEND_STATUS.md](../BACKEND_STATUS.md) · [RBAC.md](./RBAC.md)

---

## Índice

1. [Pré-requisitos](#1-pré-requisitos)
2. [Do zero — modo local (sem Docker)](#2-do-zero--modo-local-sem-docker)
3. [Do zero — stack Docker (PostgreSQL)](#3-do-zero--stack-docker-postgresql)
4. [Painéis e URLs de acesso](#4-painéis-e-urls-de-acesso)
5. [Credenciais e ambientes](#5-credenciais-e-ambientes)
6. [Testar manualmente (curl / Swagger)](#6-testar-manualmente-curl--swagger)
7. [Testes automatizados](#7-testes-automatizados)
8. [Logs e relatórios](#8-logs-e-relatórios)
9. [Problemas comuns](#9-problemas-comuns)

---

## 1. Pré-requisitos

| Ferramenta | Versão mínima | Para quê |
|------------|---------------|----------|
| Python | 3.10+ | API local e testes |
| pip / venv | — | Dependências Python |
| Docker | recente | Stack completa (API + Postgres + pgAdmin) |
| Docker Compose | v2 (`docker compose`) | Orquestração |
| Make | opcional | Atalhos (`make run`, `make coverage`, etc.) |
| curl ou HTTPie | opcional | Testes manuais via terminal |
| Navegador | — | Swagger, ReDoc, pgAdmin, cobertura HTML |

Clone o repositório e entre na pasta:

```bash
cd LogIn
```

---

## 2. Do zero — modo local (sem Docker)

Ideal para desenvolvimento rápido: **não usa PostgreSQL**. Dados ficam em memória (mocks).

### 2.1 Configurar ambiente

```bash
cp .env-sample .env
```

Edite `.env` com estes valores mínimos:

```env
ENVIRONMENT=development
SECRET=dev-secret-local-minimo-32-caracteres!!
FRONTEND_URL=http://localhost:3000
LOG_HTTP_REQUESTS=true
```

> Em `development`, o Makefile já exporta `SECRET` e `ENVIRONMENT` se você usar `make run` / `make test`. Para `python main.py` direto, o `.env` é obrigatório.

### 2.2 Instalar dependências

```bash
make install-dev
# equivalente:
# python3 -m pip install -r requirements.txt -r requirements-dev.txt
```

Recomendado: usar virtualenv antes do install.

### 2.3 Subir a API

```bash
make run
```

API disponível em **http://localhost:8000**.

### 2.4 Verificar que subiu

```bash
curl -s http://localhost:8000/health | jq .
curl -s http://localhost:8000/health/ready | jq .
curl -s http://localhost:8000/v1/meta | jq .
```

Respostas esperadas:

- `/health` e `/health/live` → `200` com `{"status":"ok"}`
- `/health/ready` → `200` com `"database": "mocked"` em development
- `/v1/meta` → JSON com URLs de auth, ambiente `development`, `dev_mock_id_token`

---

## 3. Do zero — stack Docker (PostgreSQL)

Sobe **PostgreSQL**, **API** e **pgAdmin**. Schema aplicado automaticamente via `init_db/database.sql` (v1.4.0).

### 3.1 Configurar `.env`

```bash
cp .env-sample .env
```

Ajuste **obrigatoriamente** para production:

```env
ENVIRONMENT=production
SECRET=coloque-uma-chave-secreta-com-pelo-menos-32-caracteres
DATABASE_USER=hero
DATABASE_PASS=changeme
DATABASE_SERVER=db_login
DATABASE_PORT=5432
DATABASE_NAME=login
```

> O container `api_login` força `DATABASE_SERVER=db_login` via `docker-compose.yaml`.  
> Sem `SECRET` com 32+ caracteres, a API **não inicia** em production.

### 3.2 Subir stack limpa

```bash
make docker-fresh
```

Esse comando:

1. Para containers e remove volumes
2. Limpa cache de build Docker
3. Rebuild completo das imagens
4. Sobe tudo do zero (`up -d`)

Alternativa mais leve (sem reset total):

```bash
make docker-up
```

### 3.3 Verificar containers

```bash
docker compose ps
make docker-logs          # logs da API (Ctrl+C para sair)
docker compose logs db_login
```

Aguarde o healthcheck do Postgres (`healthy`) antes de testar a API.

### 3.4 Verificar API conectada ao banco

```bash
curl -s http://localhost:8000/health/ready
```

Esperado: `200` com `"database": "connected"`.  
Se `503`: banco ainda subindo ou credenciais incorretas no `.env`.

### 3.5 Primeiro usuário (Docker / production)

O SQL seed cria apenas **roles** (Operador=1, Administrador=2). **Não há usuários** pré-cadastrados.

Cadastre o primeiro admin via signup + update de role, ou use Swagger:

```bash
# 1. Signup
curl -s -X POST http://localhost:8000/v1/users/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Admin Inicial",
    "email": "admin@example.com",
    "cpf": "33333333333",
    "phone": "11999990003",
    "password": "admin1234"
  }'

# 2. Login
curl -s -X POST http://localhost:8000/v1/users/login/json \
  -H "Content-Type: application/json" \
  -d '{"cpf":"33333333333","password":"admin1234"}'

# 3. Promover a admin (use o access_token do passo 2)
curl -s -X PUT http://localhost:8000/v1/users/1 \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role_id": 2}'
```

> Em development local, pule este passo — use as credenciais mock da seção 5.

---

## 4. Painéis e URLs de acesso

### 4.1 API e documentação interativa

| Painel | URL | Autenticação | Descrição |
|--------|-----|--------------|-----------|
| **Swagger UI** | http://localhost:8000/docs | Botão "Authorize" para JWT | Testar todos os endpoints com formulários |
| **ReDoc** | http://localhost:8000/redoc | — | Documentação legível |
| **OpenAPI JSON** | http://localhost:8000/openapi.json | — | Schema bruto para ferramentas |

**Como usar o Swagger:**

1. Abra http://localhost:8000/docs
2. Teste endpoints públicos (`/health`, `/v1/meta`, `/v1/users/login/json`)
3. Faça login JSON → copie `access_token`
4. Clique **Authorize** → cole `Bearer SEU_TOKEN` (ou só o token, conforme o campo)
5. Teste rotas protegidas (`/v1/users/logged`, `/v1/roles/`, etc.)

### 4.2 pgAdmin (somente Docker)

| Painel | URL | Login padrão (.env-sample) |
|--------|-----|----------------------------|
| **pgAdmin** | http://localhost:5050 | E-mail: `admin@example.com` · Senha: `changeme` |

**Conectar ao PostgreSQL no pgAdmin:**

1. Acesse http://localhost:5050 e faça login
2. Clique direito em **Servers** → **Register** → **Server**
3. Aba **General:** Name = `LogIn DB`
4. Aba **Connection:**
   - Host: `db_login` (nome do serviço na rede Docker — **não** use `localhost` de dentro do pgAdmin)
   - Port: `5432`
   - Username: `hero` (ou `DATABASE_USER` do `.env`)
   - Password: `changeme` (ou `DATABASE_PASS`)
   - Database: `login`
5. Save

> Se conectar do **host** (DBeaver, psql local): Host = `localhost`, Port = `5432`.

```bash
# psql direto no container
docker exec -it database_login psql -U hero -d login
```

### 4.3 Cobertura de testes (HTML)

| Painel | Como gerar | URL / caminho |
|--------|------------|---------------|
| **Relatório de cobertura** | `make coverage` | Abrir `htmlcov/index.html` no navegador |

```bash
make coverage
xdg-open htmlcov/index.html    # Linux
# ou abra o arquivo manualmente no navegador
```

### 4.4 Logs da aplicação

| Recurso | Caminho / comando | Quando existe |
|---------|-------------------|---------------|
| **Stdout da API (Docker)** | `make docker-logs` | Stack Docker |
| **Access log JSONL** | `logs/api_requests/access.jsonl` | `LOG_HTTP_REQUESTS_FILE=true` |
| **Relatório de latência** | `python3 src/scripts/maintenance/latency_report.py` | Gera CSV em `reports/maintenance/` |

### 4.5 Resumo rápido de portas

| Porta | Serviço |
|-------|---------|
| **8000** | API FastAPI |
| **5432** | PostgreSQL |
| **5050** | pgAdmin |

---

## 5. Credenciais e ambientes

### 5.1 Modos de operação

| `ENVIRONMENT` | Banco | Repositórios | Uso |
|---------------|-------|--------------|-----|
| `development` | Não exigido | Mocks in-memory | Local, testes, protótipo |
| `production` | PostgreSQL obrigatório | SQLAlchemy | Docker, deploy real |

### 5.2 Usuários mock (somente `development`)

| Papel | CPF | Senha | E-mail |
|-------|-----|-------|--------|
| Operador | `11111111111` | `dev123` | operador@example.com |
| Administrador | `22222222222` | `admin123` | admin@example.com |

### 5.3 OAuth Google mock (somente `development`)

| Item | Valor |
|------|-------|
| Token mock | `dev-google-mock` |
| Fluxo | `GET /v1/auth/google/url` → copiar `state` → `POST /v1/auth/google/callback` |

Em **production**, `id_token` direto no callback é **rejeitado** — use fluxo com `code` e credenciais Google reais.

### 5.4 Papéis RBAC

| role_id | Nome | Permissões resumidas |
|---------|------|----------------------|
| 1 | Operador | Leitura de users, perfil próprio |
| 2 | Administrador | CRUD users/roles, API keys, messaging |

Matriz completa: [docs/RBAC.md](./RBAC.md).

---

## 6. Testar manualmente (curl / Swagger)

Base URL: `http://localhost:8000`  
Substitua `TOKEN` pelo `access_token` obtido no login.

### 6.1 Health e meta

```bash
curl http://localhost:8000/health
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready
curl http://localhost:8000/v1/meta
```

### 6.2 Autenticação — login, refresh, logout

```bash
# Login JSON (recomendado)
curl -s -X POST http://localhost:8000/v1/users/login/json \
  -H "Content-Type: application/json" \
  -d '{"cpf":"22222222222","password":"admin123"}' | jq .

# Perfil autenticado
curl -s http://localhost:8000/v1/users/logged \
  -H "Authorization: Bearer TOKEN" | jq .

# Refresh
curl -s -X POST http://localhost:8000/v1/users/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"SEU_REFRESH_TOKEN"}' | jq .

# Logout (cookie + tokens opcionais no body)
curl -s -X POST http://localhost:8000/v1/users/logout \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"SEU_REFRESH_TOKEN","access_token":"TOKEN"}' \
  -c cookies.txt -b cookies.txt
```

**Login inválido** → `401` (não `400`).  
**3 tentativas erradas** → conta bloqueada (`active=false`) → `403`.

### 6.3 Signup e CRUD de usuários

```bash
# Cadastro (público; rate limit ~30 req/min por IP)
curl -s -X POST http://localhost:8000/v1/users/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name":"Novo Usuario",
    "email":"novo@example.com",
    "cpf":"44444444444",
    "phone":"11988887777",
    "password":"senha1234"
  }'

# Listar (operador ou admin) → 200
curl -s http://localhost:8000/v1/users/ -H "Authorization: Bearer TOKEN"

# Buscar por ID
curl -s http://localhost:8000/v1/users/1 -H "Authorization: Bearer TOKEN"

# Atualizar (admin)
curl -s -X PUT http://localhost:8000/v1/users/1 \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"active":true,"role_id":2}'

# Soft delete (admin) → 204
curl -s -o /dev/null -w "%{http_code}\n" -X DELETE http://localhost:8000/v1/users/3 \
  -H "Authorization: Bearer TOKEN"
```

**E-mail/CPF duplicado** no signup → `409`.

### 6.4 Roles (admin)

```bash
curl -s http://localhost:8000/v1/roles/ -H "Authorization: Bearer TOKEN_ADMIN"

curl -s -X POST http://localhost:8000/v1/roles/ \
  -H "Authorization: Bearer TOKEN_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{"description":"Supervisor","active":true}'

curl -s -X PUT http://localhost:8000/v1/roles/3 \
  -H "Authorization: Bearer TOKEN_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{"description":"Supervisor Atualizado"}'

curl -s -o /dev/null -w "%{http_code}\n" -X DELETE http://localhost:8000/v1/roles/3 \
  -H "Authorization: Bearer TOKEN_ADMIN"
```

### 6.5 OAuth Google (development)

```bash
# 1. Obter URL e state
STATE=$(curl -s http://localhost:8000/v1/auth/google/url | jq -r .state)

# 2. Callback com mock
curl -s -X POST http://localhost:8000/v1/auth/google/callback \
  -H "Content-Type: application/json" \
  -d "{\"id_token\":\"dev-google-mock\",\"state\":\"$STATE\"}" | jq .

# 3. Vincular conta local existente (CPF + senha)
STATE=$(curl -s http://localhost:8000/v1/auth/google/url | jq -r .state)
curl -s -X POST http://localhost:8000/v1/auth/google/link \
  -H "Content-Type: application/json" \
  -d "{
    \"cpf\":\"11111111111\",
    \"password\":\"dev123\",
    \"id_token\":\"dev-google-mock\",
    \"state\":\"$STATE\"
  }"
```

**State inválido/ausente** → `503`.

### 6.6 API Keys (admin)

```bash
# Criar (a key completa só aparece uma vez!)
curl -s -X POST http://localhost:8000/v1/api-keys/ \
  -H "Authorization: Bearer TOKEN_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{"name":"integracao-teste","scopes":"read"}'

# Listar
curl -s http://localhost:8000/v1/api-keys/ \
  -H "Authorization: Bearer TOKEN_ADMIN"

# Usar API Key (prioridade sobre JWT)
curl -s http://localhost:8000/v1/users/logged \
  -H "X-API-Key: ltk_PREFIXO_SECRETO"

# Revogar → 204
curl -s -o /dev/null -w "%{http_code}\n" -X DELETE http://localhost:8000/v1/api-keys/1 \
  -H "Authorization: Bearer TOKEN_ADMIN"
```

**Scopes:** `read` = só GET · `write` = mutações · `admin` = RBAC normal do dono.

### 6.7 Sessão por cookie

O login seta cookie `session_token` (HttpOnly). Teste com curl guardando cookies:

```bash
curl -s -X POST http://localhost:8000/v1/users/login/json \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"cpf":"22222222222","password":"admin123"}'

curl -s http://localhost:8000/v1/users/logged -b cookies.txt
```

Prioridade de auth: **API Key > Cookie > JWT Bearer**.

### 6.8 Recuperação de senha

Requer SMTP configurado (`SMTP_USER`, `SMTP_PASSWORD`). Sem SMTP → `503`.

```bash
# Sempre retorna 200 (sem revelar se e-mail existe)
curl -s -X POST http://localhost:8000/v1/users/forgot-password/admin@example.com

# Reset (token recebido por e-mail — em dev, verifique logs)
curl -s -X POST http://localhost:8000/v1/users/reset-password \
  -H "Content-Type: application/json" \
  -d '{"token":"TOKEN_DO_EMAIL","password":"novasenha123"}'
```

### 6.9 WhatsApp / Twilio (admin)

Em `development` com `TWILIO_ENABLED=false`: respostas **mock** (sem envio real).

```bash
curl -s -X POST http://localhost:8000/v1/messaging/whatsapp \
  -H "Authorization: Bearer TOKEN_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{"to":"5511999990000","body":"Teste"}'

curl -s -X POST http://localhost:8000/v1/messaging/whatsapp/template \
  -H "Authorization: Bearer TOKEN_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{"to":"5511999990000","content_sid":"HX...","variables":{"1":"Nome"}}'

curl -s http://localhost:8000/v1/messaging/phone/5511999990000/lookup \
  -H "Authorization: Bearer TOKEN_ADMIN"
```

---

## 7. Testes automatizados

### 7.1 Comandos

```bash
make install-dev      # primeira vez
make test-fast        # rápido, sem cobertura
make test             # pytest + cobertura mínima 70%
make coverage         # relatório terminal + HTML
make check            # lint + test-fast
```

Os testes rodam com `ENVIRONMENT=development` (mocks) — **não precisam de Docker**.

### 7.2 Mapa: o que cada suite testa

| Arquivo | Tipo | O que valida |
|---------|------|--------------|
| `tests/integration/test_health.py` | Integração | `/health`, `/health/live`, `/health/ready` |
| `tests/integration/test_users_auth.py` | Integração | Login, refresh, logout, signup |
| `tests/integration/test_users_crud.py` | Integração | PUT users |
| `tests/integration/test_users_extra.py` | Integração | Listagem, GET por ID |
| `tests/integration/test_roles.py` | Integração | Listagem roles |
| `tests/integration/test_roles_crud.py` | Integração | PUT/DELETE roles |
| `tests/integration/test_auth_google.py` | Integração | OAuth mock, state, link |
| `tests/integration/test_api_keys.py` | Integração | CRUD API keys |
| `tests/integration/test_api_key_scopes.py` | Integração | Scopes read/write/admin |
| `tests/integration/test_auth_methods.py` | Integração | Cookie, API key, prioridade |
| `tests/integration/test_reset_password.py` | Integração | Fluxo reset senha |
| `tests/integration/test_messaging.py` | Integração | Envio WhatsApp mock |
| `tests/integration/test_messaging_template.py` | Integração | Template WhatsApp |
| `tests/integration/test_middleware_signup.py` | Integração | Validação body signup |
| `tests/integration/test_middleware_logging.py` | Integração | Middleware access log |
| `tests/unit/test_security.py` | Unitário | Hash/verify senha |
| `tests/unit/test_auth.py` | Unitário | JWT encode/decode |
| `tests/unit/test_login_lockout.py` | Unitário | Bloqueio por tentativas |
| `tests/unit/test_lockout_revocation.py` | Unitário | Revogação no lockout |
| `tests/unit/test_domain_configs.py` | Unitário | Settings / configs |
| `tests/unit/test_phone_utils.py` | Unitário | Normalização telefone |
| `tests/unit/test_messaging_use_cases.py` | Unitário | Use cases messaging |

### 7.3 Rodar testes específicos

```bash
# Um arquivo
python3 -m pytest tests/integration/test_auth_google.py -v

# Por marcador
python3 -m pytest -m integration -v
python3 -m pytest -m unit -v

# Um teste pelo nome
python3 -m pytest tests/integration/test_health.py::test_health_live -v
```

### 7.4 Resultado esperado

```
48 passed
cobertura total ~87% (mínimo exigido: 70%)
```

Relatório HTML: `htmlcov/index.html`.

---

## 8. Logs e relatórios

### 8.1 Habilitar access log

No `.env`:

```env
LOG_HTTP_REQUESTS=true
LOG_HTTP_REQUESTS_FILE=true
PATH_API_REQUEST_LOGS=logs/api_requests
```

Cada request gera linha JSON em `logs/api_requests/access.jsonl` com `request_id`, `duration_ms`, `auth_method`, `user_id`.

### 8.2 Relatório de latência

```bash
python3 src/scripts/maintenance/latency_report.py
python3 src/scripts/maintenance/latency_report.py --slo-ms 300
```

Saída: CSV em `reports/maintenance/latency_summary_*.csv`.

### 8.3 Docker

```bash
make docker-logs              # API
docker compose logs -f db_login
docker compose logs -f pgadmin_db
```

---

## 9. Problemas comuns

| Sintoma | Causa provável | Solução |
|---------|----------------|---------|
| API não inicia em Docker | `SECRET` curto ou vazio | `.env`: `SECRET` com ≥ 32 caracteres |
| `/health/ready` → 503 | Postgres ainda subindo | Aguarde; `docker compose ps` → `healthy` |
| Login mock → 401 | `ENVIRONMENT` não é `development` | `.env`: `ENVIRONMENT=development` ou use signup no Docker |
| OAuth callback → 503 | `state` inválido/expirado | Chame `/v1/auth/google/url` de novo e use o `state` retornado |
| `make docker-fresh` lento | Rebuild `--no-cache` | Normal na primeira vez; use `make docker-up` no dia a dia |
| pgAdmin não conecta | Host errado | Dentro do pgAdmin: host `db_login`, não `localhost` |
| Forgot-password → 503 | SMTP não configurado | Preencha `SMTP_*` ou teste só em dev com logs |
| Porta 8000 em uso | Outro processo | `lsof -i :8000` e pare o processo ou mude a porta |
| Testes falham após editar mocks | Store compartilhado | Rode de novo; `conftest.py` reseta entre testes |

### Reset total (Docker)

```bash
make docker-fresh
```

### Reset local (cache de testes)

```bash
make clean
```

---

## Referência rápida — todos os endpoints

| Método | Endpoint | Auth | Quem |
|--------|----------|------|------|
| GET | `/health` | — | Todos |
| GET | `/health/live` | — | Todos |
| GET | `/health/ready` | — | Todos |
| GET | `/v1/meta` | — | Todos |
| POST | `/v1/users/signup` | — | Público |
| POST | `/v1/users/login` | — | Público (form OAuth2) |
| POST | `/v1/users/login/json` | — | Público |
| POST | `/v1/users/refresh` | — | Refresh token |
| POST | `/v1/users/logout` | JWT/cookie | Autenticado |
| GET | `/v1/users/logged` | JWT/cookie/key | Operador+ |
| GET | `/v1/users/` | JWT/cookie/key | Operador+ |
| GET | `/v1/users/{id}` | JWT/cookie/key | Operador+ |
| PUT | `/v1/users/{id}` | JWT/cookie/key | Admin |
| DELETE | `/v1/users/{id}` | JWT/cookie/key | Admin |
| POST | `/v1/users/forgot-password/{email}` | — | Público |
| POST | `/v1/users/reset-password` | — | Público |
| POST | `/v1/roles/` | JWT/cookie/key | Admin |
| GET | `/v1/roles/` | JWT/cookie/key | Admin |
| GET | `/v1/roles/{id}` | JWT/cookie/key | Admin |
| PUT | `/v1/roles/{id}` | JWT/cookie/key | Admin |
| DELETE | `/v1/roles/{id}` | JWT/cookie/key | Admin |
| GET | `/v1/auth/google/url` | — | Público |
| POST | `/v1/auth/google/callback` | — | Público |
| POST | `/v1/auth/google/link` | — | Público (CPF+senha) |
| POST | `/v1/api-keys/` | JWT/cookie/key | Admin |
| GET | `/v1/api-keys/` | JWT/cookie/key | Admin |
| DELETE | `/v1/api-keys/{id}` | JWT/cookie/key | Admin |
| POST | `/v1/messaging/whatsapp` | JWT/cookie/key | Admin |
| POST | `/v1/messaging/whatsapp/template` | JWT/cookie/key | Admin |
| GET | `/v1/messaging/whatsapp/{sid}` | JWT/cookie/key | Admin |
| POST | `/v1/messaging/whatsapp/notify-admin` | JWT/cookie/key | Admin |
| GET | `/v1/messaging/phone/{phone}/lookup` | JWT/cookie/key | Admin |

---

## Checklist “está tudo funcionando?”

- [ ] `make run` ou `make docker-fresh` sem erro
- [ ] http://localhost:8000/docs abre
- [ ] `GET /health/ready` → 200
- [ ] Login admin mock (dev) ou signup (Docker) funciona
- [ ] `GET /v1/users/logged` com token retorna perfil
- [ ] Operador recebe 403 em `POST /v1/roles/`
- [ ] Admin cria API key e usa `X-API-Key`
- [ ] OAuth mock (dev) com `state` funciona
- [ ] `make coverage` → 48 passed, ≥ 70%
- [ ] pgAdmin conecta ao banco (Docker)
- [ ] `logs/api_requests/access.jsonl` recebe linhas (se habilitado)
