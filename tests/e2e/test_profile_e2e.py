# tests/e2e/test_profile_e2e.py

from uuid import uuid4
import requests

from app.models.user import User


def register_user(base_url: str, user_data: dict) -> dict:
    r = requests.post(f"{base_url}/auth/register", json=user_data)
    assert r.status_code == 201, f"Register failed: {r.status_code} {r.text}"
    return r.json()


def login_user(base_url: str, username: str, password: str) -> dict:
    r = requests.post(f"{base_url}/auth/login", json={"username": username, "password": password})
    assert r.status_code == 200, f"Login failed: {r.status_code} {r.text}"
    return r.json()


def test_e2e_profile_and_password_flow(fastapi_server: str, db_session):
    base_url = fastapi_server.rstrip("/")

    username = f"e2e_user_{uuid4()}"
    orig_pw = "StartE2E123!"
    new_pw = "NewE2E456!"

    user_payload = {
        "first_name": "E2E",
        "last_name": "Tester",
        "email": f"e2e+{uuid4()}@example.com",
        "username": username,
        "password": orig_pw,
        "confirm_password": orig_pw,
    }

    # Register and login
    reg = register_user(base_url, user_payload)
    tokens = login_user(base_url, username, orig_pw)
    access = tokens["access_token"]
    headers = {"Authorization": f"Bearer {access}", "Content-Type": "application/json"}

    # Update profile
    update_payload = {
        "first_name": "E2EUpdated",
        "last_name": "Tester2",
        "email": f"e2e.updated+{uuid4()}@example.com",
        "username": f"{username}_upd"
    }
    r = requests.put(f"{base_url}/auth/profile", json=update_payload, headers=headers)
    assert r.status_code == 200, f"Profile update failed: {r.status_code} {r.text}"
    updated = r.json()
    assert updated["username"] == update_payload["username"]
    assert updated["email"] == update_payload["email"]

    # Change password
    pw_payload = {
        "current_password": orig_pw,
        "new_password": new_pw,
        "confirm_new_password": new_pw
    }
    r = requests.put(f"{base_url}/auth/password", json=pw_payload, headers=headers)
    assert r.status_code in (200, 201), f"Password change failed: {r.status_code} {r.text}"

    # Old password should fail
    r_old = requests.post(f"{base_url}/auth/login", json={"username": update_payload["username"], "password": orig_pw})
    assert r_old.status_code == 401, "Old password unexpectedly authenticated"

    # New password should succeed
    r_new = requests.post(f"{base_url}/auth/login", json={"username": update_payload["username"], "password": new_pw})
    assert r_new.status_code == 200, f"Login with new password failed: {r_new.status_code} {r_new.text}"
    new_tokens = r_new.json()
    assert "access_token" in new_tokens

    # Verify DB persisted changes and password
    user_id = new_tokens.get("user_id")
    db_user = db_session.query(User).filter(User.id == user_id).first()
    assert db_user is not None
    assert db_user.username == update_payload["username"]
    assert db_user.email == update_payload["email"]
    assert db_user.verify_password(new_pw) is True
    assert db_user.verify_password(orig_pw) is False
