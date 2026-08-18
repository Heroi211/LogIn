from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from bootstrap.session import get_session
from core.configs import settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    """Liveness — API respondendo."""
    return {
        "status": "ok",
        "app": settings.PROJECT_NAME,
        "env": settings.APP_ENV,
    }


@router.get("/health/ready")
async def readiness(session: Annotated[AsyncSession, Depends(get_session)]):
    """Readiness — API + banco acessível."""
    try:
        await session.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "unavailable", "database": "error"},
        ) from exc

    return {
        "status": "ready",
        "app": settings.PROJECT_NAME,
        "env": settings.APP_ENV,
        "database": "ok",
    }


@router.get("/metrics")
async def prometheus_metrics():
    from core.metrics import metrics

    snap = metrics.snapshot()
    lines = [
        "# HELP app_requests_total Total HTTP requests handled",
        "# TYPE app_requests_total counter",
        f"app_requests_total {snap['requests_total']}",
        "# HELP app_requests_errors_total HTTP 5xx or unhandled errors",
        "# TYPE app_requests_errors_total counter",
        f"app_requests_errors_total {snap['requests_errors']}",
        "# HELP app_latency_avg_ms Average request latency in milliseconds",
        "# TYPE app_latency_avg_ms gauge",
        f"app_latency_avg_ms {snap['latency_avg_ms']}",
    ]
    from fastapi.responses import PlainTextResponse

    return PlainTextResponse("\n".join(lines) + "\n", media_type="text/plain; version=0.0.4")
