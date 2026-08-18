from sqlalchemy import Boolean, Column, DateTime, Integer
from sqlalchemy.ext.declarative import as_declarative, declared_attr

from shared.utils import utcnow


@as_declarative()
class Base:
    created_at = Column(DateTime, default=utcnow(), nullable=False)
    active = Column(Boolean, default=True)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
