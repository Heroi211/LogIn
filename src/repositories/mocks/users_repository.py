from __future__ import annotations

from datetime import datetime
from typing import Any

from domain.dtos.user_dtos import UserCreateDTO
from domain.entities.user import ApiKeyEntity, SessionEntity, UserEntity
from infrastructure.auth.token_utils import hash_token
from infrastructure.persistence.mappers import api_key_to_entity, session_to_entity, user_to_entity
from models.api_keys import ApiKeys
from models.roles import Roles
from models.sessions import Sessions
from models.users import Users
from repositories.base import ApiKeysRepository, SessionsRepository, UsersRepository
from repositories.mocks.data import get_mock_store
from services.utils import utcnow


class MockUsersRepository(UsersRepository):
    def __init__(self) -> None:
        self._store = get_mock_store()

    def _clone_entity(self, user: Users) -> UserEntity:
        return user_to_entity(self._store.clone_user(user))

    async def get_by_id(self, user_id: int) -> UserEntity | None:
        user = self._store.users.get(user_id)
        if user and user.active:
            return self._clone_entity(user)
        return None

    async def get_by_cpf(self, cpf: str) -> UserEntity | None:
        for user in self._store.users.values():
            if user.cpf == cpf and user.active:
                return self._clone_entity(user)
        return None

    async def get_by_cpf_for_auth(self, cpf: str) -> UserEntity | None:
        for user in self._store.users.values():
            if user.cpf == cpf:
                return self._clone_entity(user)
        return None

    async def get_by_email(self, email: str) -> UserEntity | None:
        for user in self._store.users.values():
            if user.email == email and user.active:
                return self._clone_entity(user)
        return None

    async def get_by_google_id(self, google_id: str) -> UserEntity | None:
        for user in self._store.users.values():
            if getattr(user, "google_id", None) == google_id and user.active:
                return self._clone_entity(user)
        return None

    async def get_by_reset_token(self, token: str) -> UserEntity | None:
        for user in self._store.users.values():
            if user.reset_password_token == token and user.active:
                return self._clone_entity(user)
        return None

    async def list_with_role_display(self) -> list[dict[str, Any]]:
        rows = []
        for user in sorted(self._store.users.values(), key=lambda u: u.id):
            if not user.active:
                continue
            role = self._store.roles.get(user.role_id)
            rows.append(
                {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "cpf": user.cpf,
                    "phone": user.phone,
                    "active": user.active,
                    "role_id": user.role_id,
                    "role": role.get_role_display() if role else None,
                    "auth_provider": getattr(user, "auth_provider", "local"),
                }
            )
        return rows

    async def create(self, payload: UserCreateDTO, password_hash: str) -> UserEntity:
        user_id = self._store._next_user_id
        self._store._next_user_id += 1
        user = Users(
            password=password_hash,
            name=payload.name,
            email=payload.email,
            cpf=payload.cpf,
            phone=payload.phone,
            role_id=payload.role_id,
            auth_provider="local",
        )
        user.id = user_id
        user.active = True
        user.created_at = utcnow()
        self._store.users[user_id] = user
        return self._clone_entity(user)

    async def create_oauth_user(
        self,
        *,
        name: str,
        email: str,
        google_id: str,
        role_id: int = Roles.OPERATOR,
    ) -> UserEntity:
        user_id = self._store._next_user_id
        self._store._next_user_id += 1
        user = Users(
            password=None,
            name=name,
            email=email,
            cpf=None,
            phone="00000000000",
            role_id=role_id,
            auth_provider="google",
        )
        user.google_id = google_id
        user.id = user_id
        user.active = True
        user.created_at = utcnow()
        self._store.users[user_id] = user
        return self._clone_entity(user)

    async def update(self, user_id: int, data: dict[str, Any]) -> UserEntity | None:
        user = self._store.users.get(user_id)
        if not user or not user.active:
            return None
        if data.get("name"):
            user.name = data["name"]
        if data.get("email"):
            user.email = data["email"]
        if data.get("active") is not None:
            user.active = data["active"]
        if data.get("phone"):
            user.phone = data["phone"]
        if data.get("cpf"):
            user.cpf = data["cpf"]
        if data.get("google_id"):
            user.google_id = data["google_id"]
        if data.get("auth_provider"):
            user.auth_provider = data["auth_provider"]
        if data.get("role_id") is not None:
            user.role_id = data["role_id"]
        if data.get("failed_login_attempts") is not None:
            user.failed_login_attempts = data["failed_login_attempts"]
        if data.get("active") is True:
            user.failed_login_attempts = 0
        return self._clone_entity(user)

    async def soft_delete(self, user_id: int) -> UserEntity | None:
        user = self._store.users.get(user_id)
        if not user or not user.active:
            return None
        user.active = False
        return self._clone_entity(user)

    async def set_reset_token(self, user_id: int, token: str, expires: datetime) -> UserEntity | None:
        user = self._store.users.get(user_id)
        if not user or not user.active:
            return None
        user.reset_password_token = token
        user.reset_password_expires = expires
        return self._clone_entity(user)

    async def reset_password(self, user_id: int, password_hash: str) -> UserEntity | None:
        user = self._store.users.get(user_id)
        if not user:
            return None
        user.password = password_hash
        user.auth_provider = "local"
        user.reset_password_token = None
        user.reset_password_expires = None
        return self._clone_entity(user)


