# Visão visual do sistema — LogIn API

Diagramas de alto nível e organização interna.  
Atualize este arquivo quando a arquitetura macro mudar.

---

## 1. Sistema em alto nível

```mermaid
flowchart TB
    subgraph Clients["Clientes"]
        WEB["Frontend / SPA"]
        MOB["Mobile / outros"]
        OPS["Admin / operação"]
    end

    subgraph LogIn["LogIn API — monólito modular"]
        API["FastAPI<br/>bootstrap/app.py"]
        IA["Bounded Context<br/>identity_access"]
        TM["Bounded Context<br/>ticket_management<br/>(planejado)"]
        API --> IA
        API -.-> TM
    end

    subgraph External["Serviços externos"]
        SMTP["SMTP<br/>reset de senha"]
    end

    subgraph Data["Persistência"]
        PG[("PostgreSQL")]
        SQL["init_db/database.sql<br/>schema + seed"]
        SQL -.-> PG
    end

    WEB -->|"HTTPS + JWT"| API
    MOB -->|"HTTPS + JWT"| API
    OPS -->|"HTTPS + JWT"| API

    IA --> PG
    IA --> SMTP

    style TM fill:#f5f5f5,stroke:#999,stroke-dasharray: 5 5
```

**Papel de cada peça**

| Componente | Função |
|------------|--------|
| **FastAPI** | Porta HTTP única, middlewares, roteamento `/v1/*` |
| **identity_access** | Usuários, papéis, JWT, RBAC dinâmico, auditoria |
| **ticket_management** | Placeholder — futuros tickets/SLA |
| **PostgreSQL** | Dados + catálogo RBAC (`permissions`, `role_permissions`) |
| **SMTP** | E-mail de recuperação de senha (opcional em dev) |

---

## 2. Fluxo de uma requisição protegida

```mermaid
sequenceDiagram
    autonumber
    participant C as Cliente
    participant M as Middlewares<br/>(correlation, metrics, log)
    participant E as Endpoint<br/>presentation/
    participant R as require_permission
    participant U as get_current_user<br/>JWT
    participant A as DbAuthorizationService
    participant UC as Use Case<br/>application/
    participant D as Domain
    participant RE as Repository
    participant DB as PostgreSQL

    C->>M: HTTP + Bearer token
    M->>E: request + X-Request-ID
    E->>R: Depends(require_permission)
    R->>U: valida JWT
    U->>DB: carrega User (role_id)
    R->>A: user_has_any_permission(role_id, code)
    A->>DB: role_permissions (cache)
    alt sem permissão
        R-->>C: 403 Forbidden
    else autorizado
        E->>UC: execute(..., audit_ctx)
        UC->>D: regras de negócio
        UC->>RE: persistência
        RE->>DB: SQL
        UC-->>E: DTO
        E-->>C: JSON response
    end
```

---

## 3. Organização — Clean Architecture (camadas)

```mermaid
flowchart TB
    subgraph Presentation["presentation/ — borda HTTP"]
        EP["endpoints/"]
        SCH["schemas/ Pydantic"]
        MAP["mappers HTTP"]
    end

    subgraph Application["application/ — orquestração"]
        UC["use_cases/"]
        PORT["ports/ Protocol"]
        DTO["dto/"]
    end

    subgraph Domain["domain/ — núcleo puro"]
        ENT["entities/"]
        VO["value_objects/"]
        POL["permission, rbac, exceptions"]
    end

    subgraph Infrastructure["infrastructure/ — adapters"]
        PER["persistence/ ORM + repos"]
        SEC["security/ JWT, RBAC"]
        AUD["audit/"]
        EM["email/ SMTP"]
    end

    subgraph Bootstrap["bootstrap/ — composition root"]
        APP["app.py"]
        DEPS["deps.py DI"]
        SES["session.py"]
    end

    EP --> UC
    EP --> SEC
    UC --> PORT
    UC --> ENT
    UC --> DTO
    PER -.->|implementa| PORT
    SEC -.->|implementa| PORT
    AUD -.->|implementa| PORT
    DEPS --> UC
    DEPS --> PER
    APP --> EP

    Presentation --> Application
    Application --> Domain
    Infrastructure --> Application
    Infrastructure --> Domain

    style Domain fill:#e8f5e9,stroke:#2e7d32
    style Application fill:#e3f2fd,stroke:#1565c0
    style Infrastructure fill:#fff3e0,stroke:#ef6c00
    style Presentation fill:#fce4ec,stroke:#c2185b
```

**Regra de dependência:** setas apontam **para dentro**. `domain/` não conhece FastAPI nem SQLAlchemy.

---

## 4. Organização — pastas do repositório

