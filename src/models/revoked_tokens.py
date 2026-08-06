from sqlalchemy import Column, DateTime, Integer, String

from core.generic import modelsGeneric


class RevokedTokens(modelsGeneric):
    __tablename__ = "revoked_tokens"

    id = Column(Integer, autoincrement=True, primary_key=True)
    jti = Column(String(36), nullable=False, unique=True)
    token_type = Column(String(20), nullable=False)
    user_id = Column(Integer, nullable=True)
    expires_at = Column(DateTime, nullable=False)
