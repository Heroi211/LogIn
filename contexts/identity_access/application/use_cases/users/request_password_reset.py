from __future__ import annotations

import logging
import secrets
from datetime import datetime, timedelta

from contexts.identity_access.application.dto.audit import AuditContext
from contexts.identity_access.application.exceptions import (
    PasswordResetLimitError,
    UserBlockedError,
    UserInactiveError,
    UserNotFoundError,
)
from contexts.identity_access.application.ports.audit_logger import AuditLogger
from contexts.identity_access.application.ports.email_sender import EmailSender
from contexts.identity_access.application.ports.user_repository import UserRepository
from contexts.identity_access.application.use_cases._audit import record_audit
from contexts.identity_access.domain.audit.actions import AuditAction
from contexts.identity_access.domain.exceptions import PasswordResetLimitError as DomainPasswordResetLimitError
from contexts.identity_access.domain.exceptions import UserBlockedError as DomainUserBlockedError
from contexts.identity_access.domain.exceptions import UserInactiveError as DomainUserInactiveError
from contexts.identity_access.infrastructure.security.token_hash import hash_reset_token

logger = logging.getLogger(__name__)


class RequestPasswordReset:
    def __init__(
        self,
        users: UserRepository,
        email_sender: EmailSender,
        audit: AuditLogger | None = None,
        *,
        max_requests: int = 3,
        window_days: int = 30,
    ) -> None:
        self._users = users
        self._email = email_sender
        self._audit = audit
        self._max_requests = max_requests
        self._window_days = window_days

    async def execute(self, email: str, audit_ctx: AuditContext | None = None) -> None:
        user = await self._users.get_by_email(email)
        if not user:
            raise UserNotFoundError("Usuário não encontrado.")

        now = datetime.now()
        try:
            user.ensure_can_request_password_reset(
                max_requests=self._max_requests,
                window_days=self._window_days,
                now=now,
            )
        except DomainPasswordResetLimitError as exc:
            raise PasswordResetLimitError(str(exc)) from exc
        except DomainUserInactiveError as exc:
            raise UserInactiveError(str(exc)) from exc
        except DomainUserBlockedError as exc:
            raise UserBlockedError(str(exc)) from exc

        token = secrets.token_urlsafe(32)
        expires = now + timedelta(hours=1)
        user.record_password_reset_request(now=now, window_days=self._window_days)
        user.begin_password_reset(hash_reset_token(token), expires)
        await self._users.save(user)
        logger.info("Token de redefinição de senha gerado para e-mail=%s", email)
        await self._email.send_password_reset(email, token)
        await record_audit(
            self._audit,
            audit_ctx,
            action=AuditAction.AUTH_PASSWORD_RESET_REQUESTED,
            outcome="success",
            resource_type="user",
            resource_id=user.id.value if user.id else None,
            metadata={"email": email},
        )
