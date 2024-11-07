from fastapi import APIRouter,HTTPException,status,Depends,Response
from models.users import Users as users_models
from models.clients import Clients as clients_models
from schemas import clients_schemas as clients_schemas
from models.users_clients import Users_Clients as users_clients_models

from schemas import users_schemas as users_schemas
from core.deps import get_session,get_current_user
from typing import List
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
import datetime
from services import users_services as users_service
from services import clients_services as clients_service
from sqlalchemy.exc import IntegrityError
from core.auth import _generate_access_token
from core.security import get_password_hash

router = APIRouter()

#POST Client
@router.post('/', response_model=clients_schemas.clients,status_code=status.HTTP_201_CREATED)
async def post_user(Client: clients_schemas.clients,db:AsyncSession = Depends(get_session)):
    try:
        new_client:clients_models = await clients_service.register_clients(Client,db) 
        return new_client
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail="Usuário já cadastrado na base de dados")