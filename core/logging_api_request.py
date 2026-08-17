"""
Configuração do logger `api.request` (somente console via propagação ao root).

Persistência em arquivo JSONL fica desabilitada por padrão (`LOG_HTTP_REQUESTS_FILE=false`).
"""

from __future__ import annotations

_CONFIGURED = False


def setup_api_request_logging() -> None:
    """Reservado para extensão futura; access log vai apenas ao console."""
    global _CONFIGURED
    _CONFIGURED = True
