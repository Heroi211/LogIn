from pydantic import BaseModel as SC_basemodel
from typing import Optional


class role(SC_basemodel):
    id:Optional[int] = None
    description:str
    active:bool
    
    class Config:
        orm_mode = True
        
class role_update(role):
    description:Optional[str]
    active:Optional[bool]
    
