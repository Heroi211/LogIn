PYTHON ?= python3
PIP ?= $(PYTHON) -m pip
COMPOSE ?= docker compose

export PYTHONPATH := $(abspath $(CURDIR)/src):$(abspath $(CURDIR))
export ENVIRONMENT ?= development
export SECRET ?= dev-secret-for-local-make
export LOG_HTTP_REQUESTS ?= false

.PHONY: help install install-dev lint lint-fix format test test-fast coverage check \
        run docker-up docker-down docker-fresh docker-logs clean pre-commit

help:
	@echo "Alvos principais (LogIn backend):"
	@echo "  make install-dev    instala requirements + requirements-dev"
	@echo "  make lint           ruff check"
	@echo "  make lint-fix       ruff check --fix"
	@echo "  make format         ruff format"
	@echo "  make test           pytest com cobertura (mín. 70%%)"
	@echo "  make test-fast      pytest sem cobertura"
	@echo "  make coverage       relatório HTML + terminal (cobertura completa)"
	@echo "  make check          lint + test-fast"
	@echo "  make run            uvicorn local (porta 8000)"
	@echo "  make docker-up      sobe stack Docker"
	@echo "  make docker-down    para stack Docker"
	@echo "  make docker-fresh   reset total: containers, volumes, cache, rebuild limpo"
	@echo "  make docker-logs    logs da API"
	@echo "  make pre-commit     instala e roda hooks"
	@echo "  make clean          remove artefatos de teste e cache"

install:
	$(PIP) install -r requirements.txt

install-dev: install
	$(PIP) install -r requirements-dev.txt

lint:
	$(PYTHON) -m ruff check .

lint-fix:
	$(PYTHON) -m ruff check --fix .

format:
	$(PYTHON) -m ruff format .

test:
	$(PYTHON) -m pytest

test-fast:
	$(PYTHON) -m pytest -q -o addopts=

coverage:
	$(PYTHON) -m pytest --cov=src --cov-report=html --cov-report=term-missing --cov-fail-under=70
	@echo "Relatório HTML: htmlcov/index.html"

check: lint test-fast

run:
	$(PYTHON) -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

docker-up:
	@test -f .env || cp .env-sample .env
	$(COMPOSE) up -d --build

docker-down:
	$(COMPOSE) down

# Reset total: containers, volumes, imagens locais do compose, cache de build.
# Preserva bind mounts no host (./src, ./logs, ./reports, ./init_db).
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

pre-commit:
	$(PYTHON) -m pre_commit install
	$(PYTHON) -m pre_commit run --all-files

clean:
	rm -rf build dist *.egg-info htmlcov .pytest_cache .ruff_cache .coverage coverage.xml .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
