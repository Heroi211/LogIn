import logging

from fastapi import APIRouter

from core.configs import settings
from infrastructure.auth.google_oauth import DEV_MOCK_ID_TOKEN
from schemas.meta_schemas import AuthMeta, MessagingMeta, MetaResponse, OAuthMeta

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/meta", response_model=MetaResponse, tags=["meta"])
async def api_meta():
    """Informações para bootstrap do frontend (URLs de auth, ambiente, docs)."""
    base = settings.PROJECT_VERSION.rstrip("/")
    response = MetaResponse(
        name=settings.PROJECT_NAME,
        api_version=settings.PROJECT_VERSION,
        environment=settings.ENVIRONMENT,
        cors_origins=settings.cors_origins_list,
        auth=AuthMeta(
            login_form=f"{base}/users/login",
            login_json=f"{base}/users/login/json",
            refresh=f"{base}/users/refresh",
            logout=f"{base}/users/logout",
            logged=f"{base}/users/logged",
            signup=f"{base}/users/signup",
            google_url=f"{base}/auth/google/url",
            google_callback=f"{base}/auth/google/callback",
            google_link=f"{base}/auth/google/link",
            auth_priority="api_key > session_cookie > jwt_bearer",
            session_cookie=settings.SESSION_COOKIE_NAME,
            api_key_header=settings.API_KEY_HEADER,
        ),
        oauth=OAuthMeta(
            google_configured=bool(settings.GOOGLE_CLIENT_ID),
            dev_mock_id_token=DEV_MOCK_ID_TOKEN if settings.is_development else None,
        ),
        messaging=MessagingMeta(
            whatsapp_send=f"{base}/messaging/whatsapp",
            whatsapp_template=f"{base}/messaging/whatsapp/template",
            whatsapp_notify_admin=f"{base}/messaging/whatsapp/notify-admin",
            twilio_configured=settings.twilio_is_configured,
            twilio_live=settings.twilio_use_live,
        ),
    )
    logger.debug("meta requested | environment=%s", settings.ENVIRONMENT)
    return response
