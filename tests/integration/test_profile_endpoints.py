# tests/integration/test_profile_endpoints.py

import requests
from uuid import uuid4
import pytest

from app.models.user import User


def register_user(base_url: str, user_data: dict) -> dict:
    resp = requests.post(f"{base_url}/auth/register", json=user_data)
    assert resp.status_code == 201, f"Register failed: {resp.status_code} {resp.text}"
    return resp.json()


def login_user(base_url: str, username: str, password: str) -> dict:
    resp = requests.post(f"{base_url}/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200, f"Login failed: {resp.status_code} {resp.text}"
    return resp.json()


def test_update_profile_endpoint(fastapi_server: str, db_session):
    base_url = fastapi_server.rstrip("/")

    user_data = {
        "first_name": "Integration",
        "last_name": "Tester",
        "email": f"int.user+{uuid4()}@example.com",
        "username": f"int_user_{uuid4()}",
        "password": "StartPass123!",
        "confirm_password": "StartPass123!",
    }

    # Register and login
    reg = register_user(base_url, user_data)
    token_data = login_user(base_url, user_data["username"], user_data["password"])
    access_token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    # Update profile fields
    update_payload = {
        "first_name": "Updated",
        "last_name": "Name",
        "email": f"updated+{uuid4()}@example.com",
        "username": f"updated_user_{uuid4()}"
    }

    resp = requests.put(f"{base_url}/auth/profile", json=update_payload, headers=headers)
    assert resp.status_code == 200, f"Profile update failed: {resp.status_code} {resp.text}"
    returned = resp.json()

    # Response should reflect updated fields
    assert returned["first_name"] == update_payload["first_name"]
    assert returned["last_name"] == update_payload["last_name"]
    assert returned["email"] == update_payload["email"]
    assert returned["username"] == update_payload["username"]

    # Verify persisted in DB
    user_id = returned["id"]
    db_user = db_session.query(User).filter(User.id == user_id).first()
    assert db_user is not None
    assert db_user.first_name == update_payload["first_name"]
    assert db_user.last_name == update_payload["last_name"]
    assert db_user.email == update_payload["email"]
    assert db_user.username == update_payload["username"]


def test_change_password_and_relogin(fastapi_server: str, db_session):
    base_url = fastapi_server.rstrip("/")

    username = f"pw_user_{uuid4()}"
    original_password = "OrigPass123!"
    new_password = "NewPass456!"

    user_data = {
        "first_name": "Pw",
        "last_name": "Tester",
        "email": f"pw.user+{uuid4()}@example.com",
        "username": username,
        "password": original_password,
        "confirm_password": original_password,
    }

    reg = register_user(base_url, user_data)

    # Login to get token
    token_data = login_user(base_url, username, original_password)
    access_token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    # Change password
    pw_payload = {
        "current_password": original_password,
        "new_password": new_password,
        "confirm_new_password": new_password
    }
    resp = requests.put(f"{base_url}/auth/password", json=pw_payload, headers=headers)
    assert resp.status_code in (200, 201), f"Password change failed: {resp.status_code} {resp.text}"

    # Attempt to login with old password (should fail)
    r_old = requests.post(f"{base_url}/auth/login", json={"username": username, "password": original_password})
    assert r_old.status_code == 401, "Old password should not authenticate after change"

    # Login with new password (should succeed)
    r_new = requests.post(f"{base_url}/auth/login", json={"username": username, "password": new_password})
    assert r_new.status_code == 200, f"Login with new password failed: {r_new.status_code} {r_new.text}"
    new_tokens = r_new.json()
    assert "access_token" in new_tokens and new_tokens["access_token"], "New access token missing"

    # Confirm DB stored hashed password (verify using model)
    user_id = new_tokens.get("user_id")
    db_user = db_session.query(User).filter(User.id == user_id).first()
    assert db_user is not None
    assert db_user.verify_password(new_password) is True
    assert db_user.verify_password(original_password) is False
