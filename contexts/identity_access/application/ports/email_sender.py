from typing import Protocol


class EmailSender(Protocol):
    async def send_password_reset(self, email: str, token: str) -> None: ...
