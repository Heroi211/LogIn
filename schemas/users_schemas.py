from datetime import datetime
from typing import Optional

import pytz
from pydantic import BaseModel as SC_BaseModel
from pydantic import EmailStr


class users(SC_BaseModel):
    id: Optional[int] = None
    name: str
    email: EmailStr
    cpf: str
    phone: str
    active: Optional[bool] = True
    role_id: Optional[int] = 1
    reset_password_token: Optional[str] = None
    reset_password_expires: Optional[datetime] = None

    class Config:
        from_attributes = True


class users_create(users):
    password: str
    phone: str


class usersGetData(users):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    cpf: Optional[str] = None
    phone: Optional[str] = None
    active: Optional[bool] = True
    role: Optional[str] = None


class users_updateForm(SC_BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    cpf: Optional[str] = None
    phone: Optional[str] = None
    active: Optional[bool] = True

    class Config:
        from_attributes = True
