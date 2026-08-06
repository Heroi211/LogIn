
from fastapi import Cookie, Depends, HTTPException, Request, status
from fastapi.security import APIKeyHeader
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from application.container import get_container
from core.auth import ACCESS_TOKEN_TYPE, oauth2_scheme
from core.configs import settings
from core.database import Session
from infrastructure.auth.token_utils import hash_token
from infrastructure.persistence.mappers import entity_to_orm
from models.users import Users


class TokenData(BaseModel):
    username: str | None = None


api_key_header = APIKeyHeader(name=settings.API_KEY_HEADER, auto_error=False)


async def get_session():
    if settings.is_development:
        yield None
        return

    session: AsyncSession = Session()
    try:
        yield session
    finally:
        await session.close()


async def _user_from_entity(db: AsyncSession | None, user_id: int) -> Users | None:
    container = get_container(db)
    entity = await container.users.get_by_id(user_id)
    return entity_to_orm(entity) if entity else None


async def get_current_user(
    request: Request,
    db: AsyncSession | None = Depends(get_session),
    bearer_token: str | None = Depends(oauth2_scheme),
    api_key: str | None = Depends(api_key_header),
    session_token: str | None = Cookie(None, alias=settings.SESSION_COOKIE_NAME),
) -> Users:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível autenticar o usuario.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    container = get_container(db)

    if api_key:
        key_entity = await container.api_keys.verify_key(api_key)
        if key_entity:
            user = await _user_from_entity(db, key_entity.user_id)
            if user and user.active:
                request.state.auth_method = "api_key"
                request.state.api_key_scopes = key_entity.scopes
                request.state.user_id = user.id
                return user

    if session_token:
        session_entity = await container.sessions.get_by_token_hash(hash_token(session_token))
        if session_entity:
            user = await _user_from_entity(db, session_entity.user_id)
            if user and user.active:
                request.state.auth_method = "session"
                request.state.user_id = user.id
                return user

    if bearer_token:
        try:
            payload = jwt.decode(
                bearer_token,
                settings.JWT_SECRET,
                algorithms=settings.ALGORITHM,
                options={"verify_aud": False},
            )
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            if payload.get("type") != ACCESS_TOKEN_TYPE:
                raise credentials_exception

            jti = payload.get("jti")
            if jti:
                if await container.revoked_tokens.is_revoked(jti):
                    raise credentials_exception

            token_data = TokenData(username=username)
        except JWTError:
            raise credentials_exception

        user = await _user_from_entity(db, int(token_data.username))
        if user and user.active:
            request.state.auth_method = "jwt"
            request.state.user_id = user.id
            return user

    raise credentials_exception
