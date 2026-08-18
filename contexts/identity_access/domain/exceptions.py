class DomainError(Exception):
    """Erro de regra de negócio do domínio Identity & Access."""


class UserInactiveError(DomainError):
    pass


class InvalidCredentialsError(DomainError):
    pass


class InvalidResetTokenError(DomainError):
    pass


class UserNotFoundError(DomainError):
    pass


class RoleNotFoundError(DomainError):
    pass


class PermissionNotFoundError(DomainError):
    pass


class DuplicateUserError(DomainError):
    pass


class UserBlockedError(DomainError):
    pass


class PasswordResetLimitError(DomainError):
    pass


class WeakPasswordError(DomainError):
    pass
