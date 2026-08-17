PYTHON ?= python3
PIP ?= $(PYTHON) -m pip
COMPOSE ?= docker compose

export SECRET ?= dev-secret-local-minimo-32-caracteres!!
export LOG_HTTP_REQUESTS ?= true

.PHONY: help install install-dev run up docker-up docker-down docker-fresh docker-logs clean

help:
	@echo "Alvos principais (LogIn):"
	@echo "  make install        instala dependências Python"
	@echo "  make run            API local com uvicorn (porta 8000)"
	@echo "  make up             sobe stack Docker do zero (.env + build + up)"
	@echo "  make docker-up      alias de up"
	@echo "  make docker-down    para stack Docker"
	@echo "  make docker-fresh   reset total: volumes, cache, rebuild e up"
	@echo "  make docker-logs    acompanha logs da API"
	@echo "  make clean          remove caches Python locais"

install:
	$(PIP) install -r requirements.txt

install-dev: install
	@if [ -f requirements-dev.txt ]; then $(PIP) install -r requirements-dev.txt; fi

run:
	@test -f .env || cp .env-sample .env
	$(PYTHON) -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

up: docker-up

docker-up:
	@test -f .env || cp .env-sample .env
	$(COMPOSE) up -d --build
	@echo ""
	@echo "Stack a subir."
	@echo "  API:     http://localhost:8000/docs"
	@echo "  pgAdmin: http://localhost:5050"
	@echo "  Acompanhe: make docker-logs  |  $(COMPOSE) ps"

docker-down:
	$(COMPOSE) down

docker-fresh:
	@test -f .env || cp .env-sample .env
	$(COMPOSE) down -v --remove-orphans --rmi local
	docker builder prune -af
	$(COMPOSE) build --no-cache --pull
	$(COMPOSE) up -d --force-recreate
	@echo ""
	@echo "Stack limpa e a subir do zero."
	@echo "  API:     http://localhost:8000/docs"
	@echo "  pgAdmin: http://localhost:5050"
	@echo "  Acompanhe: make docker-logs  |  $(COMPOSE) ps"

docker-logs:
	$(COMPOSE) logs -f api_login

clean:
	rm -rf build dist *.egg-info htmlcov .pytest_cache .ruff_cache .coverage coverage.xml .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
