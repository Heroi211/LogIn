from sqlalchemy import Column,Integer, String, Boolean,Date,ForeignKey,Null,DateTime
from sqlalchemy.orm import relationship
from core.generic import modelsGeneric

class Users_Clients(modelsGeneric):
    __tablename__ = 'users_clients'
    id = Column(Integer,autoincrement=True,primary_key=True)
    clients_id = Column(Integer,ForeignKey('Clients.id'),nullable=True)
    user_id = Column(Integer,ForeignKey('users.id')) 
 

    #relação da FK pra apontar o relacionamento de role para usuario. 1xN
    relationship('Users',lazy='joined')
    relationship('Clients',lazy='joined')
    
    def __init__(self,clients_id,user_id):
        self.clients_id = clients_id
        self.user_id = user_id
        
    def __str__(self):
        return self.clients_id

    
    
    
 
    