from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from contexts.identity_access.infrastructure.persistence.base import Base


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, autoincrement=True, primary_key=True)
    password = Column(String(255), nullable=False)
    name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    phone = Column(String(12), nullable=False)
    cpf = Column(String(12), unique=True, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), default=1)
    reset_password_token = Column(String(64), nullable=True)
    reset_password_expires = Column(DateTime, nullable=True)
    active = Column(Boolean, nullable=False, default=True)
    blocked = Column(Boolean, nullable=False, default=False)
    failed_login_attempts = Column(Integer, nullable=False, default=0)
    password_reset_count = Column(Integer, nullable=False, default=0)
    password_reset_window_start = Column(DateTime, nullable=True)

    role = relationship("Roles", lazy="joined", back_populates="user")
