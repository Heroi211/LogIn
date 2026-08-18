from __future__ import annotations

import os
from datetime import datetime, timedelta

from jose import JWTError, jwt
from pytz import timezone as TZ

from contexts.identity_access.application.ports.token_service import TokenService
from core.configs import settings


class JwtTokenService:
    def _timezone(self):
        return TZ(os.getenv("TIMEZONE", "UTC"))

    def create_access_token(self, user_id: int) -> str:
        timezone = self._timezone()
        expire = datetime.now(tz=timezone) + timedelta(
            minutes=float(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        payload = {
            "type": "access_token",
            "exp": expire,
            "iat": datetime.now(tz=timezone),
            "sub": str(user_id),
        }
        return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.ALGORITHM)

    def create_refresh_token(self, user_id: int) -> str:
        timezone = self._timezone()
        expire = datetime.now(tz=timezone) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        payload = {
            "type": "refresh_token",
            "exp": expire,
            "iat": datetime.now(tz=timezone),
            "sub": str(user_id),
        }
        return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.ALGORITHM)

    def verify_refresh_token(self, token: str) -> int:
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=[settings.ALGORITHM],
                options={"verify_aud": False},
            )
        except JWTError as exc:
            raise ValueError("Refresh token inválido ou expirado.") from exc

        if payload.get("type") != "refresh_token":
            raise ValueError("Token informado não é um refresh token.")
        sub = payload.get("sub")
        if sub is None:
            raise ValueError("Refresh token inválido.")
        return int(sub)
