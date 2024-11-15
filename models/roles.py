from sqlalchemy import Column,Integer,String
from core.generic import modelsGeneric
from sqlalchemy.orm import relationship

User = 1
Operator = 2
Administrator = 3
User_client = 4

user_roles = [
    (User, 'Usuario'), # Usuário padrão, sem permissões especiais, mas que atua nas rotinas
    (Operator, 'Operador'), # Usuário com permissões para verificar o sistema e aprovar tarefas. 
    (Administrator, 'Administrador'), # Administrador do sistema com poder total
    (User_client, 'Usuario_cliente'), # Usuário do sistema, que também é cliente, pode cadastrar rotinas para si e para outros clientes
]

class Roles(modelsGeneric):
    __tablename__='roles'
    id = Column(Integer,primary_key=True,autoincrement=True)
    description = Column(String,nullable=False)
   
    user = relationship("Users",uselist=False, back_populates="role")
    