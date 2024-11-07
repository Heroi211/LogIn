from pydantic import BaseModel as SC_BaseModel
from typing import Optional
from pydantic import EmailStr
from datetime import datetime


from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr

class routines(BaseModel):
    id: Optional[int] = None
    titulo: str
    descricao: str
    is_completed: bool = False
    dt_vencimento: datetime
    prioridade: int  # 1 (Alta), 2 (Média), 3 (Baixa)
    users_id: Optional[int] = None
    clients_id: Optional[int] = None
    hr_estimativa: int
    hr_real: int
    status: int  

    class Config:
        orm_mode = True


class routinesUpdate(routines):
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    is_completed: Optional[bool] = None
    dt_vencimento: Optional[datetime] = None
    prioridade: Optional[int] = None
    users_id: Optional[int] = None
    clients_id: Optional[int] = None
    hr_estimativa: Optional[int] = None
    hr_real: Optional[int] = None
    status: Optional[int] = None


class routinesCreate(routines):
    pass
    
    
    