# Template de bounded context

Copie esta estrutura ao criar um novo módulo (ex.: `billing`, `tickets`):

```
contexts/<nome>/
├── README.md
├── domain/
│   ├── entities/
│   ├── value_objects/
│   ├── exceptions.py
│   └── public_api.py          # API pública para outros contextos
├── application/
│   ├── use_cases/
│   ├── ports/
│   └── dto/
├── infrastructure/
│   └── persistence/           # ORM + repositories
└── presentation/
    ├── api/v1/endpoints/
    └── schemas/
```

## Regras

- `domain/` **não** importa FastAPI, SQLAlchemy ou Pydantic.
- Outros contextos importam apenas `domain/public_api.py`.
- Autorização: port `AuthorizationService` de `identity_access.application.ports`.
- Registrar router em `bootstrap/app.py` ou módulo de composição dedicado.

Gere um esqueleto com:

```bash
python scripts/new_context.py <nome_do_contexto>
```

Valide camadas:

```bash
make check-arch
```
