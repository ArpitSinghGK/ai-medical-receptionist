"""Twilio REST client wrapper (SMS + outbound dial for warm transfer)."""
from __future__ import annotations

from functools import lru_cache

from twilio.rest import Client

from ..config import get_settings


@lru_cache
def get_client() -> Client:
    settings = get_settings()
    return Client(settings.twilio_account_sid, settings.twilio_auth_token)


def send_sms(*, to: str, body: str) -> str:
    """Send an SMS; returns the message SID."""
    settings = get_settings()
    msg = get_client().messages.create(
        to=to, from_=settings.twilio_from_number, body=body
    )
    return msg.sid  # type: ignore[no-any-return]
