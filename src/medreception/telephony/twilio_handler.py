"""Twilio inbound-call webhook + media-stream entrypoint.

On an incoming call Twilio POSTs here; we answer with TwiML that opens a
bidirectional media stream to our websocket, where audio is transcribed
(Deepgram), reasoned over (Claude), and spoken back (ElevenLabs).
"""
from __future__ import annotations

from fastapi import APIRouter, Request, Response
from twilio.twiml.voice_response import Connect, VoiceResponse

from ..config import get_settings

router = APIRouter(prefix="/telephony", tags=["telephony"])


@router.post("/incoming")
async def incoming_call(request: Request) -> Response:
    """Answer the call and connect the caller to our media-stream websocket."""
    form = await request.form()
    call_sid = form.get("CallSid", "")

    settings = get_settings()
    ws_base = settings.public_base_url.replace("http", "ws", 1)

    vr = VoiceResponse()
    vr.say("Thanks for calling. One moment while I connect you.")
    connect = Connect()
    connect.stream(url=f"{ws_base}/telephony/media/{call_sid}")
    vr.append(connect)
    return Response(content=str(vr), media_type="application/xml")
