from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Request, status

from bootstrap.deps import get_create_permission, get_list_permissions
from contexts.identity_access.application.dto.roles import CreatePermissionInput
from contexts.identity_access.application.exceptions import DuplicateUserError
from contexts.identity_access.application.use_cases.permissions.manage_permissions import (
    CreatePermission,
    ListPermissions,
)
from contexts.identity_access.domain.entities.user import User
from contexts.identity_access.domain.permission import Permission
from contexts.identity_access.infrastructure.http.audit_context import audit_context_from_request
from contexts.identity_access.infrastructure.security.authorization import require_permission
from contexts.identity_access.presentation.schemas import permissions_schemas

router = APIRouter()


def _permission_to_response(record) -> dict:
    return {
        "id": record.id,
        "code": record.code,
        "description": record.description,
        "module": record.module,
        "active": record.active,
    }


@router.get("/", response_model=List[permissions_schemas.permission])
async def list_permissions(
    use_case: Annotated[ListPermissions, Depends(get_list_permissions)],
    _: Annotated[User, Depends(require_permission(Permission.PERMISSIONS_READ))],
):
    return [_permission_to_response(p) for p in await use_case.execute()]


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=permissions_schemas.permission)
async def create_permission(
    request: Request,
    payload: permissions_schemas.permission_create,
    use_case: Annotated[CreatePermission, Depends(get_create_permission)],
    actor: Annotated[User, Depends(require_permission(Permission.PERMISSIONS_CREATE))],
):
    audit_ctx = audit_context_from_request(
        request,
        actor_user_id=actor.id.value if actor.id else None,
    )
    try:
        created = await use_case.execute(
            CreatePermissionInput(
                code=payload.code,
                description=payload.description,
                module=payload.module,
            ),
            audit_ctx,
        )
        return _permission_to_response(created)
    except DuplicateUserError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
