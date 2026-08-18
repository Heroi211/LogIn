PYTHON ?= python3
PIP ?= $(PYTHON) -m pip
COMPOSE ?= docker compose
COMPOSE_DEV ?= $(COMPOSE) -f docker-compose.yaml -f docker-compose.dev.yaml

export SECRET ?= dev-secret-local-minimo-32-caracteres!!
export LOG_HTTP_REQUESTS ?= true

.PHONY: help install install-dev run up dev up-dev docker-up docker-down docker-fresh docker-logs health clean check-arch new-context

help:
	@echo "Alvos principais (Backend Starter):"
	@echo "  make install        instala dependências Python"
	@echo "  make run            API local com uvicorn (porta 8000)"
	@echo "  make health         testa GET /health e /health/ready"
	@echo "  make check-arch     valida imports proibidos em domain/"
	@echo "  make new-context NAME=tickets  gera bounded context template"
	@echo "  make up             stack Docker (API + DB; init_db no 1º up)"
	@echo "  make dev            stack Docker com pgAdmin + hot reload"
	@echo "  make docker-fresh   reset total: volume DB + rebuild (reaplica init_db/)"
	@echo "  make docker-down    para stack Docker"
	@echo "  make docker-logs    acompanha logs da API"
	@echo "  make clean          remove caches Python locais"

install:
	$(PIP) install -r requirements.txt

install-dev: install
	@if [ -f requirements-dev.txt ]; then $(PIP) install -r requirements-dev.txt; fi

run:
	@test -f .env || cp .env-sample .env
	$(PYTHON) -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

health:
	@curl -sf http://localhost:8000/health | $(PYTHON) -m json.tool || (echo "API offline?" && exit 1)
	@curl -sf http://localhost:8000/health/ready | $(PYTHON) -m json.tool || (echo "DB offline?" && exit 1)

up: docker-up

docker-up:
	@test -f .env || cp .env-sample .env
	$(COMPOSE) up -d --build
	@echo ""
	@echo "Stack base (API + PostgreSQL)."
	@echo "  Banco: init_db/database.sql roda no PRIMEIRO start do volume."
	@echo "  API:     http://localhost:8000/docs"
	@echo "  Health:  http://localhost:8000/health/ready"
	@echo "  Dev+pgAdmin: make dev"
	@echo "  Reset DB:    make docker-fresh"

dev: up-dev

up-dev:
	@test -f .env || cp .env-sample .env
	$(COMPOSE_DEV) up -d --build
	@echo ""
	@echo "Stack DEV (API reload + pgAdmin)."
	@echo "  API:     http://localhost:8000/docs"
	@echo "  pgAdmin: http://localhost:5050"
	@echo "  Banco:   init_db/ no primeiro up  |  reset: make docker-fresh"

docker-down:
	$(COMPOSE) down
	@$(COMPOSE_DEV) down 2>/dev/null || true

docker-fresh:
	@test -f .env || cp .env-sample .env
	$(COMPOSE) down -v --remove-orphans --rmi local
	@$(COMPOSE_DEV) down -v --remove-orphans 2>/dev/null || true
	docker builder prune -af
	$(COMPOSE) build --no-cache --pull
	$(COMPOSE) up -d --force-recreate
	@echo ""
	@echo "Volume apagado — init_db/database.sql será reaplicado no PostgreSQL."

docker-logs:
	$(COMPOSE) logs -f api_login

clean:
	rm -rf build dist *.egg-info htmlcov .pytest_cache .ruff_cache .coverage coverage.xml .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

check-arch:
	$(PYTHON) scripts/check_domain_imports.py

new-context:
	@test -n "$(NAME)" || (echo "Uso: make new-context NAME=meu_contexto" && exit 1)
	$(PYTHON) scripts/new_context.py $(NAME)
