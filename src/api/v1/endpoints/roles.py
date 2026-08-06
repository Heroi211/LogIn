import logging

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from application.container import get_container
from core.deps import get_session
from core.permissions import require_admin
from models.users import Users as users_models
from schemas import roles_schemas as roles_schemas

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=roles_schemas.role)
async def post_role(
    role: roles_schemas.role,
    db: AsyncSession = Depends(get_session),
    user_logged: users_models = Depends(require_admin),
):
    container = get_container(db)
    logger.info("Role criada por user_id=%s", user_logged.id)
    return await container.create_role.execute(role)


@router.get("/", response_model=list[roles_schemas.role])
async def get_roles(
    db: AsyncSession = Depends(get_session),
    user_logged: users_models = Depends(require_admin),
):
    container = get_container(db)
    return await container.list_roles.execute()


@router.get("/{id_role}", response_model=roles_schemas.role)
async def get_role(
    id_role: int,
    db: AsyncSession = Depends(get_session),
    user_logged: users_models = Depends(require_admin),
):
    container = get_container(db)
    role = await container.get_role.execute(id_role)
    if not role:
        from domain.exceptions import EntityNotFoundError

        raise EntityNotFoundError("Role não encontrada.")
    return role


@router.put("/{id_role}", response_model=roles_schemas.role)
async def put_role(
    id_role: int,
    role: roles_schemas.role_update,
    db: AsyncSession = Depends(get_session),
    user_logged: users_models = Depends(require_admin),
):
    container = get_container(db)
    updated = await container.update_role.execute(id_role, role)
    logger.info("Role id=%s atualizada por user_id=%s", id_role, user_logged.id)
    return updated


@router.delete("/{id_role}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    id_role: int,
    db: AsyncSession = Depends(get_session),
    user_logged: users_models = Depends(require_admin),
):
    container = get_container(db)
    await container.delete_role.execute(id_role)
    logger.info("Role id=%s desativada por user_id=%s", id_role, user_logged.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
