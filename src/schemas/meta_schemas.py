"""Schema de bootstrap para o frontend."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AuthMeta(BaseModel):
    login_form: str
    login_json: str
    refresh: str
    logout: str
    logged: str
    signup: str
    google_url: str
    google_callback: str
    google_link: str
    auth_priority: str
    session_cookie: str
    api_key_header: str


class OAuthMeta(BaseModel):
    google_configured: bool
    dev_mock_id_token: str | None = None


class MessagingMeta(BaseModel):
    whatsapp_send: str
    whatsapp_template: str
    whatsapp_notify_admin: str
    twilio_configured: bool
    twilio_live: bool


class MetaResponse(BaseModel):
    name: str
    api_version: str
    environment: str
    cors_origins: list[str]
    auth: AuthMeta
    oauth: OAuthMeta
    messaging: MessagingMeta
    docs: str = Field(default="/docs")
    redoc: str = Field(default="/redoc")
