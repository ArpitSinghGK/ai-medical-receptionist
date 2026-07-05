"""FastAPI application entrypoint.

Wires the telephony webhooks and the admin dashboard API into one app so
the whole architecture is visible from a single place.
"""
from __future__ import annotations

from fastapi import FastAPI

from .dashboard.api import router as dashboard_router
from .telephony.twilio_handler import router as telephony_router


def create_app() -> FastAPI:
    app = FastAPI(title="AI Medical Receptionist", version="0.1.0")
    app.include_router(telephony_router)
    app.include_router(dashboard_router)

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()
