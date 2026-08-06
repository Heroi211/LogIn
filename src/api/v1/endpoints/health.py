import logging

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text

from core.configs import settings
from core.database import engine

logger = logging.getLogger(__name__)

router = APIRouter()


async def _check_database() -> bool:
    if settings.is_development:
        return True

    if engine is None:
        return False

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.warning("Health check: banco indisponível — %s", exc)
        return False


@router.get("/health", tags=["health"])
async def health_check():
    """Alias de compatibilidade — indica que o processo está vivo."""
    logger.debug("Health check solicitado")
    return {"status": "ok"}


@router.get("/health/live", tags=["health"])
async def liveness_check():
    """Liveness: o processo responde. Falha → reinício do container."""
    return {"status": "ok"}


@router.get("/health/ready", tags=["health"])
async def readiness_check():
    """Readiness: app pronta para tráfego (inclui banco). Falha → remove do load balancer."""
    if settings.is_development:
        return {"status": "ok", "database": "mocked"}

    if await _check_database():
        return {"status": "ok", "database": "connected"}

    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Serviço indisponível: banco de dados desconectado.",
    )
