import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from application.container import get_container
from core.deps import get_session
from core.permissions import require_admin
from domain.exceptions import MessagingError, WhatsAppNotConfiguredError
from models.users import Users
from schemas import messaging_schemas

logger = logging.getLogger(__name__)

router = APIRouter()


def _to_response(result) -> messaging_schemas.WhatsAppMessageResponse:
    return messaging_schemas.WhatsAppMessageResponse(
        sid=result.sid,
        status=result.status,
        to=result.to,
        from_number=result.from_number,
        body=result.body,
        error_code=result.error_code,
        error_message=result.error_message,
    )


@router.post("/whatsapp", response_model=messaging_schemas.WhatsAppMessageResponse)
async def send_whatsapp(
    payload: messaging_schemas.WhatsAppSendRequest,
    db: AsyncSession = Depends(get_session),
    user_logged: Users = Depends(require_admin),
):
    container = get_container(db)
    try:
        result = await container.send_whatsapp.execute(to=payload.to, body=payload.body)
    except WhatsAppNotConfiguredError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    except MessagingError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    logger.info("WhatsApp enviado por admin user_id=%s sid=%s", user_logged.id, result.sid)
    return _to_response(result)


@router.post("/whatsapp/template", response_model=messaging_schemas.WhatsAppMessageResponse)
async def send_whatsapp_template(
    payload: messaging_schemas.WhatsAppTemplateRequest,
    db: AsyncSession = Depends(get_session),
    user_logged: Users = Depends(require_admin),
):
    container = get_container(db)
    try:
        result = await container.send_whatsapp_template.execute(
            to=payload.to,
            content_sid=payload.content_sid,
            content_variables=payload.content_variables,
        )
    except WhatsAppNotConfiguredError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    except MessagingError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    logger.info("WhatsApp template enviado por admin user_id=%s sid=%s", user_logged.id, result.sid)
    return _to_response(result)


@router.get("/whatsapp/{message_sid}", response_model=messaging_schemas.WhatsAppMessageResponse)
async def get_whatsapp_status(
    message_sid: str,
    db: AsyncSession = Depends(get_session),
    user_logged: Users = Depends(require_admin),
):
    container = get_container(db)
    try:
        result = await container.get_whatsapp_status.execute(message_sid)
    except WhatsAppNotConfiguredError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    except MessagingError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    return _to_response(result)


@router.post("/whatsapp/notify-admin", response_model=messaging_schemas.WhatsAppMessageResponse)
async def notify_admin_whatsapp(
    payload: messaging_schemas.WhatsAppNotifyAdminRequest,
    db: AsyncSession = Depends(get_session),
    user_logged: Users = Depends(require_admin),
):
    container = get_container(db)
    try:
        result = await container.notify_admin_whatsapp.execute(payload.body)
    except WhatsAppNotConfiguredError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    except MessagingError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="TWILIO_ADMIN_PHONE não configurado.",
        )

    logger.info("Feedback admin WhatsApp por user_id=%s sid=%s", user_logged.id, result.sid)
    return _to_response(result)


@router.get("/phone/{phone_number}/lookup", response_model=messaging_schemas.PhoneLookupResponse)
async def lookup_phone(
    phone_number: str,
    db: AsyncSession = Depends(get_session),
    user_logged: Users = Depends(require_admin),
):
    container = get_container(db)
    try:
        result = await container.lookup_phone.execute(phone_number)
    except WhatsAppNotConfiguredError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Número não encontrado ou inválido.")

    return messaging_schemas.PhoneLookupResponse(
        phone_number=result.phone_number,
        country_code=result.country_code,
        carrier_name=result.carrier_name,
        carrier_type=result.carrier_type,
        valid=result.valid,
    )
