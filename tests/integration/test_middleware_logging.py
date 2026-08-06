"""Testes de integração — middleware de logging."""

from __future__ import annotations

import pytest
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from core.middleware.request_record import _skip_access_log, request_record


@pytest.mark.unit
@pytest.mark.parametrize(
    "path,expected",
    [
        ("/health", True),
        ("/health/live", True),
        ("/health/ready", True),
        ("/v1/users/login/json", False),
    ],
)
def test_skip_access_log_paths(path: str, expected: bool):
    assert _skip_access_log(path) is expected


async def _ok_handler(request: Request):
    return JSONResponse({"ok": True})


@pytest.mark.integration
@pytest.mark.asyncio
async def test_request_record_adds_request_id_header(monkeypatch):
    monkeypatch.setattr("core.middleware.request_record.settings.LOG_HTTP_REQUESTS", True)

    app = Starlette(routes=[Route("/v1/ping", _ok_handler)])
    app.middleware("http")(request_record)

    from starlette.testclient import TestClient as StarletteClient

    client = StarletteClient(app)
    response = client.get("/v1/ping")
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
