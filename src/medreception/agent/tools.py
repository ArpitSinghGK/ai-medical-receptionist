"""Claude tool definitions the receptionist can call mid-conversation.

Each tool maps to a service function. Promoting these to explicit tools
(rather than free-text) lets us gate side effects (booking, transfer) and
validate arguments before anything touches the database or the phone line.
"""
from __future__ import annotations

TOOLS: list[dict] = [
    {
        "name": "check_availability",
        "description": (
            "List open appointment slots for a given date. Call this before "
            "offering times to the caller."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "format": "date",
                    "description": "Requested day (YYYY-MM-DD).",
                }
            },
            "required": ["date"],
        },
    },
    {
        "name": "book_appointment",
        "description": "Book an appointment once name, phone and slot are confirmed.",
        "input_schema": {
            "type": "object",
            "properties": {
                "patient_name": {"type": "string"},
                "patient_phone": {"type": "string"},
                "starts_at": {"type": "string", "format": "date-time"},
            },
            "required": ["patient_name", "patient_phone", "starts_at"],
        },
    },
    {
        "name": "answer_faq",
        "description": (
            "Look up a clinic FAQ answer. Keys include: hours, address, "
            "parking, insurance, fees, doctors, services."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"key": {"type": "string"}},
            "required": ["key"],
        },
    },
    {
        "name": "transfer_to_human",
        "description": (
            "Warm-transfer the call to clinic staff. Call this when the caller "
            "asks for a human, the situation is urgent, or you cannot help "
            "after two attempts."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "reason": {
                    "type": "string",
                    "enum": ["requested", "urgent", "unresolved"],
                }
            },
            "required": ["reason"],
        },
    },
]

SYSTEM_PROMPT = (
    "You are the friendly voice receptionist for {clinic_name}. Greet callers "
    "warmly and speak in short, natural sentences. You can check availability, "
    "book appointments, answer clinic FAQs, and transfer to a human. Never give "
    "medical advice. If the caller is distressed or describes an emergency, "
    "transfer to a human immediately."
)
