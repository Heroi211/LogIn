from contexts.identity_access.application.dto.roles import RoleRecord
from contexts.identity_access.application.dto.users import UserListItem, UserRecord
from contexts.identity_access.application.mappers import role_to_record as _role_to_record
from contexts.identity_access.application.mappers import user_to_list_item as _user_to_list_item
from contexts.identity_access.application.mappers import user_to_record as _user_to_record


def user_record_to_response(user: UserRecord) -> dict:
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "cpf": user.cpf,
        "phone": user.phone,
        "active": user.active,
        "blocked": user.blocked,
        "role_id": user.role_id,
    }


def user_list_item_to_response(item: UserListItem) -> dict:
    return {
        "id": item.id,
        "name": item.name,
        "email": item.email,
        "cpf": item.cpf,
        "phone": item.phone,
        "active": item.active,
        "blocked": item.blocked,
        "role": item.role,
    }


def role_record_to_response(role: RoleRecord) -> dict:
    return {
        "id": role.id,
        "description": role.description,
        "active": role.active,
        "permissions": list(role.permissions),
    }


# Aliases para compatibilidade interna
user_to_record = _user_to_record
user_to_list_item = _user_to_list_item
role_to_record = _role_to_record
