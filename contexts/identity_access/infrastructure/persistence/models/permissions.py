from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from contexts.identity_access.infrastructure.persistence.base import Base

role_permissions_table = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "permission_id",
        Integer,
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Permissions(Base):
    __tablename__ = "permissions"
    id = Column(Integer, autoincrement=True, primary_key=True)
    code = Column(String(100), unique=True, nullable=False)
    description = Column(String(255), nullable=False)
    module = Column(String(100), nullable=True)
    active = Column(Boolean, nullable=False, default=True)

    roles = relationship("Roles", secondary=role_permissions_table, back_populates="permissions")
