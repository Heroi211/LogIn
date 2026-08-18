from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from bootstrap.deps import (
    get_authenticate_user,
    get_block_user,
    get_deactivate_user,
    get_list_users,
    get_my_permissions,
    get_register_user,
    get_request_password_reset,
    get_reset_password,
    get_token_service,
    get_unblock_user,
    get_update_user,
    get_user_by_id,
)
from contexts.identity_access.application.dto.users import RegisterUserInput, UpdateUserInput
from contexts.identity_access.application.exceptions import (
    DuplicateUserError,
    EmailNotConfiguredError,
    EmailSendError,
    InvalidCredentialsError,
    InvalidResetTokenError,
    PasswordResetLimitError,
    UserBlockedError,
    UserInactiveError,
    UserNotFoundError,
    WeakPasswordError,
)
from contexts.identity_access.application.mappers import user_to_record
from contexts.identity_access.application.ports.token_service import TokenService
from contexts.identity_access.application.use_cases.users.authenticate_user import AuthenticateUser
from contexts.identity_access.application.use_cases.users.block_user import BlockUser
from contexts.identity_access.application.use_cases.users.deactivate_user import DeactivateUser
from contexts.identity_access.application.use_cases.users.get_user import GetUserById
from contexts.identity_access.application.use_cases.users.list_users import ListUsers
from contexts.identity_access.application.use_cases.users.register_user import RegisterUser
from contexts.identity_access.application.use_cases.users.request_password_reset import RequestPasswordReset
from contexts.identity_access.application.use_cases.users.reset_password import ResetPassword
from contexts.identity_access.application.use_cases.users.unblock_user import UnblockUser
from contexts.identity_access.application.use_cases.permissions.set_role_permissions import GetMyPermissions
from contexts.identity_access.application.use_cases.users.update_user import UpdateUser
from contexts.identity_access.domain.entities.user import User
from contexts.identity_access.domain.permission import Permission
from contexts.identity_access.infrastructure.http.audit_context import audit_context_from_request
from contexts.identity_access.infrastructure.security.authorization import require_permission
from contexts.identity_access.infrastructure.security.deps import get_current_user
from contexts.identity_access.infrastructure.security.rate_limit import rate_limit
from contexts.identity_access.infrastructure.security.signup_guard import ensure_signup_allowed
from contexts.identity_access.presentation.mappers import user_list_item_to_response, user_record_to_response
from contexts.identity_access.presentation.schemas import users_schemas
from core.configs import settings

router = APIRouter()


@router.post("/signup", response_model=users_schemas.users, status_code=status.HTTP_201_CREATED)
async def post_user(
    request: Request,
    payload: users_schemas.users_create,
    use_case: Annotated[RegisterUser, Depends(get_register_user)],
    _: Annotated[None, Depends(rate_limit("signup", settings.RATE_LIMIT_SIGNUP_PER_MINUTE))],
    __: Annotated[None, Depends(ensure_signup_allowed)],
):
    try:
        user = await use_case.execute(
            RegisterUserInput(
                name=payload.name,
                email=str(payload.email),
                cpf=payload.cpf,
                phone=payload.phone,
                password=payload.password,
            ),
            audit_context_from_request(request),
        )
        return user_record_to_response(user)
    except DuplicateUserError as exc:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=str(exc)) from exc
    except WeakPasswordError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/login")
async def login(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    use_case: Annotated[AuthenticateUser, Depends(get_authenticate_user)],
    tokens: Annotated[TokenService, Depends(get_token_service)],
    _: Annotated[None, Depends(rate_limit("login", settings.RATE_LIMIT_LOGIN_PER_MINUTE))],
):
    try:
        user = await use_case.execute(
            form_data.username,
            form_data.password,
            audit_context_from_request(request),
        )
    except InvalidCredentialsError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return JSONResponse(
        content={
            "access_token": tokens.create_access_token(user.id),
            "refresh_token": tokens.create_refresh_token(user.id),
            "token_type": "bearer",
        },
        status_code=status.HTTP_200_OK,
    )


