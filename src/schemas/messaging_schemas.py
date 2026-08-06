from pydantic import BaseModel, Field


class WhatsAppSendRequest(BaseModel):
    to: str = Field(..., description="Telefone destino (E.164 ou DDD+número BR)")
    body: str = Field(..., min_length=1, max_length=1600)


class WhatsAppTemplateRequest(BaseModel):
    to: str
    content_sid: str = Field(..., description="Content SID do template aprovado no Twilio")
    content_variables: dict[str, str] | None = None


class WhatsAppMessageResponse(BaseModel):
    sid: str
    status: str
    to: str
    from_number: str
    body: str | None = None
    error_code: int | None = None
    error_message: str | None = None


class WhatsAppNotifyAdminRequest(BaseModel):
    body: str = Field(..., min_length=1, max_length=1600)


class PhoneLookupResponse(BaseModel):
    phone_number: str
    country_code: str | None = None
    carrier_name: str | None = None
    carrier_type: str | None = None
    valid: bool = True
