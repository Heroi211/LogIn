from __future__ import annotations

import logging
import uuid
from datetime import datetime

from core.configs import settings
from domain.entities.messaging import PhoneLookupResult, WhatsAppMessage, WhatsAppMessageResult
from infrastructure.messaging.phone_utils import normalize_phone_digits, to_whatsapp_address
from repositories.base import WhatsAppMessagingRepository
from repositories.mocks.data import get_mock_store

logger = logging.getLogger(__name__)


class MockWhatsAppRepository(WhatsAppMessagingRepository):
    """Mock para ENVIRONMENT=development — loga mensagens em stdout."""

    def __init__(self) -> None:
        self._store = get_mock_store()

    async def send_message(self, message: WhatsAppMessage) -> WhatsAppMessageResult:
        sid = f"SM{uuid.uuid4().hex[:32]}"
        to_address = to_whatsapp_address(message.to)
        from_address = message.from_number or settings.twilio_whatsapp_from_address

        record = WhatsAppMessageResult(
            sid=sid,
            status="queued",
            to=to_address,
            from_number=from_address,
            body=message.body,
            created_at=datetime.utcnow(),
        )
        self._store.whatsapp_messages[sid] = record

        logger.info(
            "ENVIRONMENT=development — WhatsApp mock | sid=%s to=%s body=%s",
            sid,
            to_address,
            message.body,
        )
        return record

    async def send_template(
        self,
        *,
        to: str,
        content_sid: str,
        content_variables: dict[str, str] | None = None,
    ) -> WhatsAppMessageResult:
        body = f"[template:{content_sid}] vars={content_variables or {}}"
        return await self.send_message(
            WhatsAppMessage(to=to, body=body, content_sid=content_sid)
        )

    async def get_message_status(self, message_sid: str) -> WhatsAppMessageResult:
        record = self._store.whatsapp_messages.get(message_sid)
        if not record:
            from domain.exceptions import MessagingError

            raise MessagingError(f"Mensagem mock não encontrada: {message_sid}")
        return record

    async def lookup_phone(self, phone_number: str) -> PhoneLookupResult | None:
        e164 = normalize_phone_digits(phone_number)
        logger.info("ENVIRONMENT=development — phone lookup mock | phone=%s", e164)
        return PhoneLookupResult(
            phone_number=e164,
            country_code="BR",
            carrier_name="Mock Carrier",
            carrier_type="mobile",
            valid=True,
        )

    async def notify_admin(self, body: str) -> WhatsAppMessageResult | None:
        admin_phone = settings.TWILIO_ADMIN_PHONE or "5511999990002"
        logger.info("ENVIRONMENT=development — notify admin mock | phone=%s", admin_phone)
        return await self.send_message(WhatsAppMessage(to=admin_phone, body=body))
