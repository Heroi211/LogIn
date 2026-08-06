from __future__ import annotations

import asyncio
import logging
from datetime import datetime

from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from core.configs import settings
from domain.entities.messaging import PhoneLookupResult, WhatsAppMessage, WhatsAppMessageResult
from domain.exceptions import MessagingError, WhatsAppNotConfiguredError
from infrastructure.messaging.phone_utils import normalize_phone_digits, to_whatsapp_address
from repositories.base import WhatsAppMessagingRepository

logger = logging.getLogger(__name__)


class TwilioWhatsAppRepository(WhatsAppMessagingRepository):
    """Implementação Twilio — Programmable Messaging API (WhatsApp).

    Docs: https://www.twilio.com/docs/whatsapp/api
    """

    def __init__(self) -> None:
        if not settings.twilio_is_configured:
            raise WhatsAppNotConfiguredError(
                "Twilio não configurado: defina TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN e TWILIO_WHATSAPP_FROM."
            )
        self._client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self._from = settings.twilio_whatsapp_from_address

    async def send_message(self, message: WhatsAppMessage) -> WhatsAppMessageResult:
        to_address = to_whatsapp_address(message.to)
        from_address = message.from_number or self._from

        if message.content_sid:
            return await self.send_template(
                to=message.to,
                content_sid=message.content_sid,
                content_variables=message.content_variables or None,
            )

        try:
            result = await asyncio.to_thread(
                self._client.messages.create,
                body=message.body,
                from_=from_address,
                to=to_address,
            )
        except TwilioRestException as exc:
            logger.exception("Twilio WhatsApp send falhou: %s", exc)
            raise MessagingError(f"Falha ao enviar WhatsApp: {exc.msg}") from exc

        return self._map_message(result, fallback_body=message.body)

    async def send_template(
        self,
        *,
        to: str,
        content_sid: str,
        content_variables: dict[str, str] | None = None,
    ) -> WhatsAppMessageResult:
        """Envia mensagem com Content Template (notificações business-initiated)."""
        to_address = to_whatsapp_address(to)
        params: dict = {
            "from_": self._from,
            "to": to_address,
            "content_sid": content_sid,
        }
        if content_variables:
            import json

            params["content_variables"] = json.dumps(content_variables)

        try:
            result = await asyncio.to_thread(self._client.messages.create, **params)
        except TwilioRestException as exc:
            logger.exception("Twilio WhatsApp template falhou: %s", exc)
            raise MessagingError(f"Falha ao enviar template WhatsApp: {exc.msg}") from exc

        return self._map_message(result)

    async def get_message_status(self, message_sid: str) -> WhatsAppMessageResult:
        try:
            result = await asyncio.to_thread(self._client.messages(message_sid).fetch)
        except TwilioRestException as exc:
            logger.exception("Twilio fetch message falhou: sid=%s", message_sid)
            raise MessagingError(f"Mensagem não encontrada: {exc.msg}") from exc

        return self._map_message(result)

    async def lookup_phone(self, phone_number: str) -> PhoneLookupResult | None:
        e164 = normalize_phone_digits(phone_number)
        try:
            info = await asyncio.to_thread(
                self._client.lookups.v1.phone_numbers(e164).fetch,
                type="carrier",
            )
        except TwilioRestException as exc:
            logger.warning("Twilio lookup falhou para %s: %s", e164, exc)
            return None

        carrier = getattr(info, "carrier", None) or {}
        return PhoneLookupResult(
            phone_number=getattr(info, "phone_number", e164) or e164,
            country_code=getattr(info, "country_code", None),
            carrier_name=carrier.get("name") if isinstance(carrier, dict) else None,
            carrier_type=carrier.get("type") if isinstance(carrier, dict) else None,
            valid=True,
            raw={"phone_number": getattr(info, "phone_number", None)},
        )

    async def notify_admin(self, body: str) -> WhatsAppMessageResult | None:
        if not settings.TWILIO_ADMIN_PHONE:
            logger.warning("TWILIO_ADMIN_PHONE não configurado — feedback admin ignorado.")
            return None

        return await self.send_message(
            WhatsAppMessage(to=settings.TWILIO_ADMIN_PHONE, body=body)
        )

    @staticmethod
    def _map_message(result, fallback_body: str | None = None) -> WhatsAppMessageResult:
        return WhatsAppMessageResult(
            sid=result.sid,
            status=getattr(result, "status", "unknown"),
            to=getattr(result, "to", ""),
            from_number=getattr(result, "from_", getattr(result, "from", "")),
            body=getattr(result, "body", None) or fallback_body,
            error_code=getattr(result, "error_code", None),
            error_message=getattr(result, "error_message", None),
            created_at=datetime.utcnow(),
        )
