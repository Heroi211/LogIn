"""Correlation ID em toda requisição (independente de access log)."""

from __future__ import annotations

import uuid

from starlette.requests import Request


async def correlation_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
