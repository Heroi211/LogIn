from pydantic import BaseModel as SC_BaseModel
from typing import Optional
from pydantic import EmailStr
from datetime import date


class users(SC_BaseModel):
    id:Optional[int] = None
    name: str
    email:EmailStr
    CPF: str
    created_at:Optional[date] = date.today()
    active:Optional[bool] = True
    role_id: int
    class Config:
        orm_mode = True

class users_update(users):
    name:Optional[str] = None 
    email:Optional[EmailStr] = None
    CPF: Optional[str] = None
    password:Optional[str] = None
    active:Optional[bool] = True
    role_id:Optional[int] = None

class users_create(users):
    password:str
    
    
    