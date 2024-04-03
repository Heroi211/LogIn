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
    updated_at = Column(Date,default=Null,onupdate=datetime.date.today(),nullable=True)
    updated_by = Column(Integer, ForeignKey('users.id'),nullable=True)
    active = Column(Boolean,default=True)
    
    #relashionship
    fk_updated_by = relationship("Users",remote_side=[id])
    #o campo updated_by esta autorelacionado com id, para registrar qual usuário alterou o cadastro de um outro, como forma de controle.
    

    
 
    