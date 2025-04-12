from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from core.generic import modelsGeneric

# Classe de modelo de dados
class Routines(modelsGeneric):
    
    STATUS_ABERTA = 1
    STATUS_EXECUTANDO = 2
    STATUS_CONCLUIDA = 3
    STATUS_CANCELADA = 4
    STATUS_VENCIDA = 5

    STATUS_ROTINA = [
        (STATUS_ABERTA, 'Aberta'), # Nenhum usuário atribuido
        (STATUS_EXECUTANDO, 'Executando'), # Usuário atribuido 
        (STATUS_CONCLUIDA, 'Concluída'), # Concluída
        (STATUS_CANCELADA, 'Cancelada'), # Cancelada pelo cliente
        (STATUS_VENCIDA, 'Vencida') # SLA estourado
    ]
    
    BAIXA = 1
    NORMAL = 2
    ALTA = 3 
    
    PRIORIDADE_ROUTINE = [
        (BAIXA, 'Baixa'), # Nenhum usuário atribuido
        (NORMAL, 'Normal'), # Usuário atribuido 
        (ALTA, 'Alta'), # Concluída
    ]
    
    __tablename__ = 'routines'
    
    id = Column(Integer, autoincrement=True, primary_key=True)
    titulo = Column(String(100), nullable=False)
    descricao = Column(String(500), nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    dt_vencimento = Column(DateTime, nullable=True)
    prioridade = Column(Integer, nullable=True)  # Usaremos um valor numérico para a prioridade: 1 (Alta), 2 (Média), 3 (Baixa)
    users_id = Column(Integer, ForeignKey('users.id'))
    clients_id = Column(Integer, ForeignKey('clients.id'))
    hr_estimativa = Column(Integer, nullable=True)  # Campo opcional para horas estimadas
    hr_real = Column(Integer, nullable=True)  # Campo opcional para horas reais
    status = Column(Integer, nullable=False)  # Status pode representar diferentes estados, como "em andamento", "concluído", etc.

    # Relações com outras tabelas
    user = relationship('Users',back_populates="routine")
    client = relationship('Clients',back_populates="routine")

    # Métodos para manipulação de tarefas
    def __init__(self, titulo, descricao, dt_vencimento=None, prioridade=3, hr_estimativa=0, hr_real=0, status=0):
        self.titulo = titulo
        self.descricao = descricao
        self.is_completed = False
        self.dt_vencimento = dt_vencimento
        self.prioridade = prioridade
        self.hr_estimativa = hr_estimativa
        self.hr_real = hr_real
        self.status = status

    def complete_task(self):
        """Marca a tarefa como concluída."""
        self.is_completed = True
        print(f"Tarefa '{self.titulo}' marcada como concluída.")
        
    def get_status_display(self):
        """Retorna o status da tarefa."""
        for status_value, status_label in self.STATUS_ROTINA:
            if self.status == status_value:
                return status_label
        return "Status inválido"
    
    def get_priority_display(self):
        """Retorna a prioridade da tarefa."""
        if 1 <= self.prioridade <= len(self.PRIORIDADE_ROUTINE):
            return self.PRIORIDADE_ROUTINE[self.prioridade - 1][1]
        return "Prioridade inválida"

    def __str__(self):
        """Representação da tarefa em formato legível."""
        status = "✓" if self.is_completed else "✗"
        priority_str = {1: "Alta", 2: "Média", 3: "Baixa"}.get(self.prioridade, "Baixa")
        due_date_str = self.dt_vencimento.strftime('%Y-%m-%d') if self.dt_vencimento else "Sem prazo"
        return f"{status} {self.titulo} [Prioridade: {priority_str}] - Due: {due_date_str}"

    # Classe para manipulação da lista de tarefas
    class TodoList:
        def __init__(self):
            self.tasks = []

        def add_task(self, task):
            """Adiciona uma nova tarefa à lista."""
            self.tasks.append(task)
            print(f"Tarefa '{task.titulo}' adicionada com sucesso.")

        def remove_task(self, title):
            """Remove uma tarefa da lista pelo título."""
            self.tasks = [task for task in self.tasks if task.titulo != title]
            print(f"Tarefa '{title}' removida.")

        def list_tasks(self, order_by_priority=False):
            """Lista todas as tarefas, opcionalmente ordenadas por prioridade."""
            tasks = sorted(self.tasks, key=lambda task: task.prioridade) if order_by_priority else self.tasks
            for task in tasks:
                print(task)

