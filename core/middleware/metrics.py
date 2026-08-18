"""Middleware de métricas básicas in-process."""

from __future__ import annotations

import time

from starlette.requests import Request

from core.configs import settings
from core.metrics import metrics


async def metrics_middleware(request: Request, call_next):
    if not settings.METRICS_ENABLED:
        return await call_next(request)

    start = time.perf_counter()
    status: int | None = None
    try:
        response = await call_next(request)
        status = response.status_code
        return response
    except Exception:
        status = None
        raise
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        metrics.record_request(duration_ms=elapsed_ms, status=status)
