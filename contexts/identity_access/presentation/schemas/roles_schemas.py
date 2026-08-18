from typing import Optional

from pydantic import BaseModel as SC_basemodel
from pydantic import Field


class role(SC_basemodel):
    id: Optional[int] = None
    description: str
    active: bool
    permissions: list[str] = Field(default_factory=list)

    class Config:
        from_attributes = True


class role_update(role):
    description: Optional[str] = None
    active: Optional[bool] = None
    permissions: Optional[list[str]] = None


class role_permissions_update(SC_basemodel):
    permissions: list[str] = Field(default_factory=list)
