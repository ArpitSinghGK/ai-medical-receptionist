"""Central configuration, loaded from the environment.

Every secret and endpoint is injected via env vars (see ``.env.example``).
Nothing is hardcoded — the same image runs for every clinic.
"""
from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Core ---
    environment: str = Field(default="development")
    database_url: str = Field(default="postgresql+psycopg://localhost/medreception")

    # --- Anthropic (the conversation brain) ---
    anthropic_api_key: str = Field(default="")
    # Haiku is the default for the *real-time* turn: on a live phone call,
    # sub-second latency matters more than raw capability. Swap to
    # claude-sonnet-5 for tougher triage prompts where latency is looser.
    llm_model: str = Field(default="claude-haiku-4-5")
    llm_max_tokens: int = Field(default=1024)

    # --- Telephony (Twilio) ---
    twilio_account_sid: str = Field(default="")
    twilio_auth_token: str = Field(default="")
    twilio_from_number: str = Field(default="")
    # Public wss:// base that Twilio streams media to.
    public_base_url: str = Field(default="http://localhost:8000")

    # --- Speech ---
    deepgram_api_key: str = Field(default="")
    elevenlabs_api_key: str = Field(default="")
    elevenlabs_voice_id: str = Field(default="")

    # --- Notifications ---
    sendgrid_api_key: str = Field(default="")
    notifications_from_email: str = Field(default="noreply@example.com")

    # --- Security ---
    # 32-byte urlsafe base64 key used to encrypt PHI at rest (Fernet).
    phi_encryption_key: str = Field(default="")
    jwt_secret: str = Field(default="change-me")
    jwt_ttl_minutes: int = Field(default=60)


@lru_cache
def get_settings() -> Settings:
    return Settings()
