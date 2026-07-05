"""Appointment booking / rescheduling / cancellation.

PHI (name, phone) is encrypted on the way in and decrypted on the way out.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Appointment, AppointmentStatus
from ..security import crypto

# Fixed-length slots; a real build would read this from clinic settings.
SLOT_MINUTES = 30


def available_slots(
    session: Session, *, clinic_id: str, day: datetime, count: int = 3
) -> list[datetime]:
    """Return the next ``count`` open slots on ``day`` (naive scheduling)."""
    taken = {
        appt.starts_at
        for appt in session.scalars(
            select(Appointment).where(
                Appointment.clinic_id == clinic_id,
                Appointment.status != AppointmentStatus.cancelled,
                Appointment.starts_at >= day.replace(hour=0, minute=0),
                Appointment.starts_at < day.replace(hour=23, minute=59),
            )
        )
    }
    slots: list[datetime] = []
    cursor = day.replace(hour=9, minute=0, second=0, microsecond=0)
    end = day.replace(hour=17, minute=0)
    while cursor < end and len(slots) < count:
        if cursor not in taken:
            slots.append(cursor)
        cursor += timedelta(minutes=SLOT_MINUTES)
    return slots


def book(
    session: Session,
    *,
    clinic_id: str,
    patient_name: str,
    patient_phone: str,
    starts_at: datetime,
) -> Appointment:
    appt = Appointment(
        clinic_id=clinic_id,
        patient_name_enc=crypto.encrypt(patient_name),
        patient_phone_enc=crypto.encrypt(patient_phone),
        starts_at=starts_at,
        status=AppointmentStatus.booked,
    )
    session.add(appt)
    session.flush()
    return appt


def reschedule(
    session: Session, *, appointment_id: str, new_start: datetime
) -> Appointment:
    appt = session.get(Appointment, appointment_id)
    if appt is None:
        raise LookupError(appointment_id)
    appt.starts_at = new_start
    appt.status = AppointmentStatus.rescheduled
    session.flush()
    return appt


def cancel(session: Session, *, appointment_id: str) -> Appointment:
    appt = session.get(Appointment, appointment_id)
    if appt is None:
        raise LookupError(appointment_id)
    appt.status = AppointmentStatus.cancelled
    session.flush()
    return appt
