from typing import Optional

from pydantic import BaseModel as SC_BaseModel
from pydantic import Field


class permission(SC_BaseModel):
    id: Optional[int] = None
    code: str = Field(..., min_length=3, max_length=100, examples=["tickets:read"])
    description: str = Field(..., min_length=3, max_length=255)
    module: Optional[str] = Field(None, max_length=100, examples=["tickets"])
    active: bool = True

    class Config:
        from_attributes = True


class permission_create(permission):
    active: bool = True
