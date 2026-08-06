"""Mapeamento global de exceções de domínio → HTTP."""

from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from domain.exceptions import (
    AccountLockedError,
    ApiKeyInvalidError,
    DomainError,
    DuplicateEntityError,
    EntityNotFoundError,
    InvalidCredentialsError,
    MessagingError,
    OAuthError,
    OAuthLinkRequiredError,
    SessionExpiredError,
    TokenRevokedError,
    WhatsAppNotConfiguredError,
)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DuplicateEntityError)
    async def duplicate_handler(_: Request, exc: DuplicateEntityError):
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)})

    @app.exception_handler(EntityNotFoundError)
    async def not_found_handler(_: Request, exc: EntityNotFoundError):
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)})

    @app.exception_handler(InvalidCredentialsError)
    async def invalid_credentials_handler(_: Request, exc: InvalidCredentialsError):
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": str(exc)})

    @app.exception_handler(TokenRevokedError)
    async def token_revoked_handler(_: Request, exc: TokenRevokedError):
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": str(exc)})

    @app.exception_handler(AccountLockedError)
    async def account_locked_handler(_: Request, exc: AccountLockedError):
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": str(exc)})

    @app.exception_handler(OAuthLinkRequiredError)
    async def oauth_link_handler(_: Request, exc: OAuthLinkRequiredError):
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)})

    @app.exception_handler(OAuthError)
    async def oauth_handler(_: Request, exc: OAuthError):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": str(exc)},
        )

    @app.exception_handler(WhatsAppNotConfiguredError)
    async def whatsapp_not_configured(_: Request, exc: WhatsAppNotConfiguredError):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": str(exc)},
        )

    @app.exception_handler(MessagingError)
    async def messaging_handler(_: Request, exc: MessagingError):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)})

    @app.exception_handler(ApiKeyInvalidError)
    async def api_key_handler(_: Request, exc: ApiKeyInvalidError):
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": str(exc)})

    @app.exception_handler(SessionExpiredError)
    async def session_expired_handler(_: Request, exc: SessionExpiredError):
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": str(exc)})

    @app.exception_handler(DomainError)
    async def domain_handler(_: Request, exc: DomainError):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)})

    @app.exception_handler(RuntimeError)
    async def runtime_handler(_: Request, exc: RuntimeError):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": str(exc)},
        )
