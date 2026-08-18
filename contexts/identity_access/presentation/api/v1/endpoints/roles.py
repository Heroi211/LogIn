from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Request, status

from bootstrap.deps import (
    get_create_role,
    get_deactivate_role,
    get_list_roles,
    get_role_by_id,
    get_set_role_permissions,
    get_update_role,
)
from contexts.identity_access.application.dto.roles import CreateRoleInput, SetRolePermissionsInput, UpdateRoleInput
from contexts.identity_access.application.exceptions import PermissionNotFoundError, RoleNotFoundError
from contexts.identity_access.application.use_cases.roles.create_role import CreateRole
from contexts.identity_access.application.use_cases.roles.deactivate_role import DeactivateRole
from contexts.identity_access.application.use_cases.roles.get_role import GetRoleById
from contexts.identity_access.application.use_cases.roles.list_roles import ListRoles
from contexts.identity_access.application.use_cases.roles.update_role import UpdateRole
from contexts.identity_access.application.use_cases.permissions.set_role_permissions import SetRolePermissions
from contexts.identity_access.domain.entities.user import User
from contexts.identity_access.domain.permission import Permission
from contexts.identity_access.infrastructure.http.audit_context import audit_context_from_request
from contexts.identity_access.infrastructure.security.authorization import require_permission
from contexts.identity_access.presentation.mappers import role_record_to_response
from contexts.identity_access.presentation.schemas import roles_schemas

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=roles_schemas.role)
async def post_role(
    request: Request,
    payload: roles_schemas.role,
    use_case: Annotated[CreateRole, Depends(get_create_role)],
    actor: Annotated[User, Depends(require_permission(Permission.ROLES_CREATE))],
):
    audit_ctx = audit_context_from_request(
        request,
        actor_user_id=actor.id.value if actor.id else None,
    )
    role = await use_case.execute(
        CreateRoleInput(description=payload.description, active=payload.active),
        audit_ctx,
    )
    return role_record_to_response(role)


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[roles_schemas.role])
async def get_roles(
    use_case: Annotated[ListRoles, Depends(get_list_roles)],
    _: Annotated[User, Depends(require_permission(Permission.ROLES_READ))],
):
    return [role_record_to_response(role) for role in await use_case.execute()]


@router.get("/{id_role}", status_code=status.HTTP_200_OK, response_model=roles_schemas.role)
async def get_role(
    id_role: int,
    use_case: Annotated[GetRoleById, Depends(get_role_by_id)],
    _: Annotated[User, Depends(require_permission(Permission.ROLES_READ))],
):
    try:
        return role_record_to_response(await use_case.execute(id_role))
    except RoleNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.put("/{id_role}", status_code=status.HTTP_202_ACCEPTED, response_model=roles_schemas.role)
async def put_role(
    request: Request,
    id_role: int,
    payload: roles_schemas.role_update,
    use_case: Annotated[UpdateRole, Depends(get_update_role)],
    actor: Annotated[User, Depends(require_permission(Permission.ROLES_UPDATE))],
):
    audit_ctx = audit_context_from_request(
        request,
        actor_user_id=actor.id.value if actor.id else None,
    )
    try:
        role = await use_case.execute(
            id_role,
            UpdateRoleInput(description=payload.description, active=payload.active),
            audit_ctx,
        )
        return role_record_to_response(role)
    except RoleNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.put("/{id_role}/permissions", response_model=roles_schemas.role)
async def put_role_permissions(
    request: Request,
    id_role: int,
    payload: roles_schemas.role_permissions_update,
    use_case: Annotated[SetRolePermissions, Depends(get_set_role_permissions)],
    actor: Annotated[User, Depends(require_permission(Permission.ROLES_UPDATE))],
):
    audit_ctx = audit_context_from_request(
        request,
        actor_user_id=actor.id.value if actor.id else None,
    )
    try:
        role = await use_case.execute(
            id_role,
            SetRolePermissionsInput(permissions=tuple(payload.permissions)),
            audit_ctx,
        )
        return role_record_to_response(role)
    except RoleNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.delete("/{id_role}", status_code=status.HTTP_202_ACCEPTED)
async def delete_role(
    request: Request,
    id_role: int,
    use_case: Annotated[DeactivateRole, Depends(get_deactivate_role)],
    actor: Annotated[User, Depends(require_permission(Permission.ROLES_DELETE))],
):
    audit_ctx = audit_context_from_request(
        request,
        actor_user_id=actor.id.value if actor.id else None,
    )
    try:
        await use_case.execute(id_role, audit_ctx)
    except RoleNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
