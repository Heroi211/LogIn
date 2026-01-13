from pydantic import BaseModel
from typing import Optional

class usersClients(BaseModel):
    id: Optional[int] = None
    client_id: int 
    user_id: int
    active: Optional[bool] = True
    class Config:
        orm_mode = True
    

class usersClientsGetNames(usersClients):
    client_id: Optional[int] = None
    user_id: Optional[int] = None
    client: Optional[str] = None
    user: Optional[str] = None
    

