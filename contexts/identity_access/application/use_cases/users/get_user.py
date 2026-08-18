from __future__ import annotations

from contexts.identity_access.application.dto.users import UserRecord
from contexts.identity_access.application.exceptions import UserNotFoundError
from contexts.identity_access.application.mappers import user_to_record
from contexts.identity_access.application.ports.user_repository import UserRepository


class GetUserById:
    def __init__(self, users: UserRepository) -> None:
        self._users = users

    async def execute(self, user_id: int) -> UserRecord:
        user = await self._users.get_by_id(user_id)
        if not user:
            raise UserNotFoundError("Usuário não encontrado.")
        return user_to_record(user)
