from sqlalchemy import Column,Integer, String, Boolean,Date,ForeignKey,Null,DateTime
from sqlalchemy.orm import relationship
from core.generic import modelsGeneric

class Users_Clients(modelsGeneric):
    __tablename__ = 'users_clients'
    id = Column(Integer,autoincrement=True,primary_key=True)
    client_id = Column(Integer,ForeignKey('clients.id'))
    user_id = Column(Integer,ForeignKey('users.id')) 
 

    #relação da FK pra apontar o relacionamento de role para usuario. 1xN
    user = relationship("Users", back_populates="user_clients")
    client = relationship("Clients", back_populates="user_clients")
    
    def __init__(self,client_id,user_id):
        self.client_id = client_id
        self.user_id = user_id
        
    def __str__(self):
        return self.client_id

    
    
    
 
    