from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from core.generic import modelsGeneric


class ApiKeys(modelsGeneric):
    __tablename__ = "api_keys"

    id = Column(Integer, autoincrement=True, primary_key=True)
    key_prefix = Column(String(12), nullable=False, index=True)
    key_hash = Column(String(255), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    scopes = Column(String(255), nullable=False, default="read")
    expires_at = Column(DateTime, nullable=True)
