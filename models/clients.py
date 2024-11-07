from sqlalchemy import Column,Integer, String, Boolean,Date,ForeignKey,Null,DateTime
from sqlalchemy.orm import relationship
from core.generic import modelsGeneric
#from pydantic import EmailStr, use no schema e não no model

class Clients(modelsGeneric):
    __tablename__ = 'clients'
    id = Column(Integer,autoincrement=True,primary_key=True)
    CNPJ = Column(String(14),nullable=False)
    razao_social = Column(String(50),nullable=False)
    email = Column(String(50),nullable=False)
    phone = Column(String(12),nullable=False)
 
    def __init__(self,CNPJ,razao_social,email,phone):
        self.CNPJ = CNPJ
        self.razao_social = razao_social
        self.email = email
        self.phone = phone
        
    def __str__(self):
        return self.razao_social
    
    
    
    
 
    