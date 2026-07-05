"""Fan-out notifications: SMS (Twilio) + email (SendGrid).

Used for booking confirmations, reminders, missed-call alerts, and
new-booking alerts to clinic staff.
"""
from __future__ import annotations

from datetime import datetime

from ..connectors import sendgrid_client, twilio_client


def appointment_confirmation(
    *, patient_phone: str, patient_email: str | None, starts_at: datetime
) -> None:
    when = starts_at.strftime("%A %d %b at %I:%M %p")
    twilio_client.send_sms(
        to=patient_phone,
        body=f"You're booked for {when}. Reply CANCEL to cancel.",
    )
    if patient_email:
        sendgrid_client.send_email(
            to=patient_email,
            subject="Appointment confirmed",
            body=f"Your appointment is confirmed for {when}.",
        )


def missed_call_alert(*, staff_phone: str, caller_number: str) -> None:
    twilio_client.send_sms(
        to=staff_phone,
        body=f"Missed call from {caller_number} — no booking was made.",
    )


def new_booking_alert(*, staff_phone: str, starts_at: datetime) -> None:
    when = starts_at.strftime("%A %d %b at %I:%M %p")
    twilio_client.send_sms(
        to=staff_phone, body=f"New booking via AI receptionist: {when}."
    )
