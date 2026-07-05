"""Agent wiring: tool schemas are well-formed and the FAQ tool dispatches
to the service without calling the LLM."""
from __future__ import annotations

from medreception.agent import tools
from medreception.agent.conversation import Conversation, TransferRequested
from medreception.services import faq

import pytest


def test_every_tool_has_a_valid_schema():
    names = {t["name"] for t in tools.TOOLS}
    assert names == {
        "check_availability",
        "book_appointment",
        "answer_faq",
        "transfer_to_human",
    }
    for tool in tools.TOOLS:
        schema = tool["input_schema"]
        assert schema["type"] == "object"
        assert set(schema["required"]).issubset(schema["properties"])


def test_answer_faq_tool_reads_from_service(session, clinic):
    faq.upsert(
        session, clinic_id=clinic.id, key="hours", question="Hours?", answer="9-5 M-F"
    )
    convo = Conversation(session=session, clinic_id=clinic.id, clinic_name="Test")
    assert convo._run_tool("answer_faq", {"key": "hours"}) == "9-5 M-F"


def test_transfer_tool_raises_signal(session, clinic):
    convo = Conversation(session=session, clinic_id=clinic.id, clinic_name="Test")
    with pytest.raises(TransferRequested) as exc:
        convo._run_tool("transfer_to_human", {"reason": "urgent"})
    assert exc.value.reason == "urgent"
