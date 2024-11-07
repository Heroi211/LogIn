from schemas import roles_schemas as roles_schemas
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from models.routines import Routines as routines_models
from schemas import routines_schemas as routines_schemas

async def register_routines(routine:routines_schemas.routines,db:AsyncSession) -> routines_models : 
    
    async with db as session:    
        task = routines_models(titulo=routine.titulo,descricao=routine.descricao,
                                   dt_vencimento=routine.dt_vencimento,prioridade=routine.prioridade,
                                   users_id=routine.users_id,clients_id=routine.clients_id,
                                   hr_estimativa=routine.hr_estimativa,hr_real=routine.hr_real,
                                   status=routine.status)
        session.add(task)
        await session.commit()
        await session.refresh(task)
        return task

async def select_all_routines(db:AsyncSession) -> List[routines_schemas.routines]:
    async with db as session:
        querie = select(routines_models).filter(routines_models.active == True)
        resultset = await session.execute(querie)
        routines:List[routines_schemas.routines] = resultset.scalars().unique().all()
        return routines
    
async def select_routine(id_routine:int,db:AsyncSession) -> routines_schemas.routines:
    async with db as session:
        querie = select(routines_models).filter(routines_models.id==id_routine, routines_models.active == True)
        resultset = await session.execute(querie)
        routine:routines_schemas.routines = resultset.scalars().unique().first()
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

async def update_routine(id_routine:int,routine:routines_schemas.routinesUpdate,db:AsyncSession) -> routines_models:
    async with db as session:
        querie = select(routines_models).filter(routines_models.id==id_routine, routines_models.active == True)
        resultset = await session.execute(querie)
        routine_up:routines_models = resultset.scalars().unique().first()
        
        if routine_up:
            if routine.titulo:
                routine_up.titulo = routine.titulo
            if routine.descricao:
                routine_up.descricao = routine.descricao
            if routine.dt_vencimento:
                routine_up.dt_vencimento = routine.dt_vencimento
            if routine.prioridade:
                routine_up.prioridade = routine.prioridade
            if routine.users_id:
                routine_up.users_id = routine.users_id
            if routine.clients_id:
                routine_up.clients_id = routine.clients_id
            if routine.hr_estimativa:
                routine_up.hr_estimativa = routine.hr_estimativa
            if routine.hr_real:
                routine_up.hr_real = routine.hr_real
            if routine.status:
                routine_up.status = routine.status
            await session.commit()
            await session.refresh(routine)
            return routine
        return None
    
async def drop_routine(id_routine:int,db:AsyncSession) -> bool:
    async with db as session:
        querie = select(routines_models).filter(routines_models.id==id_routine, routines_models.active == True)
        resultset = await session.execute(querie)
        routine:routines_models = resultset.scalars().unique().first()
        
        if routine:
            routine.active = False
            await session.commit()
            return True
        return False