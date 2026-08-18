from contexts.identity_access.domain.exceptions import (
    DuplicateUserError,
    InvalidCredentialsError,
    InvalidResetTokenError,
    PasswordResetLimitError,
    PermissionNotFoundError,
    RoleNotFoundError,
    UserBlockedError,
    UserInactiveError,
    UserNotFoundError,
    WeakPasswordError,
)

__all__ = [
    "ApplicationError",
    "DuplicateUserError",
    "EmailNotConfiguredError",
    "EmailSendError",
    "InvalidCredentialsError",
    "InvalidResetTokenError",
    "PasswordResetLimitError",
    "PermissionNotFoundError",
    "RoleNotFoundError",
    "UserBlockedError",
    "UserInactiveError",
    "UserNotFoundError",
    "WeakPasswordError",
]


class ApplicationError(Exception):
    """Erro na orquestração de casos de uso."""


class EmailNotConfiguredError(ApplicationError):
    pass


class EmailSendError(ApplicationError):
    pass
