"""Guarda de cadastro: público ou restrito a quem tem users:create."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from bootstrap.deps import get_authorization_service
from bootstrap.session import get_session
from contexts.identity_access.application.ports.authorization_service import AuthorizationService
from contexts.identity_access.domain.permission import Permission
from contexts.identity_access.infrastructure.security.deps import resolve_user_from_token
from core.configs import settings

_bearer_optional = HTTPBearer(auto_error=False)


async def ensure_signup_allowed(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_optional)],
    session: Annotated[AsyncSession, Depends(get_session)],
    authz: Annotated[AuthorizationService, Depends(get_authorization_service)],
) -> None:
    if settings.SIGNUP_PUBLIC:
        return

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cadastro público desabilitado. Autentique-se com permissão users:create.",
        )

    user = await resolve_user_from_token(credentials.credentials, session)
    if not await authz.user_has_any_permission(user.role_id, Permission.USERS_CREATE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não possui permissão para cadastrar usuários.",
        )
