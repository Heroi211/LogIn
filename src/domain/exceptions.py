from __future__ import annotations


class DomainError(Exception):
    """Erro de domínio base."""


class EntityNotFoundError(DomainError):
    pass


class DuplicateEntityError(DomainError):
    pass


class InvalidCredentialsError(DomainError):
    pass


class SessionExpiredError(DomainError):
    pass


class ApiKeyInvalidError(DomainError):
    pass


class OAuthError(DomainError):
    pass


class OAuthLinkRequiredError(DomainError):
    """Conta local existe — exige vínculo explícito com senha."""

    pass


class AccountLockedError(DomainError):
    pass


class TokenRevokedError(DomainError):
    pass


class MessagingError(DomainError):
    pass


class WhatsAppNotConfiguredError(MessagingError):
    pass
