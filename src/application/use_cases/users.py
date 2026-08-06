from __future__ import annotations

import datetime
import logging
import secrets
import smtplib
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from application.services.session_revocation import SessionRevocationService
from core.configs import settings
from core.security import get_password_hash
from domain.dtos.user_dtos import UserCreateDTO
from domain.entities.user import UserEntity
from domain.exceptions import DuplicateEntityError, EntityNotFoundError, InvalidCredentialsError
from domain.ports.repositories import (
    RevokedTokensRepositoryPort,
    SessionsRepositoryPort,
    UsersRepositoryPort,
)
from schemas import users_schemas

logger = logging.getLogger(__name__)

_MIN_PASSWORD_LEN = 8


def validate_password_strength(password: str) -> None:
    if len(password) < _MIN_PASSWORD_LEN:
        raise InvalidCredentialsError(f"Senha deve ter no mínimo {_MIN_PASSWORD_LEN} caracteres.")


@dataclass
class RegisterUserUseCase:
    users: UsersRepositoryPort

    async def execute(self, payload: users_schemas.users_create) -> UserEntity:
        validate_password_strength(payload.password)
        if await self.users.get_by_cpf(payload.cpf) or await self.users.get_by_email(payload.email):
            raise DuplicateEntityError("Usuário já cadastrado na base de dados")
        dto = UserCreateDTO(
            name=payload.name,
            email=payload.email,
            cpf=payload.cpf,
            phone=payload.phone,
            role_id=payload.role_id or 1,
        )
        return await self.users.create(dto, get_password_hash(payload.password))


@dataclass
class ListUsersUseCase:
    users: UsersRepositoryPort

    async def execute(self):
        return await self.users.list_with_role_display()


@dataclass
class GetUserUseCase:
    users: UsersRepositoryPort

    async def execute(self, user_id: int) -> UserEntity | None:
        return await self.users.get_by_id(user_id)


@dataclass
class UpdateUserUseCase:
    users: UsersRepositoryPort

    async def execute(self, user_id: int, data: dict) -> UserEntity | None:
        return await self.users.update(user_id, data)


@dataclass
class DeleteUserUseCase:
    users: UsersRepositoryPort

    async def execute(self, user_id: int):
        return await self.users.soft_delete(user_id)


@dataclass
class ForgotPasswordUseCase:
    users: UsersRepositoryPort

    async def execute(self, email: str) -> None:
        user = await self.users.get_by_email(email)
        if not user:
            return

        token = secrets.token_urlsafe(16)
        expires = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        await self.users.set_reset_token(user.id, token, expires)
        await self._send_email(email, token)

    async def _send_email(self, email: str, token: str) -> None:
        if settings.is_development:
            logger.info(
                "ENVIRONMENT=development — e-mail de reset não enviado | email=%s (token omitido)",
                email,
            )
            return

        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            logger.error("SMTP não configurado")
            return

        message = MIMEMultipart("alternative")
        message["Subject"] = "Recuperação de senha"
        message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_USER}>"
        message["To"] = email
        reset_link = f"{settings.FRONTEND_RESET_PASSWORD_URL}?email={email}&token={token}"
        message.attach(MIMEText(f"Redefina sua senha: {reset_link}", "plain"))

        try:
            if settings.SMTP_USE_SSL:
                with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                    server.sendmail(settings.SMTP_USER, email, message.as_string())
            else:
                with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                    server.starttls()
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                    server.sendmail(settings.SMTP_USER, email, message.as_string())
        except smtplib.SMTPException:
            logger.exception("Erro SMTP ao enviar e-mail de recuperação")


@dataclass
class ResetPasswordUseCase:
    users: UsersRepositoryPort
    sessions: SessionsRepositoryPort
    revoked_tokens: RevokedTokensRepositoryPort

    async def execute(self, token: str, password: str) -> UserEntity:
        validate_password_strength(password)
        user = await self.users.get_by_reset_token(token)
        if not user:
            raise EntityNotFoundError("Token inválido ou expirado.")
        if not user.reset_password_expires or user.reset_password_expires < datetime.datetime.utcnow():
            raise InvalidCredentialsError("Token inválido ou expirado.")

        updated = await self.users.reset_password(user.id, get_password_hash(password))
        if not updated:
            raise EntityNotFoundError("Usuário não encontrado.")

        if user.id is not None:
            await SessionRevocationService(self.sessions, self.revoked_tokens).revoke_all_for_user(
                user.id
            )
        return updated
