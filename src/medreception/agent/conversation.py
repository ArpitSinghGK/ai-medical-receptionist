"""The conversation orchestrator: the loop that turns caller speech into
actions via Claude tool-use.

This is the heart of the system. The telephony layer feeds it finalized
utterances; it returns the text to speak back (and may raise a transfer
signal). Business logic behind each tool lives in ``services`` — this file
only wires Claude's decisions to those functions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime

from sqlalchemy.orm import Session

from ..connectors import anthropic_client
from ..services import appointments, faq
from . import tools


class TransferRequested(Exception):
    """Raised to signal the telephony layer to warm-transfer the call."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


@dataclass
class Conversation:
    """Holds dialogue state for a single live call."""

    session: Session
    clinic_id: str
    clinic_name: str
    history: list[dict] = field(default_factory=list)

    @property
    def system_prompt(self) -> str:
        return tools.SYSTEM_PROMPT.format(clinic_name=self.clinic_name)

    def handle_utterance(self, text: str) -> str:
        """Run one caller turn to completion and return what to speak back."""
        self.history.append({"role": "user", "content": text})

        while True:
            message = anthropic_client.complete_turn(
                system=self.system_prompt,
                messages=self.history,
                tools=tools.TOOLS,
            )
            self.history.append({"role": "assistant", "content": message.content})

            if message.stop_reason != "tool_use":
                return _spoken_text(message)

            tool_results = [self._dispatch(block) for block in message.content
                            if block.type == "tool_use"]
            self.history.append({"role": "user", "content": tool_results})

    # -- tool dispatch -----------------------------------------------------

    def _dispatch(self, block) -> dict:  # noqa: ANN001 - Anthropic ToolUseBlock
        try:
            result = self._run_tool(block.name, block.input)
            return {"type": "tool_result", "tool_use_id": block.id, "content": result}
        except TransferRequested:
            raise
        except Exception as exc:  # surface a recoverable error to the model
            return {
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": f"Error: {exc}",
                "is_error": True,
            }

    def _run_tool(self, name: str, args: dict) -> str:
        if name == "check_availability":
            day = datetime.combine(date.fromisoformat(args["date"]), datetime.min.time())
            slots = appointments.available_slots(
                self.session, clinic_id=self.clinic_id, day=day
            )
            return ", ".join(s.strftime("%I:%M %p") for s in slots) or "no slots"

        if name == "book_appointment":
            appt = appointments.book(
                self.session,
                clinic_id=self.clinic_id,
                patient_name=args["patient_name"],
                patient_phone=args["patient_phone"],
                starts_at=datetime.fromisoformat(args["starts_at"]),
            )
            return f"Booked (id={appt.id})."

        if name == "answer_faq":
            answer = faq.lookup(self.session, clinic_id=self.clinic_id, key=args["key"])
            return answer or "No answer configured for that question."

        if name == "transfer_to_human":
            raise TransferRequested(args["reason"])

        raise ValueError(f"Unknown tool: {name}")


def _spoken_text(message) -> str:  # noqa: ANN001 - Anthropic Message
    return " ".join(b.text for b in message.content if b.type == "text").strip()
