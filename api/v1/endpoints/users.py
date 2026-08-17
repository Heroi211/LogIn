import datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from core.auth import _generate_access_token
from core.deps import get_current_user, get_session
from core.permissions import Permission, require_permission
from core.security import get_password_hash
from models.users import Users as users_models
from schemas import users_schemas as users_schemas
from services import users_services as users_service

router = APIRouter()


@router.post("/signup", response_model=users_schemas.users, status_code=status.HTTP_201_CREATED)
async def post_user(user: users_schemas.users_create, db: AsyncSession = Depends(get_session)):
    try:
        new_user: users_models = await users_service.register_user(user, db)
        return new_user
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Usuário já cadastrado na base de dados",
        )


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_session)):
    user = await users_service.login_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Dados incorretos")

    return JSONResponse(
        content={"access_token": _generate_access_token(sub=user.id), "token_type": "bearer"},
        status_code=status.HTTP_200_OK,
    )


@router.get("/logged", response_model=users_schemas.users)
async def get_logged(user_logged: users_models = Depends(get_current_user)):
    return user_logged


@router.get("/", response_model=List[users_schemas.usersGetData], status_code=status.HTTP_202_ACCEPTED)
async def get_users(
    db: AsyncSession = Depends(get_session),
    _: users_models = Depends(require_permission(Permission.USERS_READ)),
):
    return await users_service.select_all_users(db)


@router.get("/{id_user}", response_model=users_schemas.users, status_code=status.HTTP_202_ACCEPTED)
async def get_user(
    id_user: int,
    db: AsyncSession = Depends(get_session),
    _: users_models = Depends(require_permission(Permission.USERS_READ)),
):
    user: users_schemas.users = await users_service.select_user(id_user, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
    return user


@router.put("/{id_user}", status_code=status.HTTP_202_ACCEPTED)
async def put_user(
    id_user: int,
    payload: users_schemas.users_updateForm,
    db: AsyncSession = Depends(get_session),
    _: users_models = Depends(require_permission(Permission.USERS_UPDATE)),
):
    user_data = payload.model_dump(exclude_unset=True)
    await users_service.update_user(id_user, user_data, db)


@router.delete("/{id_user}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    id_user: int,
    db: AsyncSession = Depends(get_session),
    _: users_models = Depends(require_permission(Permission.USERS_DELETE)),
):
    await users_service.drop_user(id_user, db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/forgot-password/{email}", status_code=status.HTTP_200_OK)
async def forgot_password(email: str, db: AsyncSession = Depends(get_session)):
    try:
        token = await users_service.generate_reset_token(email, db)
        await users_service.send_email(email, token)
        return {"message": "Email de redefinição de senha enviado!."}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocorreu um erro durante a solicitação.",
        )


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(token: str, password: str, db: AsyncSession = Depends(get_session)):
    try:
        user: users_models = await users_service.get_user_by_reset_token(token, db)
        if not user or user.reset_password_expires < datetime.datetime.now():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido ou expirado")

        user.password = get_password_hash(password)
        user.reset_password_token = None
        user.reset_password_expires = None
        db.add(user)
        await db.commit()
        return {"message": "Senha redefinida com sucesso!"}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ocorreu um erro durante a solicitação.",
        )
