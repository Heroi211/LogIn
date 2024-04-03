from sqlalchemy import Column,Integer,String
from sqlalchemy.orm import relationship

from core.configs import settings

class Roles(settings.DB_BaseModel):
    __tablename__='roles'
    id = Column(Integer,primary_key=True,autoincrement=True)
    description = Column(String,nullable=False)
    active = Column(Integer,nullable=False)
    