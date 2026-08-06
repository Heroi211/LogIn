import os
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pytz import timezone as TZ

from core.configs import settings
from domain.entities.user import UserEntity
from domain.exceptions import InvalidCredentialsError
from models.users import Users
from schemas.auth_schemas import TokenResponse
from services.session_service import build_user_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.PROJECT_VERSION}/users/login", auto_error=False)

ACCESS_TOKEN_TYPE = "access_token"
REFRESH_TOKEN_TYPE = "refresh_token"


def _generate_token(type_token: str, life_time: timedelta, sub: str) -> tuple[str, str, datetime]:
    timezone_local = TZ(os.getenv("TIMEZONE", "America/Sao_Paulo"))
    expire = datetime.now(tz=timezone_local) + life_time
    jti = str(uuid.uuid4())
    payload = {
        "type": type_token,
        "exp": expire,
        "iat": datetime.now(tz=timezone_local),
        "sub": str(sub),
        "jti": jti,
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.ALGORITHM)
    expires_at = expire.astimezone(timezone.utc).replace(tzinfo=None)
    return token, jti, expires_at


def _generate_access_token(sub: str) -> tuple[str, str, datetime]:
    return _generate_token(
        type_token=ACCESS_TOKEN_TYPE,
        life_time=timedelta(minutes=float(settings.ACCESS_TOKEN_EXPIRE_MINUTES)),
        sub=sub,
    )


def _generate_refresh_token(sub: str) -> tuple[str, str, datetime]:
    return _generate_token(
        type_token=REFRESH_TOKEN_TYPE,
        life_time=timedelta(days=float(settings.REFRESH_TOKEN_EXPIRE_DAYS)),
        sub=sub,
    )


def create_token_response(user: Users | UserEntity) -> TokenResponse:
    user_id = user.id
    access_token, _, _ = _generate_access_token(sub=str(user_id))
    refresh_token, _, _ = _generate_refresh_token(sub=str(user_id))
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_seconds,
        user=build_user_session(user),
    )


def decode_token_payload_safe(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=settings.ALGORITHM,
            options={"verify_aud": False},
        )
    except JWTError as exc:
        raise InvalidCredentialsError("Token inválido ou expirado.") from exc


def decode_token_payload(token: str) -> dict:
    try:
        return decode_token_payload_safe(token)
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def decode_refresh_token_safe(refresh_token: str) -> dict:
    payload = decode_token_payload_safe(refresh_token)
    if payload.get("type") != REFRESH_TOKEN_TYPE:
        raise InvalidCredentialsError("Refresh token inválido ou expirado.")
    if payload.get("sub") is None or payload.get("jti") is None:
        raise InvalidCredentialsError("Refresh token inválido ou expirado.")
    return payload


def decode_refresh_token(refresh_token: str) -> dict:
    try:
        return decode_refresh_token_safe(refresh_token)
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def token_expires_at_from_payload(payload: dict) -> datetime:
    exp = payload.get("exp")
    if exp is None:
        return datetime.utcnow() + timedelta(days=1)
    return datetime.utcfromtimestamp(int(exp))
