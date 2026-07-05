"""Multi-tenant data model.

Every row that belongs to a clinic carries ``clinic_id`` so a single
deployment serves many clinics with isolated data. Patient-identifying
fields are stored encrypted (see ``security.crypto``).
"""
from __future__ import annotations

import enum
import uuid
from datetime import datetime, time

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _uuid() -> str:
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass


class Clinic(Base):
    """A tenant. Everything else hangs off this."""

    __tablename__ = "clinics"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(200))
    phone_number: Mapped[str] = mapped_column(String(32), unique=True)
    address: Mapped[str] = mapped_column(Text, default="")
    # Number a call is warm-transferred to when a human is needed.
    human_fallback_number: Mapped[str] = mapped_column(String(32), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    users: Mapped[list["ClinicUser"]] = relationship(back_populates="clinic")
    faqs: Mapped[list["Faq"]] = relationship(back_populates="clinic")
    hours: Mapped[list["BusinessHours"]] = relationship(back_populates="clinic")


class ClinicUser(Base):
    """Dashboard login for clinic staff."""

    __tablename__ = "clinic_users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    clinic_id: Mapped[str] = mapped_column(ForeignKey("clinics.id"), index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    clinic: Mapped[Clinic] = relationship(back_populates="users")


class AppointmentStatus(str, enum.Enum):
    booked = "booked"
    rescheduled = "rescheduled"
    cancelled = "cancelled"


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    clinic_id: Mapped[str] = mapped_column(ForeignKey("clinics.id"), index=True)
    # Encrypted at rest.
    patient_name_enc: Mapped[str] = mapped_column(Text)
    patient_phone_enc: Mapped[str] = mapped_column(Text)
    starts_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(AppointmentStatus), default=AppointmentStatus.booked
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Faq(Base):
    """Owner-editable Q&A — no code change needed to update answers."""

    __tablename__ = "faqs"
    __table_args__ = (UniqueConstraint("clinic_id", "key", name="uq_faq_clinic_key"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    clinic_id: Mapped[str] = mapped_column(ForeignKey("clinics.id"), index=True)
    # Stable slug, e.g. "parking", "insurance", "fees".
    key: Mapped[str] = mapped_column(String(64))
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)

    clinic: Mapped[Clinic] = relationship(back_populates="faqs")


class BusinessHours(Base):
    __tablename__ = "business_hours"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    clinic_id: Mapped[str] = mapped_column(ForeignKey("clinics.id"), index=True)
    day_of_week: Mapped[int] = mapped_column()  # 0 = Monday
    opens_at: Mapped[time] = mapped_column(Time)
    closes_at: Mapped[time] = mapped_column(Time)

    clinic: Mapped[Clinic] = relationship(back_populates="hours")


class CallStatus(str, enum.Enum):
    completed = "completed"
    transferred = "transferred"
    missed = "missed"


class CallLog(Base):
    """One row per inbound call. Transcript stored encrypted."""

    __tablename__ = "call_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    clinic_id: Mapped[str] = mapped_column(ForeignKey("clinics.id"), index=True)
    caller_number: Mapped[str] = mapped_column(String(32))
    transcript_enc: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[CallStatus] = mapped_column(
        Enum(CallStatus), default=CallStatus.completed
    )
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    duration_seconds: Mapped[int] = mapped_column(default=0)
