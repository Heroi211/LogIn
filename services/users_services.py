import datetime
import logging
import secrets
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.auth import authenticate_user
from core.configs import settings
from core.security import get_password_hash
from models.roles import Roles as roles_models
from models.users import Users as users_models
from schemas import users_schemas as users_schemas

logger = logging.getLogger(__name__)


async def login_user(cpf: str, password: str, db: AsyncSession):
    return await authenticate_user(cpf, password, db)


async def register_user(user: users_schemas.users_create, db: AsyncSession) -> users_models:
    new_user: users_models = users_models(
        name=user.name,
        email=user.email,
        cpf=user.cpf,
        phone=user.phone,
        password=get_password_hash(user.password),
    )
    async with db as session:
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user


async def select_all_users(db: AsyncSession) -> List[users_schemas.usersGetData]:
    async with db as session:
        querie = select(users_models).order_by(users_models.id.asc()).filter(users_models.active == True)
        resultset = await session.execute(querie)
        users: List[users_schemas.usersGetData] = resultset.scalars().unique().all()

        users_list = []
        for user in users:
            role_query = select(roles_models).filter(
                roles_models.id == user.role_id,
                roles_models.active == True,
            )
            role_result = await session.execute(role_query)
            role = role_result.scalars().unique().one_or_none()

            users_list.append(
                {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "cpf": user.cpf,
                    "phone": user.phone,
                    "active": user.active,
                    "role": role.get_role_display() if role else None,
                }
            )

        return users_list


async def select_user(id_user: int, db: AsyncSession) -> users_schemas.users:
    async with db as session:
        querie = select(users_models).filter(users_models.id == id_user, users_models.active == True)
        resultset = await session.execute(querie)
        return resultset.scalars().unique().one_or_none()


async def update_user(id_user: int, user: users_schemas.users_updateForm, db: AsyncSession) -> bool:
    async with db as session:
        querie = select(users_models).filter(users_models.id == id_user, users_models.active == True)
        resultset = await session.execute(querie)
        user_up: users_schemas.users = resultset.scalars().unique().one_or_none()

        if user_up:
            data = user.model_dump(exclude_unset=True)
            if data.get("name"):
                user_up.name = data["name"]
            if data.get("email"):
                user_up.email = data["email"]
            if data.get("active") is not None:
                user_up.active = data["active"]
            if data.get("phone"):
                user_up.phone = data["phone"]
            if data.get("cpf"):
                user_up.cpf = data["cpf"]
            await session.commit()
            return True
        return False


async def drop_user(id_user: int, db: AsyncSession):
    async with db as session:
        querie = select(users_models).filter(users_models.id == int(id_user), users_models.active == True)
        result_set = await session.execute(querie)
        user_delete: users_schemas.users = result_set.scalars().unique().one_or_none()
        if user_delete:
            user_delete.active = False
            await session.commit()
            await session.refresh(user_delete)
            return user_delete


async def get_user_by_email(email: str, db: AsyncSession):
    async with db as session:
        querie = select(users_models).filter(users_models.email == email, users_models.active == True)
        resultset = await session.execute(querie)
        user_up: users_schemas.users = resultset.scalars().unique().one_or_none()
        if user_up:
            return user_up
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


async def generate_reset_token(email: str, db: AsyncSession):
    async with db as session:
        user: users_schemas.users = await get_user_by_email(email, db)
        token = secrets.token_urlsafe(16)
        user.reset_password_token = token
        user.reset_password_expires = datetime.datetime.now() + datetime.timedelta(hours=1)
        session.add(user)
        await session.commit()
        logger.info("Token de redefinição de senha gerado para e-mail=%s", email)
        return token


async def send_email(email: str, token: str):
    sender_email = settings.SMTP_USER
    password = settings.SMTP_PASSWORD

    if not sender_email or not password:
        logger.error("SMTP não configurado: defina SMTP_USER e SMTP_PASSWORD no .env")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Serviço de e-mail não configurado.",
        )

    receiver_email = email

    message = MIMEMultipart("alternative")
    message["Subject"] = "Recuperação de senha"
    message["From"] = f"Cod3Bit Dev Team <{sender_email}>"
    message["To"] = receiver_email

    reset_link = f"{settings.FRONTEND_URL.rstrip('/')}/resetpassword?email={email}&token={token}"
    text = f"""\
    Olá,
    Recebemos uma solicitação para redefinir sua senha. Clique no link abaixo para redefinir sua senha:
    {reset_link}
    Se você não solicitou a redefinição de senha, ignore este e-mail.
    Obrigado,
    Cod3Bit - Development Team
    """
    part = MIMEText(text, "plain")
    message.attach(part)

    try:
        with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.login(user=sender_email, password=password)
            server.sendmail(sender_email, receiver_email, message.as_string())
    except smtplib.SMTPException as e:
        logger.error("Erro SMTP ao enviar e-mail de recuperação para %s: %s", email, e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erro ao enviar e-mail.")
    except Exception:
        logger.exception("Erro inesperado ao enviar e-mail de recuperação para %s", email)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erro ao enviar e-mail.")

    logger.info("E-mail de recuperação de senha enviado para %s", email)
    return True


async def get_user_by_reset_token(token: str, db: AsyncSession):
    async with db as session:
        query = select(users_models).filter(
            users_models.reset_password_token == token,
            users_models.active == True,
        )
        resultset = await session.execute(query)
        user_up: users_models = resultset.scalars().unique().one_or_none()
        if user_up:
            return user_up
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token inválido ou expirado")
