from __future__ import annotations

from contexts.identity_access.domain.entities.role import Role
from contexts.identity_access.domain.entities.user import User
from contexts.identity_access.domain.value_objects.cpf import CPF
from contexts.identity_access.domain.value_objects.email import Email
from contexts.identity_access.domain.value_objects.hashed_password import HashedPassword
from contexts.identity_access.domain.value_objects.user_id import UserId
from contexts.identity_access.infrastructure.persistence.models.roles import Roles
from contexts.identity_access.infrastructure.persistence.models.users import Users


def orm_to_user(entity: Users) -> User:
    return User(
        id=UserId(entity.id),
        name=entity.name,
        email=Email(entity.email),
        cpf=CPF(entity.cpf),
        phone=entity.phone,
        active=entity.active,
        role_id=entity.role_id,
        password=HashedPassword(entity.password),
        blocked=entity.blocked,
        failed_login_attempts=entity.failed_login_attempts,
        reset_password_token=entity.reset_password_token,
        reset_password_expires=entity.reset_password_expires,
        password_reset_count=entity.password_reset_count,
        password_reset_window_start=entity.password_reset_window_start,
    )


def user_to_orm(user: User, entity: Users | None = None) -> Users:
    if entity is None:
        entity = Users(
            name=user.name,
            email=str(user.email),
            cpf=str(user.cpf),
            phone=user.phone,
            password=user.password.value,
        )
    entity.name = user.name
    entity.email = str(user.email)
    entity.cpf = str(user.cpf)
    entity.phone = user.phone
    entity.active = user.active
    entity.blocked = user.blocked
    entity.failed_login_attempts = user.failed_login_attempts
    entity.role_id = user.role_id
    entity.password = user.password.value
    entity.reset_password_token = user.reset_password_token
    entity.reset_password_expires = user.reset_password_expires
    entity.password_reset_count = user.password_reset_count
    entity.password_reset_window_start = user.password_reset_window_start
    return entity


def orm_to_role(entity: Roles) -> Role:
    codes = frozenset(p.code for p in entity.permissions) if entity.permissions else frozenset()
    return Role(
        id=entity.id,
        description=entity.description,
        active=entity.active,
        permission_codes=codes,
    )


def role_to_orm(role: Role, entity: Roles | None = None) -> Roles:
    if entity is None:
        entity = Roles(description=role.description, active=role.active)
    entity.description = role.description
    entity.active = role.active
    return entity
