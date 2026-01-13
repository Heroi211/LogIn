from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class clients(BaseModel):
    id: Optional[int] = None
    cnpj: str
    razao_social: str
    email: EmailStr
    phone: str

    class Config:
        orm_mode = True


class clientsUpdate(clients):
    cnpj: Optional[str] = None
    razao_social: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    
class clientsGetData(clients):
    cnpj: Optional[str] = None
    razao_social: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    tarefas: Optional[int] = None
    
class clientsGetNames(BaseModel):
    id : int 
    razao_social: str
    
    class Config:
        orm_mode = True
   
    
