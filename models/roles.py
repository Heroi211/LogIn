from sqlalchemy import Column,Integer,String
from core.generic import modelsGeneric
from sqlalchemy.orm import relationship

USER = 1
OPERATOR = 2
ADMINISTRATOR = 3
USER_CLIENT = 4

ROLES = [
    (USER, 'Usuario'), # Usuário padrão, sem permissões especiais, mas que atua nas rotinas
    (OPERATOR, 'Operador'), # Usuário com permissões para verificar o sistema e aprovar tarefas. 
    (ADMINISTRATOR, 'Administrador'), # Administrador do sistema com poder total
    (USER_CLIENT, 'Usuario_cliente'), # Usuário do sistema, que também é cliente, pode cadastrar rotinas para si e para outros clientes
]

class Roles(modelsGeneric):
    __tablename__='roles'
    id = Column(Integer,primary_key=True,autoincrement=True)
    description = Column(String,nullable=False)
   
    user = relationship("Users",uselist=False, back_populates="role")
    
    def __init__(self,description):
        self.description = description
    
    def get_roles(self):
        return self.ROLES[self.id][1]