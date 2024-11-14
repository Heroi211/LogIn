from sqlalchemy import Column,Integer, Boolean,DateTime
from sqlalchemy.ext.declarative import as_declarative, declared_attr
import datetime

@as_declarative()
class modelsGeneric:

    created_at = Column(DateTime,default=datetime.datetime.now())
    active = Column(Boolean,default=True)
    
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()