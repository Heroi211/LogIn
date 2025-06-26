from fastapi import APIRouter,HTTPException,status,Depends
from models.users import Users as users_models
from models.routines import Routines as routines_models

from schemas import users_schemas as users_schemas
from schemas import clients_schemas as clients_schemas
from schemas import users_clients_schemas as users_clients_schemas
from schemas import routines_schemas as routines_schemas

from core.deps import get_session,get_current_user
from typing import List
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from services import routines_services as routines_service
from typing import Optional

router = APIRouter()

#POST routine
@router.post('/',status_code=status.HTTP_201_CREATED,response_model=routines_schemas.routines)
async def post_routine(routine:routines_schemas.routines,db:AsyncSession = Depends(get_session),user_logged :users_models = Depends(get_current_user)):
    try:
        if user_logged:
            new_routine:routines_models = await routines_service.register_routines(routine,db)
            return new_routine
        else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except HTTPException as e:
        if e.status_code != status.HTTP_401_UNAUTHORIZED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ocorreu um erro durante a solicitação.")
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Você não possui permissão para consultar esses dados.")
    

#GET routines
@router.get('/',status_code=status.HTTP_200_OK,response_model=List[routines_schemas.routines_all])
async def get_routines(db:AsyncSession = Depends(get_session),user_logged :users_models = Depends(get_current_user)):
    try:
        if user_logged:
            routines:List[routines_schemas.routines_all] = await routines_service.select_all_routines(db)
            return routines
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except HTTPException as e:
        if e.status_code != status.HTTP_401_UNAUTHORIZED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ocorreu um erro durante a solicitação.")
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Você não possui permissão para consultar esses dados.")

#GET routines
@router.get('/routines',status_code=status.HTTP_200_OK, response_model=routines_schemas.routines)
async def get_routine(routine_id:Optional[int], db:AsyncSession = Depends(get_session),user_logged :users_models = Depends(get_current_user)):
    try:
        if user_logged:
            routine:routines_schemas.routines = await routines_service.select_routine(routine_id,db)
            if routine:
                return routine
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

#GET routines assigned
@router.get('/conclude',status_code=status.HTTP_200_OK, response_model=List[routines_schemas.routinesGetNames])
async def get_routine(db:AsyncSession = Depends(get_session),user_logged :users_models = Depends(get_current_user)):
    try:
        if user_logged:
            routines_data = []
            routines:routines_schemas.routines = await routines_service.select_routine_conclude(db)
            if routines:
                for routine in routines:
                    routines_data.append(
                            {
                                "id": routine.id,
                                "titulo": routine.titulo,
                            }
                        )
                return routines_data
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

#GET Routine by client
@router.get('/client',status_code=status.HTTP_200_OK, response_model=routines_schemas.routines)
async def get_routine_by_client(client_id:Optional[int], db:AsyncSession = Depends(get_session),user_logged :users_models = Depends(get_current_user)):
    try:
        if user_logged:
            routine:routines_schemas.routines = await routines_service.select_routine_by_client(client_id,db)
            if routine:
                return routine
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
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Cliente não encontrado.')

#GET Routine by user
@router.get('/user',status_code=status.HTTP_200_OK, response_model=routines_schemas.routines)
async def get_routine_by_user(user_id:Optional[int], db:AsyncSession = Depends(get_session),user_logged :users_models = Depends(get_current_user)):
    try:
        if user_logged:
            routine:routines_schemas.routines = await routines_service.select_routine_by_user(user_id,db)
            if routine:
                return routine
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

#PUT routines
@router.put('/{routine_id}',status_code=status.HTTP_202_ACCEPTED)
async def put_routines(routine_id:int,payload: routines_schemas.routinesUpdate,db:AsyncSession = Depends(get_session),user_logged :users_models = Depends(get_current_user)):
    try:
        if user_logged:
            routine_id = routine_id
            routine_data = payload.model_dump(exclude_unset=True)
            await routines_service.update_routine(routine_id,routine_data,db)
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except HTTPException as e:
        if e.status_code != status.HTTP_401_UNAUTHORIZED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ocorreu um erro durante a solicitação.")
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Você não possui permissão para consultar esses dados.")



#PUT COMPLETE    
@router.put('/{routine_id}/complete',status_code=status.HTTP_202_ACCEPTED)
async def put_routine_complete(routine_id:int,db:AsyncSession = Depends(get_session),user_logged :users_models = Depends(get_current_user)):
    try:
        if user_logged:
            await routines_service.update_routine_complete(routine_id,db)
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except HTTPException as e:
        if e.status_code != status.HTTP_401_UNAUTHORIZED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ocorreu um erro durante a solicitação.")
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Você não possui permissão para consultar esses dados.")

#PUT PLAY
@router.put('/{routine_id}/play',status_code=status.HTTP_202_ACCEPTED)
async def put_routine_play(routine_id:int, db:AsyncSession = Depends(get_session),user_logged :users_models = Depends(get_current_user)):
    try:
        if user_logged:
            await routines_service.update_routine_play(user_logged.id,routine_id,db)
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except HTTPException as e:
        if e.status_code != status.HTTP_401_UNAUTHORIZED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ocorreu um erro durante a solicitação.")
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Você não possui permissão para consultar esses dados.")

#PUT Pause
@router.put('/pause/',status_code=status.HTTP_202_ACCEPTED)
async def put_routine_pause(payload: routines_schemas.PauseRoutine, db:AsyncSession = Depends(get_session),user_logged :users_models = Depends(get_current_user)):
    try:
        if user_logged:
            routine_id = payload.id
            motivo_pause = payload.motivo
            await routines_service.update_routine_pause(routine_id,motivo_pause,db)
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except HTTPException as e:
        if e.status_code != status.HTTP_401_UNAUTHORIZED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ocorreu um erro durante a solicitação.")
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Você não possui permissão para consultar esses dados.")


#DELETE routines
@router.delete('/',status_code=status.HTTP_202_ACCEPTED)
async def delete_routine(routine_id:int,db:AsyncSession= Depends(get_session),user_logged :users_models = Depends(get_current_user)):
    try:
        if user_logged:
            await routines_service.drop_routine(routine_id,db)
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except HTTPException as e:
        if e.status_code != status.HTTP_401_UNAUTHORIZED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ocorreu um erro durante a solicitação.")
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Você não possui permissão para consultar esses dados.")
    
    