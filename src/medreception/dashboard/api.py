"""Admin dashboard REST API.

Backs the clinic-facing panel: view appointments & call history, edit FAQs
and business hours, and read basic usage stats. All routes are tenant-scoped
to the authenticated clinic via the JWT.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_session
from ..models import Appointment, CallLog
from ..security import auth
from ..services import faq

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def current_clinic(authorization: str = Header(default="")) -> str:
    """Resolve the clinic_id from the Bearer token, or 401."""
    token = authorization.removeprefix("Bearer ").strip()
    try:
        claims = auth.decode_token(token)
    except Exception as exc:  # jwt.InvalidTokenError et al.
        raise HTTPException(status_code=401, detail="invalid token") from exc
    return claims["clinic_id"]


@router.get("/appointments")
def list_appointments(
    clinic_id: str = Depends(current_clinic),
    session: Session = Depends(get_session),
) -> list[dict]:
    rows = session.scalars(
        select(Appointment).where(Appointment.clinic_id == clinic_id)
    )
    return [
        {"id": a.id, "starts_at": a.starts_at.isoformat(), "status": a.status.value}
        for a in rows
    ]


@router.get("/calls")
def list_calls(
    clinic_id: str = Depends(current_clinic),
    session: Session = Depends(get_session),
) -> list[dict]:
    rows = session.scalars(select(CallLog).where(CallLog.clinic_id == clinic_id))
    return [
        {
            "id": c.id,
            "caller": c.caller_number,
            "status": c.status.value,
            "started_at": c.started_at.isoformat(),
            "duration_seconds": c.duration_seconds,
        }
        for c in rows
    ]


@router.get("/faqs")
def list_faqs(
    clinic_id: str = Depends(current_clinic),
    session: Session = Depends(get_session),
) -> list[dict]:
    return [
        {"key": f.key, "question": f.question, "answer": f.answer}
        for f in faq.all_for_clinic(session, clinic_id=clinic_id)
    ]


@router.get("/stats")
def usage_stats(
    clinic_id: str = Depends(current_clinic),
    session: Session = Depends(get_session),
) -> dict:
    calls = session.scalar(
        select(func.count()).select_from(CallLog).where(CallLog.clinic_id == clinic_id)
    )
    appts = session.scalar(
        select(func.count())
        .select_from(Appointment)
        .where(Appointment.clinic_id == clinic_id)
    )
    return {"total_calls": calls or 0, "total_appointments": appts or 0}
