from sqlalchemy import Column,Integer, String, Boolean,Date,ForeignKey,Null,DateTime
from sqlalchemy.orm import relationship
from core.configs import settings
#from pydantic import EmailStr, use no schema e não no model
import datetime

class modelsGeneric(settings.DB_BaseModel):
    __tablename__ = None
    created_at = Column(DateTime,default=datetime.datetime.now())
    active = Column(Boolean,default=True)