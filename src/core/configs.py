# configura as variáveis de sessão com o banco de dados
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic.v1 import BaseSettings

_REPO_ROOT = Path(__file__).resolve().parents[2]
env_path = _REPO_ROOT / ".env"

load_dotenv(dotenv_path=env_path)


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


class Settings(BaseSettings):
    PROJECT_NAME: str = os.getenv("PROJECT_NAME") or "API"
    PROJECT_VERSION: str = os.getenv("PROJECT_VERSION") or "/v1"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production").strip().lower()

    DATABASE_USER: str = os.getenv("DATABASE_USER") or ""
    DATABASE_PASS: str = os.getenv("DATABASE_PASS") or ""
    DATABASE_SERVER: str = os.getenv("DATABASE_SERVER") or "localhost"
    DATABASE_PORT: str = os.getenv("DATABASE_PORT") or "5432"
    DATABASE_NAME: str = os.getenv("DATABASE_NAME") or ""

    DATABASE_URL: str = ""

    JWT_SECRET: str = os.getenv("SECRET") or ""
    ALGORITHM: str = os.getenv("ALGORITHM") or "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: str = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES") or "30"
    REFRESH_TOKEN_EXPIRE_DAYS: str = os.getenv("REFRESH_TOKEN_EXPIRE_DAYS") or "7"
    SESSION_EXPIRE_DAYS: str = os.getenv("SESSION_EXPIRE_DAYS") or "7"
    SESSION_COOKIE_NAME: str = os.getenv("SESSION_COOKIE_NAME", "session_token")
    SESSION_COOKIE_SECURE: bool = _env_bool("SESSION_COOKIE_SECURE", False)
    SESSION_COOKIE_SAMESITE: str = os.getenv("SESSION_COOKIE_SAMESITE", "lax")
    API_KEY_HEADER: str = os.getenv("API_KEY_HEADER", "X-API-Key")

    ALLOW_MOCK_REPOS: bool = _env_bool("ALLOW_MOCK_REPOS", False)

    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "")

    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID") or ""
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET") or ""
    GOOGLE_REDIRECT_URI: str = os.getenv(
        "GOOGLE_REDIRECT_URI", "http://localhost:3000/auth/google/callback"
    )

    MAX_FAILED_LOGIN_ATTEMPTS: str = os.getenv("MAX_FAILED_LOGIN_ATTEMPTS", "3")

    DEBUG: bool = _env_bool("DEBUG", False)
    LOG_HTTP_REQUESTS: bool = _env_bool("LOG_HTTP_REQUESTS", True)
    LOG_HTTP_REQUESTS_FILE: bool = _env_bool("LOG_HTTP_REQUESTS_FILE", True)
    PATH_API_REQUEST_LOGS: str = os.getenv("PATH_API_REQUEST_LOGS", "logs/api_requests")
    LOG_HTTP_REQUESTS_MAX_BYTES: int = _env_int("LOG_HTTP_REQUESTS_MAX_BYTES", 5_242_880)
    LOG_HTTP_REQUESTS_BACKUP_COUNT: int = _env_int("LOG_HTTP_REQUESTS_BACKUP_COUNT", 5)
    PATH_MAINTENANCE_REPORTS: str = os.getenv("PATH_MAINTENANCE_REPORTS", "reports/maintenance")

    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = _env_int("SMTP_PORT", 465)
    SMTP_USER: str = os.getenv("SMTP_USER") or ""
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD") or ""
    SMTP_FROM_NAME: str = os.getenv("SMTP_FROM_NAME", "Cod3Bit Dev Team")
    SMTP_USE_SSL: bool = _env_bool("SMTP_USE_SSL", True)
    FRONTEND_RESET_PASSWORD_URL: str = os.getenv(
        "FRONTEND_RESET_PASSWORD_URL", "http://127.0.0.1:3000/resetpassword"
    )

    TWILIO_ENABLED: bool = _env_bool("TWILIO_ENABLED", False)
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID") or ""
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN") or ""
    TWILIO_WHATSAPP_FROM: str = os.getenv("TWILIO_WHATSAPP_FROM") or "whatsapp:+14155238886"
    TWILIO_ADMIN_PHONE: str = os.getenv("TWILIO_ADMIN_PHONE") or ""

    class Config:
        sensitive_case = True

    def get_log_level(self) -> int:
        return logging.DEBUG if self.DEBUG else logging.INFO

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT in {"production", "prod", "prd"}

    @property
    def cors_origins_list(self) -> list[str]:
        raw = self.CORS_ORIGINS or self.FRONTEND_URL
        origins = [origin.strip() for origin in raw.split(",") if origin.strip()]
        if origins:
            return origins
        if self.is_development:
            return ["http://localhost:3000", "http://127.0.0.1:3000"]
        return []

    @property
    def access_token_expire_seconds(self) -> int:
        return int(float(self.ACCESS_TOKEN_EXPIRE_MINUTES) * 60)

    @property
    def session_expire_seconds(self) -> int:
        return int(float(self.SESSION_EXPIRE_DAYS) * 86400)

    @property
    def max_failed_login_attempts(self) -> int:
        try:
            return max(1, int(self.MAX_FAILED_LOGIN_ATTEMPTS))
        except ValueError:
            return 3

    @property
    def twilio_is_configured(self) -> bool:
        return bool(self.TWILIO_ACCOUNT_SID and self.TWILIO_AUTH_TOKEN and self.TWILIO_WHATSAPP_FROM)

    @property
    def twilio_use_live(self) -> bool:
        if self.is_development:
            return self.TWILIO_ENABLED and self.twilio_is_configured
        return self.twilio_is_configured

    @property
    def twilio_whatsapp_from_address(self) -> str:
        raw = self.TWILIO_WHATSAPP_FROM.strip()
        if raw.startswith("whatsapp:"):
            return raw
        if raw.startswith("+"):
            return f"whatsapp:{raw}"
        return f"whatsapp:+{raw}"

    def __init__(self, **values):
        super().__init__(**values)
        if os.getenv("SESSION_COOKIE_SECURE") is None and self.is_production:
            self.SESSION_COOKIE_SECURE = True
        self.DATABASE_URL = (
            f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASS}"
            f"@{self.DATABASE_SERVER}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )


settings: Settings = Settings()
