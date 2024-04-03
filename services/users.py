from models.users import Users as users_models
from schemas import users as users_schemas
from sqlalchemy.ext.asyncio import AsyncSession
import datetime
from fastapi import HTTPException,status,Response
from sqlalchemy.future import select
from typing import List

async def register_user(user:users_schemas.users_create,db:AsyncSession) -> users_models: 
    new_user:users_models=users_models(name =user.name,email=user.email,
                                       CPF=user.CPF,password=user.password,updated_at = datetime.date.today()
                                       )
    async with db as session:
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            return new_user

async def select_all_users(db:AsyncSession) -> List[users_schemas.users]:
    async with db as session:
        querie = select(users_models)
        resultset = await session.execute(querie)
        users:List[users_schemas.users] = resultset.scalars().unique().all()
        return users
    
async def select_user(id_user:int,db:AsyncSession) -> users_schemas.users:
    async with db as session:
        querie = select(users_models).filter(users_models.id==id_user)
        resultset = await session.execute(querie)
        user = resultset.scalars().unique().one_or_none()
        
        return user

async def update_user(id_user:int,user:users_schemas.users_update,db:AsyncSession) -> users_schemas.users:
    async with db as session:
        querie = select(users_models).filter(users_models.id == id_user)
        resultset = await session.execute(querie)
        user_up:users_schemas.users = resultset.scalars().unique().one_or_none()
        
        if user_up:
            if user.name:
                user_up.name = user.name
            if user.email:
                user_up.email = user.email
            if user_up.active != user.active:
                user_up.active = user.active
            if user.password:
                user_up.password = user.password
            
            user_up.updated_at = datetime.date.today()
            user_up.updated_by = id_user #usuario_logado() implementar depois do JWT
            
            await session.commit()
            return user_up
    
async def drop_user(id_user:int, db:AsyncSession):
    async with db as session:
        querie = select(users_models).filter(users_models.id==int(id_user))
        result_set = await session.execute(querie)
        user_delete:users_schemas.users = result_set.scalars().unique().one_or_none()
        if user_delete:
            await session.delete(user_delete)
            await session.commit()
            
            
        
        
        


