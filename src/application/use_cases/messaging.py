from __future__ import annotations

from dataclasses import dataclass

from domain.entities.messaging import PhoneLookupResult, WhatsAppMessage, WhatsAppMessageResult
from domain.ports.messaging import WhatsAppMessagingPort


@dataclass
class SendWhatsAppMessageUseCase:
    messaging: WhatsAppMessagingPort

    async def execute(self, *, to: str, body: str) -> WhatsAppMessageResult:
        return await self.messaging.send_message(WhatsAppMessage(to=to, body=body))


@dataclass
class SendWhatsAppTemplateUseCase:
    messaging: WhatsAppMessagingPort

    async def execute(
        self,
        *,
        to: str,
        content_sid: str,
        content_variables: dict[str, str] | None = None,
    ) -> WhatsAppMessageResult:
        return await self.messaging.send_template(
            to=to,
            content_sid=content_sid,
            content_variables=content_variables,
        )


@dataclass
class GetWhatsAppMessageStatusUseCase:
    messaging: WhatsAppMessagingPort

    async def execute(self, message_sid: str) -> WhatsAppMessageResult:
        return await self.messaging.get_message_status(message_sid)


@dataclass
class LookupPhoneUseCase:
    messaging: WhatsAppMessagingPort

    async def execute(self, phone_number: str) -> PhoneLookupResult | None:
        return await self.messaging.lookup_phone(phone_number)


@dataclass
class NotifyAdminWhatsAppUseCase:
    """Feedback ao administrador — base para alertas futuros."""

    messaging: WhatsAppMessagingPort

    async def execute(self, body: str) -> WhatsAppMessageResult | None:
        return await self.messaging.notify_admin(body)
