from sqlalchemy import Column,Integer, Boolean,DateTime
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from core.configs import settings
#from pydantic import EmailStr, use no schema e não no model
import datetime

@as_declarative()
class modelsGeneric():

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime,default=datetime.datetime.now())
    active = Column(Boolean,default=True)
    
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()