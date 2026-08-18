from __future__ import annotations

from contexts.identity_access.application.dto.audit import AuditContext
from contexts.identity_access.application.dto.users import UserRecord
from contexts.identity_access.application.exceptions import InvalidCredentialsError
from contexts.identity_access.application.mappers import user_to_record
from contexts.identity_access.application.ports.audit_logger import AuditLogger
from contexts.identity_access.application.ports.password_hasher import PasswordHasher
from contexts.identity_access.application.ports.user_repository import UserRepository
from contexts.identity_access.application.use_cases._audit import record_audit
from contexts.identity_access.domain.audit.actions import AuditAction
from contexts.identity_access.domain.exceptions import UserBlockedError, UserInactiveError


class AuthenticateUser:
    def __init__(
        self,
        users: UserRepository,
        hasher: PasswordHasher,
        audit: AuditLogger | None = None,
        *,
        max_failed_attempts: int = 3,
    ) -> None:
        self._users = users
        self._hasher = hasher
        self._audit = audit
        self._max_failed_attempts = max_failed_attempts

    async def execute(
        self,
        cpf: str,
        password: str,
        audit_ctx: AuditContext | None = None,
    ) -> UserRecord:
        user = await self._users.get_by_cpf(cpf)
        if not user:
            await record_audit(
                self._audit,
                audit_ctx,
                action=AuditAction.AUTH_LOGIN_FAILED,
                outcome="failure",
                metadata={"cpf": cpf, "reason": "user_not_found"},
            )
            raise InvalidCredentialsError("Dados incorretos")

        try:
            user.ensure_can_authenticate()
        except (UserInactiveError, UserBlockedError) as exc:
            await record_audit(
                self._audit,
                audit_ctx,
                action=AuditAction.AUTH_LOGIN_FAILED,
                outcome="failure",
                metadata={"cpf": cpf, "reason": type(exc).__name__},
            )
            raise InvalidCredentialsError(str(exc)) from exc

        if not self._hasher.verify(password, user.password.value):
            auto_blocked = user.record_failed_login(self._max_failed_attempts)
            await self._users.save(user)
            await record_audit(
                self._audit,
                audit_ctx,
                action=AuditAction.AUTH_LOGIN_FAILED,
                outcome="failure",
                metadata={"cpf": cpf, "reason": "invalid_password"},
            )
            if auto_blocked:
                await record_audit(
                    self._audit,
                    audit_ctx,
                    action=AuditAction.USER_AUTO_BLOCKED,
                    outcome="success",
                    resource_type="user",
                    resource_id=user.id.value if user.id else None,
                    metadata={"cpf": cpf, "failed_attempts": user.failed_login_attempts},
                )
            raise InvalidCredentialsError("Dados incorretos")

        if user.failed_login_attempts > 0:
            user.clear_failed_login_attempts()
            await self._users.save(user)

        await record_audit(
            self._audit,
            audit_ctx,
            action=AuditAction.AUTH_LOGIN_SUCCESS,
            outcome="success",
            resource_type="user",
            resource_id=user.id.value if user.id else None,
            actor_user_id=user.id.value if user.id else None,
        )
        return user_to_record(user)