```mermaid
flowchart LR
    subgraph Root["LogIn/"]
        MAIN["main.py"]
        BOOT["bootstrap/"]
        CTX["contexts/"]
        CORE["core/"]
        DOCS["docs/"]
        INIT["init_db/"]
        SCR["scripts/"]
    end

    subgraph Bootstrap["bootstrap/"]
        BAPP["app.py"]
        BDEPS["deps.py"]
        BSES["session.py"]
    end

    subgraph Contexts["contexts/"]
        IA["identity_access/"]
        TPL["_template/"]
        TM2["ticket_management/"]
    end

    subgraph IA_Layers["identity_access/"]
        DOM["domain/"]
        APP2["application/"]
        INF["infrastructure/"]
        PRE["presentation/"]
    end

    MAIN --> BOOT
    BOOT --> CTX
    IA --> IA_Layers

    style TM2 fill:#f5f5f5,stroke:#999,stroke-dasharray: 5 5
```

---

## 5. RBAC dinâmico — modelo de dados

```mermaid
erDiagram
    USERS ||--o| ROLES : "role_id"
    ROLES ||--|{ ROLE_PERMISSIONS : "tem"
    PERMISSIONS ||--|{ ROLE_PERMISSIONS : "referenciada"
    USERS ||--o{ AUDIT_EVENTS : "actor opcional"

    USERS {
        int id PK
        int role_id FK
        string cpf
        bool active
        bool blocked
    }

    ROLES {
        int id PK
        string description
        bool active
    }

    PERMISSIONS {
        int id PK
        string code UK "ex: products:read"
        string description
        string module
        bool active
    }

    ROLE_PERMISSIONS {
        int role_id PK,FK
        int permission_id PK,FK
    }

    AUDIT_EVENTS {
        bigint id PK
        string action
        string outcome
        int actor_user_id FK
    }
```

**Regras**

- Usuário **não** tem permissão direta — herda do **papel** (`role_id`).
- Matriz papel→permissão **só no banco** — não em código Python.
- Admin (`role_id = 3`): bypass em `require_permission` + todas no seed.

---

## 6. Bounded contexts — mapa atual e futuro

```mermaid
flowchart LR
    subgraph Identity["identity_access ✅ ativo"]
        AUTH["Auth / JWT"]
        USR["Users"]
        ROL["Roles"]
        RBAC["RBAC dinâmico"]
        AUD2["Audit"]
    end

    subgraph Ticket["ticket_management ⏳ planejado"]
        TKT["Tickets"]
        SLA["SLA / status"]
    end

    subgraph PublicAPI["Contrato público"]
        PAPI["domain/public_api.py<br/>UserId, Permission, RoleType"]
        AUTHZ["port AuthorizationService"]
    end

    Ticket -->|"importa apenas"| PublicAPI
    Ticket -->|"HTTP opcional"| Identity

    style Ticket fill:#f5f5f5,stroke:#999,stroke-dasharray: 5 5
```

Novo módulo: `make new-context NAME=...` → [`contexts/_template/README.md`](../../contexts/_template/README.md)

---

## 7. Módulos funcionais implementados (Identity)

```mermaid
mindmap
  root((LogIn API))
    Autenticação
      Login / Refresh
      Signup
      Forgot / Reset password
      Bloqueio por tentativas
    Usuários
      CRUD
      Block / Unblock
      me/permissions
    Papéis
      CRUD
      Associar permissões
    Permissões
      Catálogo
      Cadastro
    Operação
      Health / Ready
      Metrics
      Correlation ID
      Audit events
```

Detalhamento tabular: [`FUNCTIONALITY_CATALOG.md`](../FUNCTIONALITY_CATALOG.md)

---

## 8. Deploy local (Docker)

```mermaid
flowchart LR
    DEV["make dev"]
    DC["docker-compose"]
    API2["container: API<br/>uvicorn :8000"]
    DB2[("container: PostgreSQL")]
    INIT2["volume init<br/>init_db/database.sql"]
    PGA["pgAdmin opcional<br/>docker-compose.dev"]

    DEV --> DC
    DC --> API2
    DC --> DB2
    INIT2 -->|"1º start"| DB2
    DC -.-> PGA
    API2 --> DB2
```

Reset banco: `make docker-fresh`

---

## Referências

- Manual de fluxos: [`README.md`](../../README.md)
- Catálogo: [`FUNCTIONALITY_CATALOG.md`](../FUNCTIONALITY_CATALOG.md)
- RBAC: [`RBAC.md`](../RBAC.md)
- Regras de camada: [`golden_rules.md`](golden_rules.md)
- Prompt agentes: [`AGENT_IMPLEMENTATION_PROMPT.md`](../../AGENT_IMPLEMENTATION_PROMPT.md)
