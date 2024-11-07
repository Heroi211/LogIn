from sqlalchemy import Column,Integer,String
from core.generic import modelsGeneric


class Roles(modelsGeneric):
    __tablename__='roles'
    id = Column(Integer,primary_key=True,autoincrement=True)
    description = Column(String,nullable=False)
   
    
    