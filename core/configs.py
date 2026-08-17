#configura as varíaveis de sessão com o banco de dados
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic.v1 import BaseSettings
from sqlalchemy.ext.declarative import declarative_base

env_path = Path(".") / ".env"

load_dotenv(dotenv_path=env_path)


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


class Settings(BaseSettings):
    PROJECT_NAME = os.getenv("PROJECT_NAME")
    PROJECT_VERSION = os.getenv("PROJECT_VERSION")

    DATABASE_USER: str = os.getenv("DATABASE_USER")
    DATABASE_PASS: str = os.getenv("DATABASE_PASS")
    DATABASE_SERVER: str = os.getenv("DATABASE_SERVER")
    DATABASE_PORT: str = os.getenv("DATABASE_PORT")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME")

    DATABASE_URL = (
        f"postgresql+asyncpg://{DATABASE_USER}:{DATABASE_PASS}"
        f"@{DATABASE_SERVER}:{DATABASE_PORT}/{DATABASE_NAME}"
    )
    DB_BaseModel = declarative_base()

    JWT_SECRET = os.getenv("SECRET")
    ALGORITHM = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

    DEBUG: bool = _env_bool("DEBUG", False)
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "")
    LOG_HTTP_REQUESTS: bool = _env_bool("LOG_HTTP_REQUESTS", True)
    LOG_HTTP_REQUESTS_FILE: bool = _env_bool("LOG_HTTP_REQUESTS_FILE", False)
    PATH_API_REQUEST_LOGS: str = os.getenv("PATH_API_REQUEST_LOGS", "logs/api_requests")
    LOG_HTTP_REQUESTS_MAX_BYTES: int = int(os.getenv("LOG_HTTP_REQUESTS_MAX_BYTES", "5242880"))
    LOG_HTTP_REQUESTS_BACKUP_COUNT: int = int(os.getenv("LOG_HTTP_REQUESTS_BACKUP_COUNT", "5"))

    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://127.0.0.1:3000")

    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "465"))

    class Config:
        sensitive_case = True

    def get_log_level(self) -> int:
        level_name = (self.LOG_LEVEL or "").strip().upper()
        if level_name:
            return getattr(logging, level_name, logging.INFO)
        return logging.DEBUG if self.DEBUG else logging.INFO


settings: Settings = Settings()
