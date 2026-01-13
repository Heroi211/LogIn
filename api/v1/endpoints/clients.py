from fastapi import APIRouter,HTTPException,status,Depends
from core.deps import get_session,get_current_user
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from services import clients_services as clients_service
from models import clients as clients_models
from schemas import clients_schemas as clients_schemas
from sqlalchemy.exc import IntegrityError
from models import users as users_models
from typing import Optional

router = APIRouter()

#POST Client
@router.post('/', response_model=clients_schemas.clients,status_code=status.HTTP_201_CREATED)
async def post_client(client: clients_schemas.clients,db:AsyncSession = Depends(get_session)):
    try:
        
        new_client:clients_models = await clients_service.register_clients(client,db) 
        return new_client
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail="Usuário já cadastrado na base de dados")

#GET Clients
@router.get('/',status_code=status.HTTP_200_OK,response_model=List[clients_schemas.clientsGetData])
async def get_clients(db:AsyncSession = Depends(get_session),user_logged :users_models = Depends(get_current_user)):
    try:
        if user_logged:
            clients:List[clients_schemas.clientsGetData] = await clients_service.select_all_clients(db)
            return clients
        else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except HTTPException as e:
        if e.status_code != status.HTTP_401_UNAUTHORIZED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ocorreu um erro durante a solicitação.")
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Você não possui permissão para consultar esses dados.")

#GET client by key
@router.get('/{key}',status_code=status.HTTP_200_OK, response_model=clients_schemas.clients)
async def get_client_by_id(key:int, db:AsyncSession = Depends(get_session),user_logged :users_models = Depends(get_current_user)):
    try:
        if user_logged:
            if len(str(key)) == 14:
                client:clients_schemas.clients = await clients_service.select_client_by_cnpj(str(key),db)
            else:
                client:clients_schemas.clients = await clients_service.select_client(key,db)
            if client:
                return client
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
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='cliente não encontrado.')

#PUT client
@router.put('/{client_id}',status_code=status.HTTP_202_ACCEPTED)
async def put_client(client_id: int, client:clients_schemas.clientsUpdate,db:AsyncSession = Depends(get_session),user_logged :users_models = Depends(get_current_user)):
    try:
        if user_logged:
           await clients_service.update_client(client_id,client,db)
           
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except HTTPException as e:
        if e.status_code != status.HTTP_401_UNAUTHORIZED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ocorreu um erro durante a solicitação.")
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Você não possui permissão para consultar esses dados.")
    
    
    

#DELETE role
@router.delete('/{client_id}',status_code=status.HTTP_202_ACCEPTED)
async def delete_client(client_id:int,db:AsyncSession= Depends(get_session),user_logged :users_models = Depends(get_current_user)):
    try:
        if user_logged:
            await clients_service.drop_client(client_id,db)
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except HTTPException as e:
        if e.status_code != status.HTTP_401_UNAUTHORIZED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ocorreu um erro durante a solicitação.")
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Você não possui permissão para consultar esses dados.")
    
    