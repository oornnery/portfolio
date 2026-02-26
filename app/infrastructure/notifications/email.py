import asyncio
from dataclasses import dataclass
import logging
import smtplib
from email.message import EmailMessage
import time
from typing import Protocol, Sequence

import httpx

from app.observability.metrics import AppMetrics, get_app_metrics
from app.domain.schemas import ContactForm

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ContactNotificationContext:
    request_id: str
    client_ip: str


@dataclass(frozen=True)
class NotificationChannelResult:
    channel: str
    success: bool
    error: str = ""


@dataclass(frozen=True)
class NotificationDispatchResult:
    results: tuple[NotificationChannelResult, ...]

    @property
    def any_success(self) -> bool:
        return any(result.success for result in self.results)

    @property
    def all_failed(self) -> bool:
        return bool(self.results) and not self.any_success

    @property
    def has_channels(self) -> bool:
        return bool(self.results)

    @property
    def all_skipped(self) -> bool:
        return bool(self.results) and all(
            (not result.success and "not configured" in result.error.lower())
            for result in self.results
        )


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
    ) -> NotificationChannelResult: ...


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
    ) -> NotificationChannelResult:
        if not self._is_configured():
            return NotificationChannelResult(
                channel="webhook",
                success=False,
                error="Webhook channel is not configured.",
            )

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
            return NotificationChannelResult(channel="webhook", success=True)
        except httpx.HTTPStatusError as exc:
            error = f"Webhook returned HTTP {exc.response.status_code}."
            logger.warning(f"{error} for request_id={context.request_id}.")
            return NotificationChannelResult(
                channel="webhook", success=False, error=error
            )
        except httpx.RequestError:
            error = "Webhook request failed."
            logger.exception(f"{error} request_id={context.request_id}.")
            return NotificationChannelResult(
                channel="webhook", success=False, error=error
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
    ) -> NotificationChannelResult:
        if not self._is_configured():
            return NotificationChannelResult(
                channel="email",
                success=False,
                error="Email channel is not configured.",
            )

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
            return NotificationChannelResult(channel="email", success=True)
        except (smtplib.SMTPException, OSError):
            error = "Email notification failed."
            logger.exception(f"{error} request_id={context.request_id}.")
            return NotificationChannelResult(
                channel="email", success=False, error=error
            )


class ContactNotificationService:
    def __init__(
        self,
        channels: Sequence[ContactNotificationChannel],
        metrics: AppMetrics | None = None,
    ) -> None:
        self._channels = tuple(channels)
        self._metrics = metrics or get_app_metrics()

    async def _send_channel_with_metrics(
        self,
        *,
        channel: ContactNotificationChannel,
        contact: ContactForm,
        context: ContactNotificationContext,
    ) -> NotificationChannelResult:
        started_at = time.perf_counter()
        fallback_channel_name = channel.__class__.__name__.lower()
        try:
            result = await channel.send(contact=contact, context=context)
        except BaseException:
            duration_ms = (time.perf_counter() - started_at) * 1000
            self._metrics.record_notification(
                channel=fallback_channel_name,
                outcome="exception",
                duration_ms=duration_ms,
            )
            raise

        duration_ms = (time.perf_counter() - started_at) * 1000
        if result.success:
            outcome = "success"
        elif "not configured" in result.error.lower():
            outcome = "skipped"
        else:
            outcome = "failed"
        self._metrics.record_notification(
            channel=result.channel or fallback_channel_name,
            outcome=outcome,
            duration_ms=duration_ms,
        )
        return result

    async def notify_submission(
        self,
        contact: ContactForm,
        context: ContactNotificationContext,
    ) -> NotificationDispatchResult:
        if not self._channels:
            logger.info("No notification channels registered. Nothing to dispatch.")
            return NotificationDispatchResult(results=())

        logger.info(
            f"Dispatching contact notifications for request_id={context.request_id}."
        )
        channel_results = await asyncio.gather(
            *(
                self._send_channel_with_metrics(
                    channel=channel,
                    contact=contact,
                    context=context,
                )
                for channel in self._channels
            ),
            return_exceptions=True,
        )

        normalized_results: list[NotificationChannelResult] = []
        for result in channel_results:
            if isinstance(result, BaseException):
                normalized_results.append(
                    NotificationChannelResult(
                        channel="unknown",
                        success=False,
                        error=f"Unhandled channel exception: {result.__class__.__name__}",
                    )
                )
                logger.error(
                    f"A notification channel raised an unhandled exception: {result!r}"
                )
                continue
            normalized_results.append(result)

        dispatch_result = NotificationDispatchResult(results=tuple(normalized_results))
        logger.info(
            f"Contact notifications finished for request_id={context.request_id}."
        )
        return dispatch_result