class MockSessionsRepository(SessionsRepository):
    def __init__(self) -> None:
        self._store = get_mock_store()

    async def create(
        self,
        *,
        user_id: int,
        token_hash: str,
        expires_at: datetime,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> SessionEntity:
        session_id = self._store._next_session_id
        self._store._next_session_id += 1
        record = Sessions(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        record.id = session_id
        record.active = True
        record.created_at = utcnow()
        self._store.sessions[session_id] = record
        return session_to_entity(record)

    async def get_by_token_hash(self, token_hash: str) -> SessionEntity | None:
        for record in self._store.sessions.values():
            if record.token_hash == token_hash and record.active:
                if record.expires_at < utcnow():
                    record.active = False
                    return None
                return session_to_entity(record)
        return None

    async def revoke(self, token_hash: str) -> bool:
        for record in self._store.sessions.values():
            if record.token_hash == token_hash and record.active:
                record.active = False
                return True
        return False

    async def revoke_all_for_user(self, user_id: int) -> int:
        count = 0
        for record in self._store.sessions.values():
            if record.user_id == user_id and record.active:
                record.active = False
                count += 1
        return count


class MockApiKeysRepository(ApiKeysRepository):
    def __init__(self) -> None:
        self._store = get_mock_store()

    async def create(
        self,
        *,
        key_prefix: str,
        key_hash: str,
        name: str,
        user_id: int,
        scopes: str,
        expires_at: datetime | None = None,
    ) -> ApiKeyEntity:
        key_id = self._store._next_api_key_id
        self._store._next_api_key_id += 1
        record = ApiKeys(
            key_prefix=key_prefix,
            key_hash=key_hash,
            name=name,
            user_id=user_id,
            scopes=scopes,
            expires_at=expires_at,
        )
        record.id = key_id
        record.active = True
        record.created_at = utcnow()
        self._store.api_keys[key_id] = record
        return api_key_to_entity(record)

    async def get_by_prefix(self, key_prefix: str) -> ApiKeyEntity | None:
        for record in self._store.api_keys.values():
            if record.key_prefix == key_prefix and record.active:
                return api_key_to_entity(record)
        return None

    async def list_by_user(self, user_id: int) -> list[ApiKeyEntity]:
        return [
            api_key_to_entity(record)
            for record in self._store.api_keys.values()
            if record.user_id == user_id and record.active
        ]

    async def revoke(self, api_key_id: int, user_id: int | None = None) -> bool:
        record = self._store.api_keys.get(api_key_id)
        if not record or not record.active:
            return False
        if user_id is not None and record.user_id != user_id:
            return False
        record.active = False
        return True

    async def verify_key(self, full_key: str) -> ApiKeyEntity | None:
        if not full_key.startswith("ltk_"):
            return None
        parts = full_key.split("_", 2)
        if len(parts) != 3:
            return None
        entity = await self.get_by_prefix(parts[1])
        if not entity:
            return None
        if entity.key_hash != hash_token(full_key):
            return None
        if entity.expires_at and entity.expires_at < utcnow():
            return None
        return entity
