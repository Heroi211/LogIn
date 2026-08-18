from __future__ import annotations

from contexts.identity_access.application.dto.audit import AuditContext
from contexts.identity_access.application.dto.users import RegisterUserInput, UserRecord
from contexts.identity_access.application.exceptions import WeakPasswordError
from contexts.identity_access.application.mappers import user_to_record
from contexts.identity_access.application.ports.audit_logger import AuditLogger
from contexts.identity_access.application.ports.password_hasher import PasswordHasher
from contexts.identity_access.application.ports.user_repository import UserRepository
from contexts.identity_access.application.use_cases._audit import record_audit
from contexts.identity_access.domain.audit.actions import AuditAction
from contexts.identity_access.domain.entities.user import User
from contexts.identity_access.domain.exceptions import WeakPasswordError as DomainWeakPasswordError
from contexts.identity_access.domain.services.password_policy import validate_password


class RegisterUser:
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

    async def execute(self, data: RegisterUserInput, audit_ctx: AuditContext | None = None) -> UserRecord:
        try:
            validate_password(data.password, min_length=self._password_min_length)
        except DomainWeakPasswordError as exc:
            raise WeakPasswordError(str(exc)) from exc

        user = User.register(
            name=data.name,
            email=data.email,
            cpf=data.cpf,
            phone=data.phone,
            password_hash=self._hasher.hash(data.password),
        )
        saved = await self._users.add(user)
        await record_audit(
            self._audit,
            audit_ctx,
            action=AuditAction.USER_CREATED,
            outcome="success",
            resource_type="user",
            resource_id=saved.id.value if saved.id else None,
        )
        return user_to_record(saved)
