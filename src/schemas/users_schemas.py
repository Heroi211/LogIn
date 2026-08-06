from datetime import datetime

from pydantic import BaseModel as SC_BaseModel
from pydantic import EmailStr, Field


class usersPublic(SC_BaseModel):
    """Resposta pública — sem campos sensíveis de reset."""

    id: int | None = None
    name: str
    email: EmailStr
    cpf: str
    phone: str
    created_at: datetime | None = None
    active: bool | None = True
    role_id: int | None = 1
    auth_provider: str | None = "local"

    class Config:
        from_attributes = True


class users(usersPublic):
    """Compatibilidade interna — preferir usersPublic em endpoints."""

    pass


class users_update(usersPublic):
    name: str | None = None
    email: EmailStr | None = None
    cpf: str | None = None
    password: str | None = None
    phone: str | None = None
    active: bool | None = True
    role_id: int | None = None


class users_create(SC_BaseModel):
    name: str
    email: EmailStr
    cpf: str
    phone: str
    password: str = Field(min_length=8)
    role_id: int | None = 1


class usersGetData(SC_BaseModel):
    id: int | None = None
    name: str | None = None
    email: EmailStr | None = None
    cpf: str | None = None
    phone: str | None = None
    active: bool | None = True
    role_id: int | None = None
    role: str | None = None
    auth_provider: str | None = None

    class Config:
        from_attributes = True


class users_updateForm(SC_BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    cpf: str | None = None
    phone: str | None = None
    active: bool | None = True
    role_id: int | None = None

    class Config:
        from_attributes = True


class ResetPasswordRequest(SC_BaseModel):
    token: str
    password: str = Field(min_length=8)


class MessageResponse(SC_BaseModel):
    message: str
