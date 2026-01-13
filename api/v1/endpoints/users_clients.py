from fastapi import APIRouter,HTTPException, status,Depends
from schemas import users_clients_schemas as users_clients_schemas
from schemas import clients_schemas as clients_schemas
from models import users_clients as users_clients_models
from services import users_clients_services as users_clients_service
from services import clients_services as clients_service

from models.roles import Roles as roles_models
from models.users import Users as users_models
from core.deps import get_session, get_current_user
from services import roles_services as roles_service

from sqlalchemy.ext.asyncio import AsyncSession
from services.utils import processar_origem

from typing import List


router = APIRouter()

#POST users_clients
@router.post('/',status_code=status.HTTP_201_CREATED,response_model=users_clients_schemas.usersClients)
async def post_users_clients(user_client:users_clients_schemas.usersClients,db:AsyncSession = Depends(get_session),user_logged :users_models = Depends(get_current_user)):
    try:
        if user_logged:
            new_user_clients:users_clients_models = await users_clients_service.register_user_client(user_client,db)
            return new_user_clients
        else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except HTTPException as e:
        if e.status_code != status.HTTP_401_UNAUTHORIZED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ocorreu um erro durante a solicitação.")
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Você não possui permissão para consultar esses dados.")
    

#GET users_clients
@router.get('/',status_code=status.HTTP_200_OK,response_model=List[users_clients_schemas.usersClients])
async def get_users_clients(db:AsyncSession = Depends(get_session),user_logged :users_models = Depends(get_current_user)):
    try:
        if user_logged == 3:
            users_clients:List[users_clients_schemas.usersClients] = await users_clients_service.select_all_user_clients(db)
            return users_clients
        else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except HTTPException as e:
        if e.status_code != status.HTTP_401_UNAUTHORIZED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ocorreu um erro durante a solicitação.")
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Você não possui permissão para consultar esses dados.")

#GET users_clients by key
@router.get('/',status_code=status.HTTP_200_OK, response_model=users_clients_schemas.usersClients)
async def get_users_clients_byclientid(key:int,origem:int, db:AsyncSession = Depends(get_session),user_logged :users_models = Depends(get_current_user)):
    try:
        if user_logged == 3:
            if not processar_origem(origem):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
            if origem == 1:
                user_client:users_clients_schemas.usersClients = await users_clients_service.select_user_client_by_clientid(key,db)
                return user_client
            if origem == 2:
                user_client:users_clients_schemas.usersClients = await users_clients_service.select_user_client_by_userid(key,db)
                return user_client
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except HTTPException as e:
        if e.status_code == status.HTTP_400_BAD_REQUEST:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ocorreu um erro durante a solicitação.")
        elif e.status_code == status.HTTP_400_BAD_REQUEST:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Você não possui permissão para consultar esses dados.")
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Usuário não encontrado.')

#GET users_clients by user_id     
@router.get('/assigned/{users_client_id}',status_code=status.HTTP_200_OK, response_model=list[clients_schemas.clientsGetNames])
async def get_users_client_byuserid(users_client_id:int,db:AsyncSession = Depends(get_session),user_logged:users_models = Depends(get_current_user)):
    try:
        if user_logged.role_id in (4,3):
            user_clients:users_clients_schemas.usersClientsGetNames = await users_clients_service.select_user_client_by_userid(users_client_id,db)  
            if user_clients:
                clients_data = []
                for client in user_clients:
                    id_client = client.client_id
                    clients = await clients_service.select_client(id_client,db)
                    clients_data.append(
                        {
                            "id": clients.id,
                            "razao_social": clients.razao_social,
                        }
                    )
                return clients_data
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except HTTPException as e:
        if e.status_code == status.HTTP_400_BAD_REQUEST:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ocorreu um erro durante a solicitação.")
        elif e.status_code == status.HTTP_400_BAD_REQUEST:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Você não possui permissão para consultar esses dados.")
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Usuário não encontrado.')
             


#DELETE users_clients
@router.delete('/{users_client_id}',status_code=status.HTTP_202_ACCEPTED)
async def delete_users_client_id(users_client_id:int,db:AsyncSession= Depends(get_session),user_logged :users_models = Depends(get_current_user)):
    try:
        if user_logged == 3:
            await users_clients_service.drop_user_client(users_client_id,db)
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except HTTPException as e:
        if e.status_code != status.HTTP_401_UNAUTHORIZED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ocorreu um erro durante a solicitação.")
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Você não possui permissão para consultar esses dados.")
    
    