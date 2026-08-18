from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable

from contexts.identity_access.domain.exceptions import (
    InvalidCredentialsError,
    InvalidResetTokenError,
    PasswordResetLimitError,
    UserBlockedError,
    UserInactiveError,
)
from contexts.identity_access.domain.role_type import RoleType
from contexts.identity_access.domain.value_objects.cpf import CPF
from contexts.identity_access.domain.value_objects.email import Email
from contexts.identity_access.domain.value_objects.hashed_password import HashedPassword
from contexts.identity_access.domain.value_objects.user_id import UserId


@dataclass
class User:
    """Aggregate root: identidade autenticável e perfil de acesso."""

    id: UserId | None
    name: str
    email: Email
    cpf: CPF
    phone: str
    active: bool
    role_id: int
    password: HashedPassword
    blocked: bool = False
    failed_login_attempts: int = 0
    reset_password_token: str | None = None
    reset_password_expires: datetime | None = None
    password_reset_count: int = 0
    password_reset_window_start: datetime | None = None

    @classmethod
    def register(
        cls,
        *,
        name: str,
        email: str,
        cpf: str,
        phone: str,
        password_hash: str,
        role_id: int = RoleType.USER,
    ) -> User:
        return cls(
            id=None,
            name=name,
            email=Email(email),
            cpf=CPF(cpf),
            phone=phone,
            active=True,
            role_id=int(role_id),
            password=HashedPassword(password_hash),
        )

    def ensure_can_authenticate(self) -> None:
        if not self.active:
            raise UserInactiveError("Usuário inativo.")
        if self.blocked:
            raise UserBlockedError("Usuário bloqueado. Contate o administrador.")

    def verify_password(self, plain: str, verify: Callable[[str, str], bool]) -> None:
        self.ensure_can_authenticate()
        if not verify(plain, self.password.value):
            raise InvalidCredentialsError("Dados incorretos")

    def record_failed_login(self, max_attempts: int) -> bool:
        """Incrementa falhas de login. Retorna True se o usuário foi bloqueado agora."""
        if self.blocked:
            return False
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= max_attempts:
            self.blocked = True
            return True
        return False

    def clear_failed_login_attempts(self) -> None:
        self.failed_login_attempts = 0

    def block(self) -> None:
        self.blocked = True

    def unblock(self) -> None:
        self.blocked = False
        self.failed_login_attempts = 0

    def deactivate(self) -> None:
        self.active = False

    def assign_role(self, role_id: int) -> None:
        self.role_id = int(role_id)

    def _reset_password_reset_window_if_expired(self, now: datetime, window_days: int) -> None:
        if self.password_reset_window_start is None:
            return
        if now >= self.password_reset_window_start + timedelta(days=window_days):
            self.password_reset_window_start = None
            self.password_reset_count = 0

    def ensure_can_request_password_reset(
        self,
        *,
        max_requests: int,
        window_days: int,
        now: datetime,
    ) -> None:
        self.ensure_can_authenticate()
        self._reset_password_reset_window_if_expired(now, window_days)
        if (
            self.password_reset_window_start is not None
            and self.password_reset_count >= max_requests
        ):
            raise PasswordResetLimitError(
                f"Limite de {max_requests} recuperações de senha em {window_days} dias atingido."
            )

    def record_password_reset_request(self, *, now: datetime, window_days: int) -> None:
        self._reset_password_reset_window_if_expired(now, window_days)
        if self.password_reset_window_start is None:
            self.password_reset_window_start = now
            self.password_reset_count = 0
        self.password_reset_count += 1

    def begin_password_reset(self, token_hash: str, expires: datetime) -> None:
        self.reset_password_token = token_hash
        self.reset_password_expires = expires

    def complete_password_reset(
        self,
        token_hash: str,
        new_password_hash: str,
        *,
        now: datetime | None = None,
    ) -> None:
        moment = now or datetime.now()
        if (
            not self.reset_password_token
            or self.reset_password_token != token_hash
            or not self.reset_password_expires
            or self.reset_password_expires < moment
        ):
            raise InvalidResetTokenError("Token inválido ou expirado")
        self.password = HashedPassword(new_password_hash)
        self.reset_password_token = None
        self.reset_password_expires = None

    def update_profile(
        self,
        *,
        name: str | None = None,
        email: str | None = None,
        cpf: str | None = None,
        phone: str | None = None,
        active: bool | None = None,
    ) -> None:
        if name is not None:
            self.name = name
        if email is not None:
            self.email = Email(email)
        if cpf is not None:
            self.cpf = CPF(cpf)
        if phone is not None:
            self.phone = phone
        if active is not None:
            self.active = active
