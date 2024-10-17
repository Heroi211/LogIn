from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from fastapi import status
from starlette.responses import JSONResponse

class ValidateRequestBodyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "POST" and request.url.path == "/v1/users/signup":
            try:
                body = await request.json()
                if not body:
                    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "Você não enviou os dados para cadastro"})
            except Exception:
                return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "Você não enviou os dados para cadastro"})
        response = await call_next(request)
        return response