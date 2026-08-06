from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from core.configs import settings
from repositories.base import (
    ApiKeysRepository,
    RevokedTokensRepository,
    RolesRepository,
    SessionsRepository,
    UsersRepository,
    WhatsAppMessagingRepository,
)
from repositories.mocks.revoked_tokens_repository import MockRevokedTokensRepository
from repositories.mocks.roles_repository import MockRolesRepository
from repositories.mocks.users_repository import (
    MockApiKeysRepository,
    MockSessionsRepository,
    MockUsersRepository,
)
from repositories.sqlalchemy.revoked_tokens_repository import SqlAlchemyRevokedTokensRepository
from repositories.sqlalchemy.roles_repository import SqlAlchemyRolesRepository
from repositories.sqlalchemy.sessions_repository import (
    SqlAlchemyApiKeysRepository,
    SqlAlchemySessionsRepository,
)
from repositories.sqlalchemy.users_repository import SqlAlchemyUsersRepository

logger = logging.getLogger(__name__)


class UsersRepositoryFactory:
    @staticmethod
    def create(session: AsyncSession | None) -> UsersRepository:
        if settings.is_development:
            return MockUsersRepository()
        if session is None:
            raise RuntimeError("Sessão de banco obrigatória fora de development.")
        return SqlAlchemyUsersRepository(session)


class RolesRepositoryFactory:
    @staticmethod
    def create(session: AsyncSession | None) -> RolesRepository:
        if settings.is_development:
            return MockRolesRepository()
        if session is None:
            raise RuntimeError("Sessão de banco obrigatória fora de development.")
        return SqlAlchemyRolesRepository(session)


class SessionsRepositoryFactory:
    @staticmethod
    def create(session: AsyncSession | None) -> SessionsRepository:
        if settings.is_development:
            return MockSessionsRepository()
        if session is None:
            raise RuntimeError("Sessão de banco obrigatória fora de development.")
        return SqlAlchemySessionsRepository(session)


class ApiKeysRepositoryFactory:
    @staticmethod
    def create(session: AsyncSession | None) -> ApiKeysRepository:
        if settings.is_development:
            return MockApiKeysRepository()
        if session is None:
            raise RuntimeError("Sessão de banco obrigatória fora de development.")
        return SqlAlchemyApiKeysRepository(session)


class RevokedTokensRepositoryFactory:
    @staticmethod
    def create(session: AsyncSession | None) -> RevokedTokensRepository:
        if settings.is_development:
            return MockRevokedTokensRepository()
        if session is None:
            raise RuntimeError("Sessão de banco obrigatória fora de development.")
        return SqlAlchemyRevokedTokensRepository(session)


class WhatsAppMessagingRepositoryFactory:
    @staticmethod
    def create() -> WhatsAppMessagingRepository:
        from repositories.mocks.whatsapp_repository import MockWhatsAppRepository
        from repositories.twilio.whatsapp_repository import TwilioWhatsAppRepository

        if settings.twilio_use_live:
            logger.debug("WhatsAppMessagingRepository → Twilio (live)")
            return TwilioWhatsAppRepository()

        if settings.is_development:
            logger.debug("WhatsAppMessagingRepository → mock (ENVIRONMENT=development)")
            return MockWhatsAppRepository()

        logger.warning("Twilio não configurado em production — usando mock seguro.")
        return MockWhatsAppRepository()
