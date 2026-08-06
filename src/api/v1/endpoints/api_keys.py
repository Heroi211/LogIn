import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from application.container import get_container
from core.deps import get_session
from core.permissions import require_admin
from models.users import Users
from schemas import auth_schemas

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=auth_schemas.ApiKeyCreatedResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    payload: auth_schemas.ApiKeyCreateRequest,
    db: AsyncSession = Depends(get_session),
    user_logged: Users = Depends(require_admin),
):
    container = get_container(db)
    full_key, entity = await container.create_api_key.execute(
        user_id=user_logged.id,
        name=payload.name,
        scopes=payload.scopes,
    )
    logger.info("API Key criada id=%s por user_id=%s", entity.id, user_logged.id)
    return auth_schemas.ApiKeyCreatedResponse(
        id=entity.id,
        name=entity.name,
        scopes=entity.scopes,
        key=full_key,
        expires_at=entity.expires_at,
    )


@router.get("/", response_model=list[auth_schemas.ApiKeyListItem])
async def list_api_keys(
    db: AsyncSession = Depends(get_session),
    user_logged: Users = Depends(require_admin),
):
    container = get_container(db)
    keys = await container.api_keys.list_by_user(user_logged.id)
    return [
        auth_schemas.ApiKeyListItem(
            id=key.id,
            name=key.name,
            scopes=key.scopes,
            key_prefix=key.key_prefix,
            expires_at=key.expires_at,
            created_at=key.created_at,
        )
        for key in keys
    ]


@router.delete("/{api_key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    api_key_id: int,
    db: AsyncSession = Depends(get_session),
    user_logged: Users = Depends(require_admin),
):
    container = get_container(db)
    revoked = await container.revoke_api_key.execute(api_key_id, user_logged.id)
    if not revoked:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API Key não encontrada.")
    logger.info("API Key id=%s revogada por user_id=%s", api_key_id, user_logged.id)
