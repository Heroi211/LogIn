from fastapi import APIRouter,HTTPException,status,Depends
from models import users as users_models
from schemas import users as users_schemas
from core.deps import get_session

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
import datetime


router = APIRouter()

@router.post('/', response_model=users_schemas.users,status_code=status.HTTP_202_ACCEPTED)
async def post_user(usuario: users_schemas.users_create,db:AsyncSession = Depends(get_session)):
    new_user:users_models=users_models(nome =usuario.nome,email=usuario.email,
                                       CPF=usuario.CPF,created_at=datetime.datetime.now(),
                                       updated_at=datetime.datetime.now())
    async with db as session:
        try:
            session.add(new_user)
            await session.commit()
            await session.refresh()
            return new_user
        except HTTPException:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Impossível cadastrar usuário, você não tem permissão.')
    
    