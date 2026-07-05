"""Shared test fixtures: an in-memory SQLite DB and a seeded clinic."""
from __future__ import annotations

import os

# Provide a valid Fernet key before any app module imports the settings.
os.environ.setdefault(
    "PHI_ENCRYPTION_KEY", "hlN1S3o9m8xkQ0v2b7c4d6e8f0g2h4j6k8l0m2n4p6q="
)

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from medreception.models import Base, Clinic


@pytest.fixture
def session():
    engine = create_engine("sqlite://", future=True)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    with factory() as s:
        yield s


@pytest.fixture
def clinic(session):
    c = Clinic(name="Test Clinic", phone_number="+15550001111")
    session.add(c)
    session.flush()
    return c
