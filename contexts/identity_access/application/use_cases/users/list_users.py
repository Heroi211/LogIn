from __future__ import annotations

from contexts.identity_access.application.dto.users import UserListItem
from contexts.identity_access.application.mappers import role_label_for, user_to_list_item
from contexts.identity_access.application.ports.role_repository import RoleRepository
from contexts.identity_access.application.ports.user_repository import UserRepository


class ListUsers:
    def __init__(self, users: UserRepository, roles: RoleRepository) -> None:
        self._users = users
        self._roles = roles

    async def execute(self) -> list[UserListItem]:
        items: list[UserListItem] = []
        for user in await self._users.list_active():
            role = await self._roles.get_by_id(user.role_id)
            items.append(user_to_list_item(user, role_label_for(role)))
        return items
