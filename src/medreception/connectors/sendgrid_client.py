"""SendGrid email connector (appointment confirmations & reminders)."""
from __future__ import annotations

from ..config import get_settings


def send_email(*, to: str, subject: str, body: str) -> None:
    """Send a transactional email.

    TODO: wire the SendGrid SDK. Kept as a seam so the notification service
    can be unit-tested without network access.
    """
    settings = get_settings()
    _ = (settings.sendgrid_api_key, settings.notifications_from_email)
    _ = (to, subject, body)
    # from sendgrid import SendGridAPIClient
    # SendGridAPIClient(settings.sendgrid_api_key).send(...)
    raise NotImplementedError("SendGrid delivery not wired in the starter")
