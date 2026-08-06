"""Entrypoint da API na raiz do repo; adiciona ``src/`` ao ``sys.path``."""
import sys
from contextlib import asynccontextmanager
from pathlib import Path

_SRC = Path(__file__).resolve().parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1 import api
from api.v1.endpoints import health
from api.v1.middleware import ValidateRequestBodyMiddleware
from core.configs import settings
from core.exception_handlers import register_exception_handlers
from core.logging_api_request import setup_api_request_logging
from core.logging_setup import setup_root_logging
from core.middleware.request_record import request_record
from core.revoked_token_cleanup import purge_expired_revoked_tokens
from core.startup_validation import validate_settings

setup_root_logging()
setup_api_request_logging()
validate_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await purge_expired_revoked_tokens()
    yield


app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION, lifespan=lifespan)
register_exception_handlers(app)
app.middleware("http")(request_record)
app.include_router(health.router)
app.add_middleware(ValidateRequestBodyMiddleware)
app.include_router(api.router, prefix=settings.PROJECT_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", settings.API_KEY_HEADER, "X-Request-ID"],
    expose_headers=["X-Request-ID"],
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
