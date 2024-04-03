from pydantic import BaseModel as SC_BaseModel
from typing import Optional
from pydantic import EmailStr
import datetime


class users(SC_BaseModel):
    id:Optional[int] = None
    name: str
    email:EmailStr
    CPF: str
    created_at:Optional[datetime.datetime] = datetime.datetime.now()
    updated_at:Optional[datetime.date] = None
    updated_by:Optional[int] = None
    active:Optional[bool] = True
    
    class Config:
        orm_mode = True

class users_update(users):
    name:Optional[str] = None 
    email:Optional[EmailStr] = None
    CPF: Optional[str] = None
    password:Optional[str] = None
    updated_at:datetime.date = datetime.date.today()
    updated_by:Optional[int] = None
    active:Optional[bool] = True

class users_create(users):
    password:str
    
    
    