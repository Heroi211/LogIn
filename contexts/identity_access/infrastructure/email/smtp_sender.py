from __future__ import annotations

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from core.configs import settings
from contexts.identity_access.application.exceptions import EmailNotConfiguredError, EmailSendError

logger = logging.getLogger(__name__)


class SmtpEmailSender:
    async def send_password_reset(self, email: str, token: str) -> None:
        sender_email = settings.SMTP_USER
        password = settings.SMTP_PASSWORD

        if not sender_email or not password:
            logger.error("SMTP não configurado: defina SMTP_USER e SMTP_PASSWORD no .env")
            raise EmailNotConfiguredError("Serviço de e-mail não configurado.")

        from_display = settings.email_from_display
        signature = settings.email_signature

        message = MIMEMultipart("alternative")
        message["Subject"] = f"{from_display} — Recuperação de senha"
        message["From"] = f"{from_display} <{sender_email}>"
        message["To"] = email

        reset_link = f"{settings.FRONTEND_URL.rstrip('/')}/resetpassword?email={email}&token={token}"
        text = f"""\
Olá,

Recebemos uma solicitação para redefinir sua senha. Clique no link abaixo:

{reset_link}

Se você não solicitou a redefinição de senha, ignore este e-mail.

Atenciosamente,
{signature}
"""
        message.attach(MIMEText(text, "plain"))

        try:
            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.login(user=sender_email, password=password)
                server.sendmail(sender_email, email, message.as_string())
        except smtplib.SMTPException as exc:
            logger.error("Erro SMTP ao enviar e-mail de recuperação para %s: %s", email, exc)
            raise EmailSendError("Erro ao enviar e-mail.") from exc
        except Exception as exc:
            logger.exception("Erro inesperado ao enviar e-mail de recuperação para %s", email)
            raise EmailSendError("Erro ao enviar e-mail.") from exc

        logger.info("E-mail de recuperação de senha enviado para %s", email)
