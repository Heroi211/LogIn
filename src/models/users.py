from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from core.generic import modelsGeneric


class Users(modelsGeneric):
    __tablename__ = "users"
    id = Column(Integer, autoincrement=True, primary_key=True)
    password = Column(String(255), nullable=True)
    name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    phone = Column(String(12), nullable=False)
    cpf = Column(String(12), unique=True, nullable=True)
    role_id = Column(Integer, ForeignKey("roles.id"), default=1)
    auth_provider = Column(String(20), nullable=False, default="local")
    google_id = Column(String(255), unique=True, nullable=True)
    failed_login_attempts = Column(Integer, nullable=False, default=0)
    reset_password_token = Column(String(255), nullable=True)
    reset_password_expires = Column(DateTime, nullable=True)

    role = relationship("Roles", lazy="joined", back_populates="user")
