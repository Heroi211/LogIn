import logging

from fastapi import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from core.configs import settings

logger = logging.getLogger(__name__)


class ValidateRequestBodyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        signup_path = f"{settings.PROJECT_VERSION}/users/signup"
        if request.method == "POST" and request.url.path == signup_path:
            try:
                body = await request.json()
                if not body:
                    logger.warning("Signup rejeitado: body vazio | path=%s", request.url.path)
                    return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={"detail": "Você não enviou os dados para cadastro"},
                    )
            except Exception:
                logger.warning("Signup rejeitado: body inválido | path=%s", request.url.path)
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"detail": "Você não enviou os dados para cadastro"},
                )
        response = await call_next(request)
        return response