@router.post("/refresh")
async def refresh_token(
    refresh_token: str,
    tokens: Annotated[TokenService, Depends(get_token_service)],
):
    try:
        user_id = tokens.verify_refresh_token(refresh_token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    return JSONResponse(
        content={
            "access_token": tokens.create_access_token(user_id),
            "refresh_token": tokens.create_refresh_token(user_id),
            "token_type": "bearer",
        },
        status_code=status.HTTP_200_OK,
    )


@router.get("/me/permissions")
async def get_my_permissions_route(
    user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[GetMyPermissions, Depends(get_my_permissions)],
):
    codes = await use_case.execute(user.role_id)
    return {"permissions": codes}


@router.get("/logged", response_model=users_schemas.users)
async def get_logged(user: Annotated[User, Depends(get_current_user)]):
    return user_record_to_response(user_to_record(user))


@router.get("/", response_model=List[users_schemas.usersGetData], status_code=status.HTTP_202_ACCEPTED)
async def get_users(
    use_case: Annotated[ListUsers, Depends(get_list_users)],
    _: Annotated[User, Depends(require_permission(Permission.USERS_READ))],
):
    return [user_list_item_to_response(item) for item in await use_case.execute()]


@router.get("/{id_user}", response_model=users_schemas.users, status_code=status.HTTP_202_ACCEPTED)
async def get_user(
    id_user: int,
    use_case: Annotated[GetUserById, Depends(get_user_by_id)],
    _: Annotated[User, Depends(require_permission(Permission.USERS_READ))],
):
    try:
        return user_record_to_response(await use_case.execute(id_user))
    except UserNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.put("/{id_user}", status_code=status.HTTP_202_ACCEPTED)
async def put_user(
    request: Request,
    id_user: int,
    payload: users_schemas.users_updateForm,
    use_case: Annotated[UpdateUser, Depends(get_update_user)],
    actor: Annotated[User, Depends(require_permission(Permission.USERS_UPDATE))],
):
    data = payload.model_dump(exclude_unset=True)
    audit_ctx = audit_context_from_request(
        request,
        actor_user_id=actor.id.value if actor.id else None,
    )
    try:
        await use_case.execute(
            id_user,
            UpdateUserInput(
                name=data.get("name"),
                email=str(data["email"]) if data.get("email") else None,
                cpf=data.get("cpf"),
                phone=data.get("phone"),
                active=data.get("active"),
            ),
            audit_ctx,
        )
    except UserNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{id_user}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    request: Request,
    id_user: int,
    use_case: Annotated[DeactivateUser, Depends(get_deactivate_user)],
    actor: Annotated[User, Depends(require_permission(Permission.USERS_DELETE))],
):
    audit_ctx = audit_context_from_request(
        request,
        actor_user_id=actor.id.value if actor.id else None,
    )
    try:
        await use_case.execute(id_user, audit_ctx)
    except UserNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{id_user}/block", response_model=users_schemas.users, status_code=status.HTTP_200_OK)
async def block_user(
    request: Request,
    id_user: int,
    use_case: Annotated[BlockUser, Depends(get_block_user)],
    actor: Annotated[User, Depends(require_permission(Permission.USERS_BLOCK))],
):
    audit_ctx = audit_context_from_request(
        request,
        actor_user_id=actor.id.value if actor.id else None,
    )
    try:
        user = await use_case.execute(id_user, audit_ctx)
        return user_record_to_response(user)
    except UserNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{id_user}/unblock", response_model=users_schemas.users, status_code=status.HTTP_200_OK)
async def unblock_user(
    request: Request,
    id_user: int,
    use_case: Annotated[UnblockUser, Depends(get_unblock_user)],
    actor: Annotated[User, Depends(require_permission(Permission.USERS_UNBLOCK))],
):
    audit_ctx = audit_context_from_request(
        request,
        actor_user_id=actor.id.value if actor.id else None,
    )
    try:
        user = await use_case.execute(id_user, audit_ctx)
        return user_record_to_response(user)
    except UserNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/forgot-password/{email}", status_code=status.HTTP_200_OK)
async def forgot_password(
    request: Request,
    email: str,
    use_case: Annotated[RequestPasswordReset, Depends(get_request_password_reset)],
    _: Annotated[None, Depends(rate_limit("forgot-password", settings.RATE_LIMIT_FORGOT_PASSWORD_PER_MINUTE))],
):
    try:
        await use_case.execute(email, audit_context_from_request(request))
        return {"message": "Email de redefinição de senha enviado!."}
    except UserNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PasswordResetLimitError as exc:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(exc)) from exc
    except UserBlockedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except UserInactiveError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except EmailNotConfiguredError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except EmailSendError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocorreu um erro durante a solicitação.",
        ) from exc


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    request: Request,
    token: str,
    password: str,
    use_case: Annotated[ResetPassword, Depends(get_reset_password)],
):
    try:
        await use_case.execute(token, password, audit_context_from_request(request))
        return {"message": "Senha redefinida com sucesso!"}
    except InvalidResetTokenError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except WeakPasswordError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocorreu um erro durante a solicitação.",
        ) from exc
