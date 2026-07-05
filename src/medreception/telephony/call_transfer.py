"""Warm-transfer a live call to clinic staff.

Invoked when the conversation orchestrator raises ``TransferRequested``
(caller asked for a human, an emergency, or the AI is stuck after two tries).
"""
from __future__ import annotations

from twilio.twiml.voice_response import Dial, VoiceResponse


def transfer_twiml(*, fallback_number: str, reason: str) -> str:
    """Return TwiML that dials the human fallback number."""
    vr = VoiceResponse()
    if reason == "urgent":
        vr.say("Let me get someone to help you right away.")
    else:
        vr.say("Connecting you to a member of our team now.")
    dial = Dial()
    dial.number(fallback_number)
    vr.append(dial)
    return str(vr)
