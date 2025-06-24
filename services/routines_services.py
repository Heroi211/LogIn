from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from models.routines import Routines as routines_models
from models.clients import Clients as clients
from models.users import Users as users
from models.users_clients import Users_Clients as users_clients
from schemas import routines_schemas as routines_schemas
from services.utils import to_utc


async def register_routines(routine:routines_schemas.routines,db:AsyncSession) -> routines_models : 
    
    async with db as session:       
              
        if routine.clients_id:  
            new_routine = routines_models(titulo=routine.titulo,
                                        descricao=routine.descricao,
                                        dt_vencimento=to_utc(routine.dt_vencimento),
                                        prioridade=routine.prioridade,
                                        clients_id=routine.clients_id,
                                        hr_estimativa=routine.hr_estimativa,
                                        status=routine.status)
        session.add(new_routine)
        await session.commit()
        await session.refresh(new_routine)
        return new_routine

async def select_all_routines(db:AsyncSession) -> List[routines_schemas.routines_all]:
    async with db as session:
        querie = select(routines_models).filter(routines_models.active == True)
        resultset = await session.execute(querie)
        routines = resultset.scalars().unique().all()
        
        routines_list = []
        
        for routine in routines:
            client = await session.get(clients, routine.clients_id)
            user = await session.get(users, routine.users_id)
            routines_list
            routines_list.append( 
            {    "id": routine.id,
                "titulo": routine.titulo,
                "descricao": routine.descricao,
                "status": routine.get_status_display(),
                "hr_estimativa": routine.hr_estimativa,
                "hr_real": routine.hr_real,
                "user": user.name if user else None,
                "client": client.razao_social if client else None,
                "cliente_id": routine.clients_id,
                "user_id": routine.users_id,
                "prioridade": routine.get_priority_display(),
                "dt_vencimento": routine.dt_vencimento}
                )
        return routines_list
    
async def select_routine(id_routine:int,db:AsyncSession) -> routines_schemas.routines:
    async with db as session:
        querie = select(routines_models).filter(routines_models.id==id_routine, routines_models.active == True)
        resultset = await session.execute(querie)
        routine:routines_schemas.routines = resultset.scalars().unique().all()
        return routine
    
async def select_routine_conclude(db:AsyncSession) -> routines_schemas.routines:
    async with db as session:
        querie = select(routines_models).filter(routines_models.active == True , routines_models.status == routines_models.STATUS_EXECUTANDO)
        resultset = await session.execute(querie)
        routine:routines_schemas.routines = resultset.scalars().unique().all()  
        return routine

async def select_routine_by_client(id_client:int,db:AsyncSession) -> List[routines_schemas.routines]:
    async with db as session:
        querie = select(routines_models).filter(routines_models.clients_id==id_client, routines_models.active == True)
        resultset = await session.execute(querie)
        routines:List[routines_schemas.routines] = resultset.scalars().unique().all()
        return routines

async def select_routine_by_user(id_user:int,db:AsyncSession) -> List[routines_schemas.routines]:
    async with db as session:
        querie = select(routines_models).filter(routines_models.users_id==id_user, routines_models.active == True)
        resultset = await session.execute(querie)
        routines:List[routines_schemas.routines] = resultset.scalars().unique().all()
        return routines

async def update_routine(id_routine:int,routine:routines_schemas.routinesUpdate,db:AsyncSession) -> bool:
    async with db as session:
        querie = select(routines_models).filter(routines_models.id==id_routine, routines_models.active == True)
        resultset = await session.execute(querie)
        routine_up:routines_models = resultset.scalars().unique().one_or_none()
        
        if routine_up:
            if routine['titulo']:
                routine_up.titulo = routine['titulo']
            if routine['descricao']:
                routine_up.descricao = routine['descricao']
            if routine['dt_vencimento']:
                routine_up.dt_vencimento = to_utc(routine['dt_vencimento'])
            if routine['prioridade']:
                routine_up.prioridade = routine['prioridade']
            if routine['users_id']:
                routine_up.users_id = routine['users_id']
            if routine['clients_id']:
                routine_up.clients_id = routine['clients_id']
            if routine['hr_estimativa']:
                routine_up.hr_estimativa = routine['hr_estimativa']
            if routine['status']:
                routine_up.status = routine['status']
            await session.commit()
            return True
        return False
    
async def drop_routine(id_routine:int,db:AsyncSession) -> bool:
    async with db as session:
        querie = select(routines_models).filter(routines_models.id==id_routine, routines_models.active == True)
        resultset = await session.execute(querie)
        routine:routines_models = resultset.scalars().unique().first()
        
        if routine:
            routine.set_inactive()
            await session.commit()
            return True
        return False
    
async def update_routine_complete(id_routine:int,db:AsyncSession) -> bool:
    async with db as session:
        querie = select(routines_models).filter(routines_models.id==id_routine, routines_models.active == True)
        resultset = await session.execute(querie)
        routine:routines_models = resultset.scalars().unique().one_or_none()
        
        if routine:
            if routine.status == routine.STATUS_EXECUTANDO:
                routine.complete_task()        
                await session.commit()
                return True
        return False
    
async def update_routine_play(user_logged_id,id_routine:int,db:AsyncSession) -> bool:
    async with db as session:
        querie = select(routines_models).filter(routines_models.id==id_routine, routines_models.active == True)
        resultset = await session.execute(querie)
        routine:routines_models = resultset.scalars().unique().one_or_none()
        
        if routine:
            routine.play_task(user_logged_id)     
            await session.commit()
            return True
        return False
    
async def update_routine_pause(id_routine:int,motivo_pause,db:AsyncSession) -> bool:
    async with db as session:
        querie = select(routines_models).filter(routines_models.id==id_routine, routines_models.active == True)
        resultset = await session.execute(querie)
        routine:routines_models = resultset.scalars().unique().one_or_none()
        
        if routine:
            routine.pause_task(motivo=motivo_pause)  # Assuming this method marks the task as inactive
            await session.commit()
            return True 
        return False