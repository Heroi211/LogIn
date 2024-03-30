from sqlalchemy import Column,Integer, String, Boolean,DateTime,ForeignKey
from sqlalchemy.orm import relationship
from core.configs import settings
#from pydantic import EmailStr, use no schema e não no model
import datetime

class User(settings.DB_BaseModel):
    __tablename__ = 'users'
    id = Column(int,autoincrement=True,primary_key=True)
    password = Column(String(30),nullable=False)
    nome = Column(String(50),nullable=False)
    email = Column(String(50),nullable=False)
    CPF = Column(String(12), unique=True,nullable=False)
    created_at = Column(DateTime,default=datetime.datetime.now())
    updated_at = Column(DateTime,onupdate=datetime.datetime.now())
    updated_by = Column(Integer, ForeignKey('users.id'))
    active = Column(Boolean,default=True)
    
    #relashionship
    fk_updated_by = relationship("users",remote_side=[id])
    #o campo updated_by esta autorelacionado com id, para registrar qual usuário alterou o cadastro de um outro, como forma de controle.
    

    
 
    