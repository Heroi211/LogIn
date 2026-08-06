from datetime import datetime

from pydantic import BaseModel, EmailStr


class LogoutRequest(BaseModel):
    refresh_token: str | None = None
    access_token: str | None = None


class LoginRequest(BaseModel):
    cpf: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class GoogleCallbackRequest(BaseModel):
    code: str | None = None
    id_token: str | None = None
    state: str


class GoogleLinkRequest(BaseModel):
    cpf: str
    password: str
    code: str | None = None
    id_token: str | None = None
    state: str


class GoogleAuthUrlResponse(BaseModel):
    url: str
    state: str
    mock_id_token: str | None = None


class MetaResponse(BaseModel):
    name: str
    api_version: str
    environment: str
    cors_origins: list[str]
    auth: dict
    oauth: dict
    messaging: dict
    docs: str
    redoc: str


class ApiKeyCreateRequest(BaseModel):
    name: str
    scopes: str = "read"


class ApiKeyCreatedResponse(BaseModel):
    id: int
    name: str
    scopes: str
    key: str
    expires_at: datetime | None = None


class ApiKeyListItem(BaseModel):
    id: int
    name: str
    scopes: str
    key_prefix: str
    expires_at: datetime | None = None
    created_at: datetime | None = None


class UserSession(BaseModel):
    id: int
    name: str
    email: EmailStr
    cpf: str = ""
    phone: str
    role_id: int
    role: str
    active: bool
    auth_provider: str = "local"

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserSession
