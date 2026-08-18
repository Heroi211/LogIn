from __future__ import annotations

from contexts.identity_access.application.dto.roles import RoleRecord
from contexts.identity_access.application.dto.users import UserListItem, UserRecord
from contexts.identity_access.domain.entities.role import Role
from contexts.identity_access.domain.entities.user import User
from contexts.identity_access.domain.role_type import RoleType


def user_to_record(user: User) -> UserRecord:
    assert user.id is not None
    return UserRecord(
        id=user.id.value,
        name=user.name,
        email=str(user.email),
        cpf=str(user.cpf),
        phone=user.phone,
        active=user.active,
        blocked=user.blocked,
        role_id=user.role_id,
        password_hash=user.password.value,
        reset_password_token=user.reset_password_token,
        reset_password_expires=user.reset_password_expires,
    )


def user_to_list_item(user: User, role_label: str | None) -> UserListItem:
    assert user.id is not None
    return UserListItem(
        id=user.id.value,
        name=user.name,
        email=str(user.email),
        cpf=str(user.cpf),
        phone=user.phone,
        active=user.active,
        blocked=user.blocked,
        role=role_label,
    )


def role_to_record(role: Role) -> RoleRecord:
    assert role.id is not None
    return RoleRecord(
        id=role.id,
        description=role.description,
        active=role.active,
        permissions=tuple(sorted(role.permission_codes)),
    )


def role_label_for(role: Role | None) -> str | None:
    if role is None or role.id is None:
        return None
    return RoleType.label_for(role.id)
