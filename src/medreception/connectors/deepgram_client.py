"""Deepgram streaming STT connector (stub).

The telephony layer pipes Twilio media-stream audio frames in and receives
interim + final transcripts out. Kept as a seam so dialogue logic can be
tested against canned transcripts.
"""
from __future__ import annotations

from collections.abc import AsyncIterator

from ..config import get_settings


async def transcribe_stream(
    audio_frames: AsyncIterator[bytes],
) -> AsyncIterator[str]:
    """Yield finalized utterances from a stream of μ-law audio frames.

    TODO: open a Deepgram live websocket and forward frames.
    """
    _ = get_settings().deepgram_api_key
    async for _frame in audio_frames:  # pragma: no cover - stub
        raise NotImplementedError("Deepgram live transcription not wired")
        yield ""  # unreachable; keeps this an async generator
