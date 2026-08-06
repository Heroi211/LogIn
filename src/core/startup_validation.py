"""Validações de boot — falha rápida em configuração insegura."""

from __future__ import annotations

import logging

from core.configs import settings

logger = logging.getLogger(__name__)

_MIN_SECRET_LEN = 32


def validate_settings() -> None:
    if settings.is_production:
        secret = settings.JWT_SECRET.strip()
        if len(secret) < _MIN_SECRET_LEN:
            raise RuntimeError(
                f"SECRET inválido em production: mínimo {_MIN_SECRET_LEN} caracteres."
            )
        if not settings.DATABASE_NAME or not settings.DATABASE_USER:
            raise RuntimeError("DATABASE_* obrigatório em production.")
        if not settings.SESSION_COOKIE_SECURE:
            logger.warning(
                "SESSION_COOKIE_SECURE=false em production — recomendado true com HTTPS."
            )

    if settings.is_development:
        if settings.DATABASE_SERVER not in ("", "localhost", "127.0.0.1"):
            allow = settings.ALLOW_MOCK_REPOS
            if not allow:
                raise RuntimeError(
                    "ENVIRONMENT=development com DATABASE_SERVER remoto exige ALLOW_MOCK_REPOS=true."
                )
        logger.info("ENVIRONMENT=development — repositórios mock ativos.")
