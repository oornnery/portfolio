import asyncio
from dataclasses import dataclass
import logging
import smtplib
from email.message import EmailMessage
from typing import Protocol, Sequence

import httpx

from app.schemas import ContactForm

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ContactNotificationContext:
    request_id: str
    client_ip: str


@dataclass(frozen=True)
class EmailNotificationConfig:
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    smtp_from: str
    smtp_use_tls: bool
    smtp_use_ssl: bool
    smtp_timeout_seconds: int
    to_email: str
    subject_prefix: str
    request_id_header: str


class ContactNotificationChannel(Protocol):
    async def send(
        self,
        contact: ContactForm,
        context: ContactNotificationContext,
    ) -> None: ...


class WebhookNotificationChannel:
    def __init__(
        self,
        webhook_url: str,
        request_id_header: str,
        timeout_seconds: float = 10.0,
    ) -> None:
        self._webhook_url = webhook_url.strip()
        self._request_id_header = request_id_header
        self._timeout_seconds = timeout_seconds

    @staticmethod
    def _is_placeholder(url: str) -> bool:
        return "..." in url

    def _is_configured(self) -> bool:
        if not self._webhook_url:
            return False
        if self._is_placeholder(self._webhook_url):
            logger.info(
                "Skipping webhook notification because URL appears to be a placeholder."
            )
            return False
        return True

    @staticmethod
    def _build_payload(contact: ContactForm) -> dict[str, str]:
        return {
            "content": (
                f"**New portfolio message**\n"
                f"**Name:** {contact.name}\n"
                f"**Email:** {contact.email}\n"
                f"**Subject:** {contact.subject}\n"
                f"**Message:**\n{contact.message}"
            )
        }

    async def send(
        self, contact: ContactForm, context: ContactNotificationContext
    ) -> None:
        if not self._is_configured():
            return

        payload = self._build_payload(contact)
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self._webhook_url,
                    json=payload,
                    headers={self._request_id_header: context.request_id},
                    timeout=self._timeout_seconds,
                )
                response.raise_for_status()
            logger.info(
                f"Webhook notification sent successfully for request_id={context.request_id}."
            )
        except httpx.HTTPStatusError as exc:
            logger.warning(
                f"Webhook notification returned HTTP {exc.response.status_code} "
                f"for request_id={context.request_id}."
            )
        except httpx.RequestError:
            logger.exception(
                f"Webhook notification request failed for request_id={context.request_id}."
            )


class EmailNotificationChannel:
    def __init__(self, config: EmailNotificationConfig) -> None:
        self._config = config

    def _is_configured(self) -> bool:
        is_complete = bool(
            self._config.to_email.strip()
            and self._config.smtp_host.strip()
            and self._config.smtp_from.strip()
        )
        if not is_complete and (
            self._config.to_email or self._config.smtp_host or self._config.smtp_from
        ):
            logger.info(
                "Email notification settings are incomplete; skipping email notification."
            )
        return is_complete

    def _build_subject(self, contact: ContactForm) -> str:
        subject_prefix = self._config.subject_prefix.strip()
        if subject_prefix:
            return f"{subject_prefix} | {contact.subject}"
        return f"Portfolio contact | {contact.subject}"

    @staticmethod
    def _build_body(contact: ContactForm, context: ContactNotificationContext) -> str:
        return (
            f"New portfolio message\n\n"
            f"Name: {contact.name}\n"
            f"Email: {contact.email}\n"
            f"Subject: {contact.subject}\n"
            f"Client IP: {context.client_ip}\n\n"
            f"Message:\n{contact.message}\n"
        )

    def _send_email_sync(self, message: EmailMessage) -> None:
        timeout = self._config.smtp_timeout_seconds
        if self._config.smtp_use_ssl:
            with smtplib.SMTP_SSL(
                self._config.smtp_host,
                self._config.smtp_port,
                timeout=timeout,
            ) as server:
                if self._config.smtp_username:
                    server.login(self._config.smtp_username, self._config.smtp_password)
                server.send_message(message)
            return

        with smtplib.SMTP(
            self._config.smtp_host, self._config.smtp_port, timeout=timeout
        ) as server:
            if self._config.smtp_use_tls:
                server.starttls()
            if self._config.smtp_username:
                server.login(self._config.smtp_username, self._config.smtp_password)
            server.send_message(message)

    async def send(
        self, contact: ContactForm, context: ContactNotificationContext
    ) -> None:
        if not self._is_configured():
            return

        message = EmailMessage()
        message["From"] = self._config.smtp_from
        message["To"] = self._config.to_email
        message["Subject"] = self._build_subject(contact)
        message["Reply-To"] = str(contact.email)
        message[self._config.request_id_header] = context.request_id
        message.set_content(self._build_body(contact, context))

        try:
            await asyncio.to_thread(self._send_email_sync, message)
            logger.info(
                f"Email notification sent successfully for request_id={context.request_id}."
            )
        except (smtplib.SMTPException, OSError):
            logger.exception(
                f"Email notification failed for request_id={context.request_id}."
            )


class ContactNotificationService:
    def __init__(self, channels: Sequence[ContactNotificationChannel]) -> None:
        self._channels = tuple(channels)

    async def notify_submission(
        self,
        contact: ContactForm,
        context: ContactNotificationContext,
    ) -> None:
        if not self._channels:
            logger.info("No notification channels registered. Nothing to dispatch.")
            return

        logger.info(
            f"Dispatching contact notifications for request_id={context.request_id}."
        )
        results = await asyncio.gather(
            *(
                channel.send(contact=contact, context=context)
                for channel in self._channels
            ),
            return_exceptions=True,
        )

        for result in results:
            if isinstance(result, Exception):
                logger.error(
                    f"A notification channel raised an unhandled exception: {result!r}"
                )

        logger.info(
            f"Contact notifications finished for request_id={context.request_id}."
        )
