"""FAQ lookup — owner-editable answers, no code change to update."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Faq


def lookup(session: Session, *, clinic_id: str, key: str) -> str | None:
    """Return the answer for a FAQ slug (e.g. "parking"), or None."""
    faq = session.scalar(
        select(Faq).where(Faq.clinic_id == clinic_id, Faq.key == key)
    )
    return faq.answer if faq else None


def all_for_clinic(session: Session, *, clinic_id: str) -> list[Faq]:
    return list(
        session.scalars(select(Faq).where(Faq.clinic_id == clinic_id))
    )


def upsert(
    session: Session, *, clinic_id: str, key: str, question: str, answer: str
) -> Faq:
    faq = session.scalar(
        select(Faq).where(Faq.clinic_id == clinic_id, Faq.key == key)
    )
    if faq is None:
        faq = Faq(clinic_id=clinic_id, key=key, question=question, answer=answer)
        session.add(faq)
    else:
        faq.question = question
        faq.answer = answer
    session.flush()
    return faq
