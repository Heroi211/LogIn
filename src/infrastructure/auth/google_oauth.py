from __future__ import annotations

import logging
import secrets
from datetime import datetime, timedelta
from typing import Any
from urllib.parse import urlencode

import httpx

from core.configs import settings
from domain.exceptions import OAuthError

logger = logging.getLogger(__name__)

DEV_MOCK_ID_TOKEN = "dev-google-mock"
DEV_MOCK_PROFILE = {
    "sub": "google-dev-001",
    "email": "google.dev@example.com",
    "name": "Google Dev User",
}

_STATE_TTL_MINUTES = 10
_pending_oauth_states: dict[str, datetime] = {}


class GoogleOAuthService:
    AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"

    def generate_state(self) -> str:
        state = secrets.token_urlsafe(32)
        _pending_oauth_states[state] = datetime.utcnow() + timedelta(minutes=_STATE_TTL_MINUTES)
        self._purge_expired_states()
        return state

    def validate_state(self, state: str | None) -> None:
        if not state:
            raise OAuthError("Parâmetro state obrigatório.")
        self._purge_expired_states()
        expires = _pending_oauth_states.pop(state, None)
        if expires is None or expires < datetime.utcnow():
            raise OAuthError("State inválido ou expirado.")

    def _purge_expired_states(self) -> None:
        now = datetime.utcnow()
        expired = [key for key, exp in _pending_oauth_states.items() if exp < now]
        for key in expired:
            _pending_oauth_states.pop(key, None)

    def build_authorization_url(self, state: str | None = None) -> tuple[str, str]:
        oauth_state = state or self.generate_state()
        if not settings.GOOGLE_CLIENT_ID:
            if settings.is_development:
                url = f"{settings.FRONTEND_URL}/auth/google/callback?mock=1&state={oauth_state}"
                return url, oauth_state
            raise OAuthError("GOOGLE_CLIENT_ID não configurado.")

        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent",
            "state": oauth_state,
        }
        return f"{self.AUTH_URL}?{urlencode(params)}", oauth_state

    async def exchange_code(self, code: str) -> dict[str, Any]:
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            raise OAuthError("Credenciais Google não configuradas.")

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                    "grant_type": "authorization_code",
                },
            )
        if response.status_code != 200:
            logger.warning("Google token exchange falhou: %s", response.text)
            raise OAuthError("Falha ao trocar código OAuth.")

        payload = response.json()
        id_token = payload.get("id_token")
        if not id_token:
            raise OAuthError("Resposta Google sem id_token.")
        return await self.verify_id_token(id_token)

    async def verify_id_token(self, id_token: str) -> dict[str, Any]:
        if settings.is_development and id_token == DEV_MOCK_ID_TOKEN:
            return dict(DEV_MOCK_PROFILE)

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(self.TOKENINFO_URL, params={"id_token": id_token})

        if response.status_code != 200:
            raise OAuthError("id_token Google inválido.")

        profile = response.json()
        if settings.GOOGLE_CLIENT_ID and profile.get("aud") != settings.GOOGLE_CLIENT_ID:
            raise OAuthError("id_token não pertence a este client_id.")
        if not profile.get("sub") or not profile.get("email"):
            raise OAuthError("Perfil Google incompleto.")
        return profile
