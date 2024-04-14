from sqlalchemy import Column,Integer, String, Boolean,Date,ForeignKey,Null,DateTime
from sqlalchemy.orm import relationship
from core.configs import settings
#from pydantic import EmailStr, use no schema e não no model
import datetime

class Users(settings.DB_BaseModel):
    __tablename__ = 'users'
    id = Column(Integer,autoincrement=True,primary_key=True)
    password = Column(String(30),nullable=False)
    name = Column(String(50),nullable=False)
    email = Column(String(50),nullable=False)
    CPF = Column(String(12), unique=True,nullable=False)
    created_at = Column(DateTime,default=datetime.datetime.now())
    role_id = Column(Integer,ForeignKey('roles.id'))
    active = Column(Boolean,default=True)
    
    #relação da FK pra apontar o relacionamento de role para usuario. 1xN
    role = relationship("Roles",lazy='joined')
    
    
 
    