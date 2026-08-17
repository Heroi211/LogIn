from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.deps import get_session
from core.permissions import Permission, require_permission
from models.users import Users as users_models
from schemas import roles_schemas as roles_schemas
from services import roles_services as roles_service

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=roles_schemas.role)
async def post_role(
    role: roles_schemas.role,
    db: AsyncSession = Depends(get_session),
    _: users_models = Depends(require_permission(Permission.ROLES_CREATE)),
):
    return await roles_service.register_role(role, db)


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[roles_schemas.role])
async def get_roles(
    db: AsyncSession = Depends(get_session),
    _: users_models = Depends(require_permission(Permission.ROLES_READ)),
):
    return await roles_service.select_all_roles(db)


@router.get("/{id_role}", status_code=status.HTTP_200_OK, response_model=roles_schemas.role)
async def get_role(
    id_role: int,
    db: AsyncSession = Depends(get_session),
    _: users_models = Depends(require_permission(Permission.ROLES_READ)),
):
    role: roles_schemas.role = await roles_service.select_role(id_role, db)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Papel não encontrado.")
    return role


@router.put("/{id_role}", status_code=status.HTTP_202_ACCEPTED, response_model=roles_schemas.role)
async def put_role(
    id_role: int,
    role: roles_schemas.role_update,
    db: AsyncSession = Depends(get_session),
    _: users_models = Depends(require_permission(Permission.ROLES_UPDATE)),
):
    return await roles_service.update_role(id_role, role, db)


@router.delete("/{id_role}", status_code=status.HTTP_202_ACCEPTED)
async def delete_role(
    id_role: int,
    db: AsyncSession = Depends(get_session),
    _: users_models = Depends(require_permission(Permission.ROLES_DELETE)),
):
    await roles_service.drop_role(id_role, db)
