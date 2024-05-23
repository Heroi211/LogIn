from fastapi import APIRouter,HTTPException,status,Depends,Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from models.users import Users as users_models

from schemas import users_schemas as users_schemas
from core.deps import get_session,get_current_user
from typing import List
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
import datetime
from services import users_services as users_service
from sqlalchemy.exc import IntegrityError
from core.auth import _generate_access_token

router = APIRouter()

#POST user / signup
@router.post('/signup', response_model=users_schemas.users,status_code=status.HTTP_201_CREATED)
async def post_user(user: users_schemas.users_create,db:AsyncSession = Depends(get_session)):
    try:
        new_user:users_models = await users_service.register_user(user,db)
        return new_user
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail="Usuário já cadastrado na base de dados")

#POST Login
@router.post('/login')
async def login(form_data:OAuth2PasswordRequestForm = Depends(),db:AsyncSession = Depends(get_session)):
    user = await users_service.login_user(form_data.username,form_data.password,db)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Dados incorretos")
    
    return JSONResponse(content={"access_token":_generate_access_token(sub=user.id), "token_type":"bearer"},status_code=status.HTTP_200_OK)

#GET Logged
@router.get('/logged', response_model=users_schemas.users)
async def get_logged(user_logged :users_models = Depends(get_current_user)):
    return user_logged

#GET users
@router.get('/', response_model=List[users_schemas.users])
async def get_users(db:AsyncSession = Depends(get_session),user_logged :users_models = Depends(get_current_user)):
    try:
        if user_logged.role_id == 3:
            users:List[users_schemas.users] = await users_service.select_all_users(db)
            return users
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except HTTPException as e:
        if e.status_code != status.HTTP_401_UNAUTHORIZED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ocorreu um erro durante a solicitação.")
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Você não possui permissão para consultar esses dados.")
    
#GET user
@router.get('/{id_user}',response_model=users_schemas.users,status_code=status.HTTP_202_ACCEPTED)
async def get_user(id_user : int, db:AsyncSession = Depends(get_session),user_logged :users_models = Depends(get_current_user)):
    try:
        if user_logged.role_id == 3:
            user:users_schemas.users = await users_service.select_user(id_user,db)
            if user:
                return user
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
        elif e.status_code == status.HTTP_401_UNAUTHORIZED:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Você não possui permissão para consultar esses dados.")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Ocorreu um erro durante a solicitação.")

#PUT user
@router.put('/{id_user}',response_model=users_schemas.users,status_code=status.HTTP_202_ACCEPTED)
async def put_user(id_user:int,user:users_schemas.users_update, db:AsyncSession = Depends(get_session),user_logged :users_models = Depends(get_current_user)): 
    try:
        if user_logged.role_id == 3:
            user_update:users_schemas.users = await users_service.update_user(id_user,user,db)
            return user_update
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except HTTPException as e:
        if e.status_code != status.HTTP_401_UNAUTHORIZED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ocorreu um erro durante a solicitação.")
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Você não possui permissão para consultar esses dados.")
    
#DELETE user
@router.delete('/{id_user}',status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id_user,db:AsyncSession = Depends(get_session),user_logged :users_models = Depends(get_current_user)):
    try:
        if user_logged.role_id == 3:
            await users_service.drop_user(id_user,db)
            return Response (status_code=status.HTTP_204_NO_CONTENT)
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except HTTPException as e:
        if e.status_code != status.HTTP_401_UNAUTHORIZED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ocorreu um erro durante a solicitação.")
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Você não possui permissão para consultar esses dados.")

