# Description: Arquivo de modelagem da tabela de log de alterações de usuários.
from sqlalchemy import Column,Integer,String,DateTime,ForeignKey,Boolean
from sqlalchemy.orm import relationship
import datetime
from core.generic import modelsGeneric

class Users_update(modelsGeneric):
    __tablename__=('users_update')
    id = Column(Integer,primary_key=True,autoincrement=True)
    updated_at = Column(DateTime,default=datetime.datetime.now(),nullable=False)
    user_id = Column(Integer,ForeignKey('users.id'))
    user_password = Column(String, nullable=True)
    user_name = Column(String, nullable=True)
    user_email = Column(String, nullable=True)
    user_CPF = Column(String,unique=True, nullable=False)
    role_changed = Column(Integer,ForeignKey('roles.id'),nullable=True)
    active_changed = Column(Boolean, nullable=True)
    user_changer = Column(Integer,ForeignKey('users.id')) #usuário que fez a alteração.
    
    #relação dos roles com usuário na tabela de log.
    relationship('Users',lazy='joined')
    relationship('Roles',lazy='joined')
    
    
    
    