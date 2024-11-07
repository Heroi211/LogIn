from pydantic import BaseModel
from typing import Optional

class usersClients(BaseModel):
    id: Optional[int] = None
    clients_id: Optional[int] = None
    user_id: int

    class Config:
        orm_mode = True


class usersClientsUpdate(usersClients):
    clients_id: Optional[int] = None
    user_id: Optional[int] = None

