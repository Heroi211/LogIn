from sqlalchemy import Column,Integer, String, Boolean,Date,ForeignKey,Null,DateTime
from sqlalchemy.orm import relationship
from core.configs import settings
#from pydantic import EmailStr, use no schema e não no model
import datetime

class Client(settings.DB_BaseModel):
    __tablename__ = 'client'
    id = Column(Integer,autoincrement=True,primary_key=True)
    password = Column(String(255),nullable=False)
    name = Column(String(50),nullable=False)
    email = Column(String(50),nullable=False)
    phone = Column(String(12),nullable=False)
    CPF = Column(String(12), unique=True,nullable=False)
    created_at = Column(DateTime,default=datetime.datetime.now())
    role_id = Column(Integer,ForeignKey('roles.id'),default=1)
    active = Column(Boolean,default=True)
    reset_password_token = Column(String(255),nullable=True)
    reset_password_expires = Column(DateTime,nullable=True)
    
    #relação da FK pra apontar o relacionamento de role para usuario. 1xN
    role = relationship("Roles",lazy='joined')
    
    
 
    