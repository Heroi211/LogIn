from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta


def hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def generate_session_token() -> str:
    return secrets.token_urlsafe(32)


def generate_api_key() -> tuple[str, str, str]:
    """Retorna (chave completa, prefixo, hash)."""
    prefix = secrets.token_hex(4)
    secret = secrets.token_urlsafe(24)
    full_key = f"ltk_{prefix}_{secret}"
    return full_key, prefix, hash_token(full_key)


def session_expires_at(days: int | None = None, hours: int | None = None) -> datetime:
    delta = timedelta(days=days or 0, hours=hours or 0)
    if delta.total_seconds() <= 0:
        delta = timedelta(days=7)
    return datetime.utcnow() + delta
