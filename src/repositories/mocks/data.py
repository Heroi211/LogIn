"""Dados mockados para ENVIRONMENT=development."""

from __future__ import annotations

import copy
from datetime import datetime

from core.security import get_password_hash
from models.api_keys import ApiKeys
from models.roles import Roles
from models.sessions import Sessions
from models.users import Users

_NOW = datetime.utcnow()


def _role(role_id: int, description: str) -> Roles:
    role = Roles(description=description)
    role.id = role_id
    role.active = True
    role.created_at = _NOW
    return role


def _user(
    user_id: int,
    name: str,
    email: str,
    cpf: str,
    phone: str,
    password_plain: str,
    role_id: int,
) -> Users:
    user = Users(
        password=get_password_hash(password_plain),
        name=name,
        email=email,
        phone=phone,
        cpf=cpf,
        role_id=role_id,
    )
    user.id = user_id
    user.active = True
    user.created_at = _NOW
    user.reset_password_token = None
    user.reset_password_expires = None
    user.failed_login_attempts = 0
    return user


def initial_roles() -> list[Roles]:
    return [
        _role(Roles.OPERATOR, "Operador"),
        _role(Roles.ADMINISTRATOR, "Administrador"),
    ]


def initial_users() -> list[Users]:
    return [
        _user(1, "Operador Dev", "operador@example.com", "11111111111", "11999990001", "dev123", Roles.OPERATOR),
        _user(2, "Admin Dev", "admin@example.com", "22222222222", "11999990002", "admin123", Roles.ADMINISTRATOR),
    ]


MOCK_CREDENTIALS_HINT = {
    "operator": {"cpf": "11111111111", "password": "dev123"},
    "administrator": {"cpf": "22222222222", "password": "admin123"},
}


class MockStore:
    """Store in-memory compartilhado entre repositórios mock."""

    def __init__(self) -> None:
        self.roles: dict[int, Roles] = {r.id: copy.deepcopy(r) for r in initial_roles()}
        self.users: dict[int, Users] = {u.id: copy.deepcopy(u) for u in initial_users()}
        self._next_user_id = max(self.users) + 1
        self._next_role_id = max(self.roles) + 1
        self.sessions: dict[int, Sessions] = {}
        self.api_keys: dict[int, ApiKeys] = {}
        self._next_session_id = 1
        self._next_api_key_id = 1
        self.revoked_jtis: set[str] = set()
        self.whatsapp_messages: dict[str, object] = {}

    def clone_user(self, user: Users) -> Users:
        return copy.deepcopy(user)

    def clone_role(self, role: Roles) -> Roles:
        return copy.deepcopy(role)


_store: MockStore | None = None


def get_mock_store() -> MockStore:
    global _store
    if _store is None:
        _store = MockStore()
    return _store
