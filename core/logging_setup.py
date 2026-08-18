"""
Configuração central de logging para o processo da API.

Garante que todos os loggers emitem para stdout — necessário para docker logs.
"""
from __future__ import annotations

import logging
import sys

from core.configs import settings

_ROOT_CONFIGURED = False


def setup_root_logging() -> None:
    """Configura o logger raiz com StreamHandler para stdout (idempotente)."""
    global _ROOT_CONFIGURED
    if _ROOT_CONFIGURED:
        return

    root = logging.getLogger()

    already_has_stream = any(
        isinstance(h, logging.StreamHandler)
        and getattr(h, "stream", None) in (sys.stdout, sys.stderr)
        for h in root.handlers
    )

    if not already_has_stream:
        handler = logging.StreamHandler(sys.stdout)
        if settings.LOG_FORMAT.strip().lower() == "json":
            from core.logging_json import JsonLogFormatter

            handler.setFormatter(JsonLogFormatter())
        else:
            handler.setFormatter(
                logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
            )
        handler.setLevel(settings.get_log_level())
        root.addHandler(handler)

    root.setLevel(settings.get_log_level())
    _ROOT_CONFIGURED = True
