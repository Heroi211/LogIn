from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB

from core.generic import modelsGeneric


class AuditEvent(modelsGeneric):
    """Registro append-only de eventos de auditoria (segurança e negócio)."""

    __tablename__ = "audit_events"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    request_id = Column(String(36), nullable=True, index=True)
    actor_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(String(100), nullable=True)
    outcome = Column(String(20), nullable=False)
    ip_address = Column(String(45), nullable=True)
    event_metadata = Column(JSONB, nullable=True)
