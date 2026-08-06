import logging

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from application.container import get_container
from core.configs import settings
from core.cookies import clear_session_cookie, set_session_cookie
from core.deps import get_session
from core.permissions import require_admin, require_operator
from core.rate_limit import rate_limit_public
from domain.exceptions import TokenRevokedError
from infrastructure.persistence.mappers import entity_to_orm
from models.users import Users as users_models
from schemas import auth_schemas, users_schemas
from services.session_service import build_user_session

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/signup", response_model=users_schemas.usersPublic, status_code=status.HTTP_201_CREATED)
async def post_user(
    user: users_schemas.users_create,
    request: Request,
    db: AsyncSession = Depends(get_session),
):
    rate_limit_public(request)
    container = get_container(db)
    entity = await container.register_user.execute(user)
    new_user = entity_to_orm(entity)
    logger.info("Usuário cadastrado: id=%s", new_user.id)
    return new_user


@router.post("/login", response_model=auth_schemas.TokenResponse)
async def login(
    response: Response,
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_session),
):
    rate_limit_public(request)
    container = get_container(db)
    result = await container.login.execute(
        form_data.username,
        form_data.password,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    set_session_cookie(response, result.session_token)
    logger.info("Login bem-sucedido: user_id=%s", result.token_response.user.id)
    return result.token_response


@router.post("/login/json", response_model=auth_schemas.TokenResponse)
async def login_json(
    payload: auth_schemas.LoginRequest,
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_session),
):
    rate_limit_public(request)
    container = get_container(db)
    result = await container.login.execute(
        payload.cpf,
        payload.password,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    set_session_cookie(response, result.session_token)
    logger.info("Login JSON bem-sucedido: user_id=%s", result.token_response.user.id)
    return result.token_response


@router.post("/refresh", response_model=auth_schemas.TokenResponse)
async def refresh_token(
    payload: auth_schemas.RefreshRequest,
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_session),
):
    container = get_container(db)
    try:
        result = await container.refresh.execute(
            payload.refresh_token,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
    except TokenRevokedError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    set_session_cookie(response, result.session_token)
    logger.info("Refresh bem-sucedido: user_id=%s", result.token_response.user.id)
    return result.token_response


@router.post("/logout", response_model=users_schemas.MessageResponse)
async def logout_user(
    response: Response,
    payload: auth_schemas.LogoutRequest | None = None,
    db: AsyncSession = Depends(get_session),
    session_token: str | None = Cookie(None, alias=settings.SESSION_COOKIE_NAME),
):
    container = get_container(db)
    body = payload or auth_schemas.LogoutRequest()
    await container.logout.execute(
        session_token,
        refresh_token=body.refresh_token,
        access_token=body.access_token,
    )
    clear_session_cookie(response)
    logger.info("Logout realizado")
    return users_schemas.MessageResponse(message="Logout realizado com sucesso.")


@router.get("/logged", response_model=auth_schemas.UserSession)
async def get_logged(user_logged: users_models = Depends(require_operator)):
    return build_user_session(user_logged)


@router.get("/", response_model=list[users_schemas.usersGetData])
async def get_users(
    db: AsyncSession = Depends(get_session),
    user_logged: users_models = Depends(require_operator),
):
    container = get_container(db)
    return await container.list_users.execute()


@router.get("/{id_user}", response_model=users_schemas.usersPublic)
async def get_user(
    id_user: int,
    db: AsyncSession = Depends(get_session),
    user_logged: users_models = Depends(require_operator),
):
    container = get_container(db)
    entity = await container.get_user.execute(id_user)
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
    return entity_to_orm(entity)


@router.put("/{id_user}", response_model=users_schemas.usersPublic)
async def put_user(
    id_user: int,
    payload: users_schemas.users_updateForm,
    db: AsyncSession = Depends(get_session),
    user_logged: users_models = Depends(require_admin),
):
    container = get_container(db)
    user_data = payload.model_dump(exclude_unset=True)
    updated = await container.update_user.execute(id_user, user_data)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
    logger.info("Usuário id=%s atualizado por admin user_id=%s", id_user, user_logged.id)
    return entity_to_orm(updated)


@router.delete("/{id_user}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    id_user: int,
    db: AsyncSession = Depends(get_session),
    user_logged: users_models = Depends(require_admin),
):
    container = get_container(db)
    deleted = await container.delete_user.execute(id_user)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
    logger.info("Usuário id=%s desativado por admin user_id=%s", id_user, user_logged.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/forgot-password/{email}", response_model=users_schemas.MessageResponse)
async def forgot_password(email: str, db: AsyncSession = Depends(get_session)):
    container = get_container(db)
    await container.forgot_password.execute(email)
    return users_schemas.MessageResponse(
        message="Se o e-mail existir, enviaremos instruções de redefinição de senha."
    )


@router.post("/reset-password", response_model=users_schemas.MessageResponse)
async def reset_password(
    payload: users_schemas.ResetPasswordRequest,
    db: AsyncSession = Depends(get_session),
):
    container = get_container(db)
    await container.reset_password.execute(payload.token, payload.password)
    return users_schemas.MessageResponse(message="Senha redefinida com sucesso!")
