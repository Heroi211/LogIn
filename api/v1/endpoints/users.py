from fastapi import APIRouter,HTTPException,status,Depends,Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from models.users import Users as users_models

from schemas import users as users_schemas
from core.deps import get_session,get_current_user
from typing import List
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
import datetime
from services import users as users_service
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
    user = await users_service.login_user(form_data.CPF,form_data.password,db)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Dados incorretos")
    
    return JSONResponse(content={"access_token":_generate_access_token(sub=user.id), "token_type":"bearer"},status_code=status.HTTP_200_OK)

#GET Logged
@router.get('/logged', response_model=users_schemas.users)
def get_logged(user_logged :users_models = Depends(get_current_user)):
    return user_logged

#GET users
@router.get('/', response_model=List[users_schemas.users])
async def get_users(db:AsyncSession = Depends(get_session)):
    users:List[users_schemas.users] = await users_service.select_all_users(db)
    return users
    
#GET user
@router.get('/{id_user}',response_model=users_schemas.users,status_code=status.HTTP_202_ACCEPTED)
async def get_user(id_user : int, db:AsyncSession = Depends(get_session)):
    user:users_schemas.users = await users_service.select_user(id_user,db)
    if user:
        return user
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Usuário não encotrado.')

#PUT user
@router.put('/{id_user}',response_model=users_schemas.users,status_code=status.HTTP_202_ACCEPTED)
async def put_user(id_user:int,user:users_schemas.users_update, db:AsyncSession = Depends(get_session)):
    user_update:users_schemas.users = await users_service.update_user(id_user,user,db)
    return user_update

#DELETE user
@router.delete('/{id_user}',status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id_user,db:AsyncSession = Depends(get_session)):
    try:
        await users_service.drop_user(id_user,db)
        return Response (status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail='Erro que ninguém sabe de onde vem')
   

