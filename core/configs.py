#configura as varíaveis de sessão com o banco de dados
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic.v1 import BaseSettings
from sqlalchemy.ext.declarative import declarative_base

env_path = Path(".") / ".env"

load_dotenv(dotenv_path=env_path)

VALID_APP_ENVS = frozenset({"development", "staging", "production"})


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


class Settings(BaseSettings):
    # --- Aplicação ---
    APP_ENV: str = os.getenv("APP_ENV", "development")
    PROJECT_NAME = os.getenv("PROJECT_NAME", "Gestao Tickets")
    PROJECT_VERSION = os.getenv("PROJECT_VERSION", "/v1")

    # Branding (e-mails, textos exibidos ao usuário)
    APP_BRAND_NAME: str = os.getenv("APP_BRAND_NAME", "Backend Starter")
    EMAIL_FROM_NAME: str = os.getenv("EMAIL_FROM_NAME", "")  # vazio → usa APP_BRAND_NAME
    EMAIL_SIGNATURE: str = os.getenv("EMAIL_SIGNATURE", "")  # vazio → usa APP_BRAND_NAME

    # --- Banco (SQLAlchemy + asyncpg — sem migrations) ---
    DATABASE_USER: str = os.getenv("DATABASE_USER", "")
    DATABASE_PASS: str = os.getenv("DATABASE_PASS", "")
    DATABASE_SERVER: str = os.getenv("DATABASE_SERVER", "localhost")
    DATABASE_PORT: str = os.getenv("DATABASE_PORT", "5432")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "")

    DATABASE_URL = (
        f"postgresql+asyncpg://{DATABASE_USER}:{DATABASE_PASS}"
        f"@{DATABASE_SERVER}:{DATABASE_PORT}/{DATABASE_NAME}"
    )
    DB_BaseModel = declarative_base()

    # --- JWT ---
    JWT_SECRET = os.getenv("SECRET", "")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    SIGNUP_PUBLIC: bool = _env_bool("SIGNUP_PUBLIC", True)

    # --- Logging ---
    DEBUG: bool = _env_bool("DEBUG", False)
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "")
    LOG_HTTP_REQUESTS: bool = _env_bool("LOG_HTTP_REQUESTS", True)
    LOG_HTTP_REQUESTS_FILE: bool = _env_bool("LOG_HTTP_REQUESTS_FILE", False)
    PATH_API_REQUEST_LOGS: str = os.getenv("PATH_API_REQUEST_LOGS", "logs/api_requests")
    LOG_HTTP_REQUESTS_MAX_BYTES: int = int(os.getenv("LOG_HTTP_REQUESTS_MAX_BYTES", "5242880"))
    LOG_HTTP_REQUESTS_BACKUP_COUNT: int = int(os.getenv("LOG_HTTP_REQUESTS_BACKUP_COUNT", "5"))

    # --- Frontend / SMTP ---
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://127.0.0.1:3000")
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "465"))

    # --- Segurança (Fase B) ---
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")
    LOGIN_MAX_FAILED_ATTEMPTS: int = int(os.getenv("LOGIN_MAX_FAILED_ATTEMPTS", "3"))
    PASSWORD_RESET_MAX_REQUESTS: int = int(os.getenv("PASSWORD_RESET_MAX_REQUESTS", "3"))
    PASSWORD_RESET_WINDOW_DAYS: int = int(os.getenv("PASSWORD_RESET_WINDOW_DAYS", "30"))
    PASSWORD_MIN_LENGTH: int = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
    RATE_LIMIT_LOGIN_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_LOGIN_PER_MINUTE", "10"))
    RATE_LIMIT_SIGNUP_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_SIGNUP_PER_MINUTE", "5"))
    RATE_LIMIT_FORGOT_PASSWORD_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_FORGOT_PASSWORD_PER_MINUTE", "3"))
    PERMISSION_CACHE_TTL_SECONDS: int = int(os.getenv("PERMISSION_CACHE_TTL_SECONDS", "60"))

    # --- Observabilidade (Fase C) ---
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "text")  # text | json
    METRICS_ENABLED: bool = _env_bool("METRICS_ENABLED", True)

    class Config:
        sensitive_case = True

    def get_log_level(self) -> int:
        level_name = (self.LOG_LEVEL or "").strip().upper()
        if level_name:
            return getattr(logging, level_name, logging.INFO)
        return logging.DEBUG if self.DEBUG else logging.INFO

    @property
    def email_from_display(self) -> str:
        return self.EMAIL_FROM_NAME.strip() or self.APP_BRAND_NAME

    @property
    def email_signature(self) -> str:
        return self.EMAIL_SIGNATURE.strip() or self.APP_BRAND_NAME

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    @property
    def is_staging(self) -> bool:
        return self.APP_ENV == "staging"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    def validate_app_env(self) -> None:
        if self.APP_ENV not in VALID_APP_ENVS:
            raise ValueError(
                f"APP_ENV inválido: {self.APP_ENV!r}. Use: {', '.join(sorted(VALID_APP_ENVS))}"
            )

    @property
    def cors_origins_list(self) -> list[str]:
        raw = self.CORS_ORIGINS.strip()
        if raw == "*":
            return ["*"]
        return [origin.strip() for origin in raw.split(",") if origin.strip()]


settings: Settings = Settings()
settings.validate_app_env()
