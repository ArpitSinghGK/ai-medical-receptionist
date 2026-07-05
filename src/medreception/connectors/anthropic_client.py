"""Thin wrapper around the Anthropic SDK.

Centralises model choice, tool-use plumbing, and the system prompt so the
conversation orchestrator stays focused on dialogue state.
"""
from __future__ import annotations

from functools import lru_cache

import anthropic

from ..config import get_settings


@lru_cache
def get_client() -> anthropic.Anthropic:
    # Reads ANTHROPIC_API_KEY from the environment; never hardcode a key.
    return anthropic.Anthropic(api_key=get_settings().anthropic_api_key or None)


def complete_turn(
    *,
    system: str,
    messages: list[dict],
    tools: list[dict],
) -> anthropic.types.Message:
    """One agent turn. Returns the raw Message so the caller can inspect
    ``stop_reason`` and dispatch any ``tool_use`` blocks."""
    settings = get_settings()
    return get_client().messages.create(
        model=settings.llm_model,
        max_tokens=settings.llm_max_tokens,
        system=system,
        tools=tools,
        messages=messages,
    )
