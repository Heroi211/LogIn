"""Composition root — montagem da aplicação FastAPI."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from contexts.identity_access.infrastructure.persistence.database import engine
from contexts.identity_access.presentation.api.v1 import api as identity_api
from contexts.identity_access.presentation.api.v1.endpoints import health
from contexts.identity_access.presentation.api.v1.middleware import ValidateRequestBodyMiddleware
from core.configs import settings
from core.logging_api_request import setup_api_request_logging
from core.logging_setup import setup_root_logging
from core.middleware.correlation_id import correlation_id_middleware
from core.middleware.metrics import metrics_middleware
from core.middleware.request_record import request_record


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    setup_root_logging()
    setup_api_request_logging()

    app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION, lifespan=lifespan)
    app.middleware("http")(correlation_id_middleware)
    app.middleware("http")(metrics_middleware)
    app.middleware("http")(request_record)
    app.add_middleware(ValidateRequestBodyMiddleware)
    app.include_router(health.router)
    app.include_router(identity_api.router, prefix=settings.PROJECT_VERSION)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=settings.CORS_ORIGINS.strip() != "*",
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app
