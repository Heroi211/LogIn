from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from bootstrap.session import get_session
from contexts.identity_access.domain.entities.user import User
from contexts.identity_access.infrastructure.persistence.repositories.user_repository import (
    SqlAlchemyUserRepository,
)
from contexts.identity_access.infrastructure.security.oauth import oauth2_scheme
from core.configs import settings


class TokenData(BaseModel):
    username: str | None = None


async def resolve_user_from_token(token: str, session: AsyncSession) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível autenticar o usuario.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.ALGORITHM],
            options={"verify_aud": False},
        )
        if payload.get("type") not in (None, "access_token"):
            raise credentials_exception
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=str(username))
    except JWTError as exc:
        raise credentials_exception from exc

    users = SqlAlchemyUserRepository(session)
    user = await users.get_by_id(int(token_data.username), active_only=False)
    if user is None or not user.active:
        raise credentials_exception
    if user.blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário bloqueado.",
        )
    return user


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    return await resolve_user_from_token(token, session)
