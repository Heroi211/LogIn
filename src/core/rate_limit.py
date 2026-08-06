"""Rate limit simples in-memory para endpoints públicos sensíveis."""

from __future__ import annotations

import time
from collections import defaultdict

from fastapi import HTTPException, Request, status

_BUCKETS: dict[str, list[float]] = defaultdict(list)
_WINDOW_SECONDS = 60
_MAX_REQUESTS = 30


def rate_limit_public(request: Request) -> None:
    client = request.client.host if request.client else "unknown"
    path = request.url.path
    key = f"{client}:{path}"
    now = time.time()
    window_start = now - _WINDOW_SECONDS
    hits = [t for t in _BUCKETS[key] if t >= window_start]
    if len(hits) >= _MAX_REQUESTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Muitas requisições. Tente novamente em instantes.",
        )
    hits.append(now)
    _BUCKETS[key] = hits
