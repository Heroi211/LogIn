from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from application.container import get_container
from core.configs import settings
from core.cookies import set_session_cookie
from core.deps import get_session
from infrastructure.auth.google_oauth import DEV_MOCK_ID_TOKEN
from schemas import auth_schemas

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/google/url", response_model=auth_schemas.GoogleAuthUrlResponse)
async def google_auth_url(db: AsyncSession = Depends(get_session)):
    container = get_container(db)
    url, oauth_state = container.google.build_authorization_url()
    mock_token = DEV_MOCK_ID_TOKEN if settings.is_development else None
    return auth_schemas.GoogleAuthUrlResponse(
        url=url,
        state=oauth_state,
        mock_id_token=mock_token,
    )


@router.post("/google/callback", response_model=auth_schemas.TokenResponse)
async def google_callback(
    payload: auth_schemas.GoogleCallbackRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_session),
):
    container = get_container(db)
    result = await container.google_oauth.execute(
        code=payload.code,
        id_token=payload.id_token,
        state=payload.state,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    set_session_cookie(response, result.session_token)
    logger.info("OAuth Google callback: user_id=%s", result.token_response.user.id)
    return result.token_response


@router.post("/google/link", response_model=auth_schemas.UserSession)
async def google_link_account(
    payload: auth_schemas.GoogleLinkRequest,
    db: AsyncSession = Depends(get_session),
):
    container = get_container(db)
    user = await container.google_link.execute(
        cpf=payload.cpf,
        password=payload.password,
        id_token=payload.id_token,
        code=payload.code,
        state=payload.state,
    )
    from services.session_service import build_user_session

    logger.info("Conta Google vinculada: user_id=%s", user.id)
    return build_user_session(user)
