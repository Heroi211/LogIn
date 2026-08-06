"""Testes unitários — exceções de domínio e configs."""

import pytest

from core.configs import settings
from domain.exceptions import (
    AccountLockedError,
    DomainError,
    InvalidCredentialsError,
    MessagingError,
    TokenRevokedError,
)


@pytest.mark.unit
def test_domain_exceptions_inherit_base():
    assert issubclass(InvalidCredentialsError, DomainError)
    assert issubclass(AccountLockedError, DomainError)
    assert issubclass(TokenRevokedError, DomainError)
    assert issubclass(MessagingError, DomainError)


@pytest.mark.unit
def test_settings_development_flags():
    assert settings.is_development is True
    assert settings.ENVIRONMENT == "development"
    assert isinstance(settings.cors_origins_list, list)
