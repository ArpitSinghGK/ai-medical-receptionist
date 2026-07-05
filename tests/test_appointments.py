"""Booking service: PHI is encrypted, slots exclude taken times."""
from __future__ import annotations

from datetime import datetime

from medreception.models import Appointment, AppointmentStatus
from medreception.security import crypto
from medreception.services import appointments


def test_book_encrypts_phi(session, clinic):
    appt = appointments.book(
        session,
        clinic_id=clinic.id,
        patient_name="Jane Doe",
        patient_phone="+15557654321",
        starts_at=datetime(2026, 7, 6, 9, 0),
    )
    # Stored ciphertext must not leak the plaintext...
    assert "Jane Doe" not in appt.patient_name_enc
    # ...but must round-trip.
    assert crypto.decrypt(appt.patient_name_enc) == "Jane Doe"
    assert appt.status is AppointmentStatus.booked


def test_available_slots_excludes_booked(session, clinic):
    day = datetime(2026, 7, 6, 0, 0)
    appointments.book(
        session,
        clinic_id=clinic.id,
        patient_name="A",
        patient_phone="+1",
        starts_at=day.replace(hour=9, minute=0),
    )
    slots = appointments.available_slots(session, clinic_id=clinic.id, day=day, count=3)
    assert day.replace(hour=9, minute=0) not in slots
    assert len(slots) == 3


def test_cancel_sets_status(session, clinic):
    appt = appointments.book(
        session,
        clinic_id=clinic.id,
        patient_name="A",
        patient_phone="+1",
        starts_at=datetime(2026, 7, 6, 10, 0),
    )
    appointments.cancel(session, appointment_id=appt.id)
    refreshed = session.get(Appointment, appt.id)
    assert refreshed.status is AppointmentStatus.cancelled
