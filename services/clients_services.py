from models.clients import Clients as clients_models
from models.routines import Routines as routines_models
from schemas import clients_schemas as clients_schemas
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func


async def register_clients(client:clients_schemas.clients,db:AsyncSession) -> clients_models:
    async with db as session:
        new_client = clients_models(cnpj=client.cnpj,
                                    razao_social=client.razao_social,
                                    email=client.email,
                                    phone=client.phone)
        session.add(new_client)
        await session.commit()
        await session.refresh(new_client)
        return new_client

async def select_all_clients(db:AsyncSession) -> clients_schemas.clientsGetData:
    async with db as session:
        querie = select(clients_models).filter(clients_models.active == True)
        resultset = await session.execute(querie)
        clients:clients_schemas.clients = resultset.scalars().unique().all()    
        
        clients_list = []
        
        for client in clients:
            querie = select(func.count(routines_models.id)).filter(routines_models.clients_id == client.id,routines_models.active == True)
            resultset = await session.execute(querie)
            count = resultset.scalar()
            clients_list.append(
                {
                "id": client.id,
                "cnpj": client.cnpj,
                "razao_social": client.razao_social,
                "email": client.email,
                "phone": client.phone,
                "tarefas": count
                }
            )
        
        return clients_list

async def select_client(id_client:int, db:AsyncSession) -> clients_schemas.clients:
    async with db as session:
        querie = select(clients_models).filter(clients_models.active == True, clients_models.id == id_client)
        resultset = await session.execute(querie)
        client:clients_schemas.clients = resultset.scalars().unique().first()
        return client

async def select_client_by_cnpj(cnpj:str, db:AsyncSession) -> clients_schemas.clients:
    async with db as session:
        querie = select(clients_models).filter(clients_models.active == True, clients_models.cnpj==cnpj)
        resultset = await session.execute(querie)
        client:clients_schemas.clients = resultset.scalars().unique().first()
        return client

async def select_client_by_email(email:str, db:AsyncSession) -> clients_schemas.clients:
    async with db as session:
        querie = select(clients_models).filter(clients_models.email==email,clients_models.active == True)
        resultset = await session.execute(querie)
        client:clients_schemas.clients = resultset.scalars().unique().first()
        return client

async def update_client(id_client:int,client:clients_schemas.clientsUpdate,db:AsyncSession) -> bool:
    async with db as session:
        querie = select(clients_models).filter(clients_models.id==id_client,clients_models.active == True)
        resultset = await session.execute(querie)
        client_up:clients_models = resultset.scalars().unique().one_or_none()
        
        if client_up:
            if client.cnpj:
                client_up.cnpj = client.cnpj
            if client.razao_social:
                client_up.razao_social = client.razao_social
            if client.email:
                client_up.email = client.email
            if client.phone:
                client_up.phone = client.phone
            await session.commit()
            await session.refresh(client_up)
            return True
        return False

async def drop_client(id_client:int,db:AsyncSession) -> clients_schemas.clients:
    async with db as session:
        querie = select(clients_models).filter_by(id=id_client,active=True)
        resultset = await session.execute(querie)
        client:clients_models = resultset.scalars().unique().first()
        
        if client:
            client.active = False
            await session.commit()
            await session.refresh(client)
            return client
        return None
