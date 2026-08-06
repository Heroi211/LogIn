from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from core.generic import modelsGeneric


class Sessions(modelsGeneric):
    __tablename__ = "sessions"

    id = Column(Integer, autoincrement=True, primary_key=True)
    token_hash = Column(String(255), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
