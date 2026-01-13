from schemas import users_clients_schemas 
from models.users_clients import Users_Clients as users_clients_models

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from typing import List



async def register_user_client(user_client:users_clients_schemas.usersClients ,db:AsyncSession) -> users_clients_models : 
    
    new_user_client:users_clients_models = users_clients_models(user_id = user_client.user_id,client_id = user_client.client_id)
    
    async with db as session:
        session.add(new_user_client)
        await session.commit()
        await session.refresh(new_user_client)
        return new_user_client

async def select_all_user_clients(db:AsyncSession) -> List[users_clients_schemas.usersClients]:
    async with db as session:
        querie = select(users_clients_models).filter(users_clients_models.active == True)
        resultset = await session.execute(querie)
        user_clients:List[users_clients_schemas.usersClients] = resultset.scalars().unique().all()
        return user_clients
        
        
async def select_user_client_by_clientid(client_id:int,db:AsyncSession) -> users_clients_schemas.usersClients:
    async with db as session:
        querie = select(users_clients_models).filter(users_clients_models.client_id == client_id,users_clients_models.active==True)
        resultset = await session.execute(querie)
        user_client:users_clients_schemas.usersClients = resultset.scalars().unique().all()
        return user_client 

async def select_user_client_by_userid(user_id:int,db:AsyncSession) -> users_clients_schemas.usersClients:
    async with db as session:
        querie = select(users_clients_models).filter(users_clients_models.user_id == user_id,users_clients_models.active==True)
        resultset = await session.execute(querie)
        user_client:users_clients_schemas.usersClients = resultset.scalars().unique().all()
        return user_client

async def drop_user_client(id_user_client:int,db:AsyncSession):
    async with db as session:
        querie = select(users_clients_models).filter(users_clients_models.id == id_user_client,users_clients_models.active==True)
        resultset = await session.execute(querie)
        user_client_del:users_clients_schemas.usersClients = resultset.scalars().unique().one_or_none()
        
        if user_client_del:
            user_client_del.active = False
            await session.commit()
            await session.refresh(user_client_del)
            return user_client_del
            

    
    
    

    
    