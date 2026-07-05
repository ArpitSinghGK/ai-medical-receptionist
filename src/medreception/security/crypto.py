"""Symmetric encryption for PHI (patient names, phones, transcripts).

Fields are encrypted before they touch the database and decrypted only
when rendered to an authenticated clinic user. The key lives in the
environment (``PHI_ENCRYPTION_KEY``), never in code or the DB.
"""
from __future__ import annotations

from functools import lru_cache

from cryptography.fernet import Fernet

from ..config import get_settings


@lru_cache
def _cipher() -> Fernet:
    key = get_settings().phi_encryption_key
    if not key:
        # Fail loud rather than silently storing plaintext PHI.
        raise RuntimeError("PHI_ENCRYPTION_KEY is not set")
    return Fernet(key.encode())


def encrypt(plaintext: str) -> str:
    return _cipher().encrypt(plaintext.encode()).decode()


def decrypt(token: str) -> str:
    if not token:
        return ""
    return _cipher().decrypt(token.encode()).decode()
