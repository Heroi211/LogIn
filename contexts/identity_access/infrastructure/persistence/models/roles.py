from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from contexts.identity_access.domain.role_type import RoleType
from contexts.identity_access.infrastructure.persistence.base import Base
from contexts.identity_access.infrastructure.persistence.models.permissions import (
    Permissions,
    role_permissions_table,
)


class Roles(Base):
    USER = RoleType.USER
    OPERATOR = RoleType.OPERATOR
    ADMINISTRATOR = RoleType.ADMINISTRATOR
    USER_CLIENT = RoleType.USER_CLIENT

    ROLES = [
        (RoleType.USER, RoleType.USER.label()),
        (RoleType.OPERATOR, RoleType.OPERATOR.label()),
        (RoleType.ADMINISTRATOR, RoleType.ADMINISTRATOR.label()),
        (RoleType.USER_CLIENT, RoleType.USER_CLIENT.label()),
    ]

    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String, nullable=False)

    user = relationship("Users", uselist=False, back_populates="role")
    permissions = relationship(
        "Permissions",
        secondary=role_permissions_table,
        back_populates="roles",
        lazy="selectin",
    )

    def __init__(self, description: str, active: int | bool = True):
        self.description = description
        self.active = bool(active)

    def get_role_display(self) -> str:
        return RoleType.label_for(self.id)
