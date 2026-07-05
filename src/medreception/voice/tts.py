"""ElevenLabs text-to-speech connector (stub).

Converts the agent's reply text into μ-law audio frames Twilio can play
back on the call.
"""
from __future__ import annotations

from ..config import get_settings


async def synthesize(text: str) -> bytes:
    """Return μ-law/8kHz audio for ``text``.

    TODO: call the ElevenLabs streaming API and transcode to Twilio's format.
    """
    settings = get_settings()
    _ = (settings.elevenlabs_api_key, settings.elevenlabs_voice_id, text)
    raise NotImplementedError("ElevenLabs synthesis not wired in the starter")
