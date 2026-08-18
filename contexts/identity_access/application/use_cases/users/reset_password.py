from __future__ import annotations

from contexts.identity_access.application.dto.audit import AuditContext
from contexts.identity_access.application.exceptions import InvalidResetTokenError, WeakPasswordError
from contexts.identity_access.application.ports.audit_logger import AuditLogger
from contexts.identity_access.application.ports.password_hasher import PasswordHasher
from contexts.identity_access.application.ports.user_repository import UserRepository
from contexts.identity_access.application.use_cases._audit import record_audit
from contexts.identity_access.domain.audit.actions import AuditAction
from contexts.identity_access.domain.exceptions import InvalidResetTokenError as DomainInvalidResetToken
from contexts.identity_access.domain.exceptions import WeakPasswordError as DomainWeakPasswordError
from contexts.identity_access.domain.services.password_policy import validate_password
from contexts.identity_access.infrastructure.security.token_hash import hash_reset_token


class ResetPassword:
    def __init__(
        self,
        users: UserRepository,
        hasher: PasswordHasher,
        audit: AuditLogger | None = None,
        *,
        password_min_length: int = 8,
    ) -> None:
        self._users = users
        self._hasher = hasher
        self._audit = audit
        self._password_min_length = password_min_length

    async def execute(
        self,
        token: str,
        new_password: str,
        audit_ctx: AuditContext | None = None,
    ) -> None:
        try:
            validate_password(new_password, min_length=self._password_min_length)
        except DomainWeakPasswordError as exc:
            raise WeakPasswordError(str(exc)) from exc

        user = await self._users.get_by_reset_token(token)
        if not user:
            await record_audit(
                self._audit,
                audit_ctx,
                action=AuditAction.AUTH_PASSWORD_RESET_COMPLETED,
                outcome="failure",
                metadata={"reason": "token_not_found"},
            )
            raise InvalidResetTokenError("Token inválido ou expirado")

        token_hash = hash_reset_token(token)
        try:
            user.complete_password_reset(token_hash, self._hasher.hash(new_password))
        except DomainInvalidResetToken as exc:
            await record_audit(
                self._audit,
                audit_ctx,
                action=AuditAction.AUTH_PASSWORD_RESET_COMPLETED,
                outcome="failure",
                resource_type="user",
                resource_id=user.id.value if user.id else None,
                metadata={"reason": "token_expired"},
            )
            raise InvalidResetTokenError(str(exc)) from exc

        await self._users.save(user)
        await record_audit(
            self._audit,
            audit_ctx,
            action=AuditAction.AUTH_PASSWORD_RESET_COMPLETED,
            outcome="success",
            resource_type="user",
            resource_id=user.id.value if user.id else None,
        )
