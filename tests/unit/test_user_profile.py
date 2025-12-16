# tests/unit/test_user_profile.py

from datetime import datetime, timezone
import pytest

from app.models.user import User, utcnow


def test_user_update_sets_fields_and_timestamp():
    user = User(
        first_name="Alice",
        last_name="Smith",
        email="alice@example.com",
        username="alice",
        password="hashedpw",
    )

    # ensure updated_at can be set by update()
    prev = user.updated_at
    user.update(first_name="Alicia", email="alicia@example.com")

    assert user.first_name == "Alicia"
    assert user.email == "alicia@example.com"
    assert user.updated_at is not None
    assert isinstance(user.updated_at, datetime)
    # updated_at should be recent (within a minute)
    assert (utcnow() - user.updated_at).total_seconds() < 60


def test_password_hash_and_verify():
    raw = "StrongPass123!"
    hashed = User.hash_password(raw)
    assert hashed != raw

    user = User(
        first_name="Bob",
        last_name="Jones",
        email="bob@example.com",
        username="bobj",
        password=hashed,
    )

    assert user.verify_password(raw) is True
    assert user.verify_password("wrongpass") is False
