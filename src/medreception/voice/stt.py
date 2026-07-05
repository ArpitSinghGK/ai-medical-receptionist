"""Speech-to-text façade over the Deepgram connector.

Isolates the rest of the app from the specific STT vendor.
"""
from __future__ import annotations

from collections.abc import AsyncIterator

from ..connectors import deepgram_client


async def utterances(audio_frames: AsyncIterator[bytes]) -> AsyncIterator[str]:
    """Yield finalized caller utterances from a Twilio media stream."""
    async for text in deepgram_client.transcribe_stream(audio_frames):
        yield text
