"""FAQ service: owner-editable answers, upsert semantics."""
from __future__ import annotations

from medreception.services import faq


def test_upsert_then_lookup(session, clinic):
    faq.upsert(
        session,
        clinic_id=clinic.id,
        key="parking",
        question="Is there parking?",
        answer="Free lot behind the building.",
    )
    assert faq.lookup(session, clinic_id=clinic.id, key="parking") == (
        "Free lot behind the building."
    )


def test_upsert_updates_existing(session, clinic):
    faq.upsert(session, clinic_id=clinic.id, key="fees", question="Fees?", answer="$80")
    faq.upsert(session, clinic_id=clinic.id, key="fees", question="Fees?", answer="$95")
    assert faq.lookup(session, clinic_id=clinic.id, key="fees") == "$95"
    assert len(faq.all_for_clinic(session, clinic_id=clinic.id)) == 1


def test_lookup_missing_returns_none(session, clinic):
    assert faq.lookup(session, clinic_id=clinic.id, key="unknown") is None
