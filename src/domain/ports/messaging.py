from __future__ import annotations

from domain.entities.messaging import PhoneLookupResult, WhatsAppMessage, WhatsAppMessageResult


class WhatsAppMessagingPort:
    """Porta de saída para envio de mensagens WhatsApp (Twilio ou mock)."""

    async def send_message(self, message: WhatsAppMessage) -> WhatsAppMessageResult: ...

    async def send_template(
        self,
        *,
        to: str,
        content_sid: str,
        content_variables: dict[str, str] | None = None,
    ) -> WhatsAppMessageResult: ...

    async def get_message_status(self, message_sid: str) -> WhatsAppMessageResult: ...

    async def lookup_phone(self, phone_number: str) -> PhoneLookupResult | None: ...

    async def notify_admin(self, body: str) -> WhatsAppMessageResult | None: ...
