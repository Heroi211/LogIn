from pydantic import BaseModel as SC_BaseModel
from typing import Optional
from pydantic import EmailStr
import datetime


class users(SC_BaseModel):
    id:Optional[int] = None
    nome: str
    email:EmailStr
    CPF: str
    created_at:datetime
    updated_at:datetime
    updated_by:Optional[int] = None
    active:Optional[bool] = True
    
    class Config:
        orm_mode = True

class users_update(users):
    nome:Optional[str] = None 
    email:Optional[EmailStr] = None
    CPF: Optional[str] = None
    updated_at:datetime = datetime.datetime.now()
    updated_by:int
    active:Optional[bool] = True

class users_create(users):
    password:str
    
    
    