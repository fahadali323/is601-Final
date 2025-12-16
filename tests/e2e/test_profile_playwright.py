from uuid import uuid4

def test_playwright_password_change_flow(page, fastapi_server):
    base = fastapi_server.rstrip('/')

    username = f"pw_ui_{uuid4()}"
    old_password = "UiStart123!"
    new_password = "UiNew456!"

    # -------------------------
    # Register
    # -------------------------
    page.goto(f"{base}/register")
    page.fill('#username', username)
    page.fill('#email', f"{username}@example.com")
    page.fill('#first_name', 'UI')
    page.fill('#last_name', 'Tester')
    page.fill('#password', old_password)
    page.fill('#confirm_password', old_password)
    page.click('button[type="submit"]')

    page.wait_for_selector('#successAlert', timeout=7000)
    page.wait_for_url('**/login', timeout=8000)

    # -------------------------
    # Login (old password)
    # -------------------------
    page.fill('#username', username)
    page.fill('#password', old_password)
    page.click('button[type="submit"]')
    page.wait_for_url('**/dashboard', timeout=8000)

    # -------------------------
    # Change password
    # -------------------------
    page.goto(f"{base}/profile/password")

    page.fill('#currentPassword', old_password)
    page.fill('#newPassword', new_password)
    page.fill('#confirmNewPassword', new_password)
    page.click('button[type="submit"]')

    page.wait_for_selector('#toastContainer', timeout=7000)

    # -------------------------
    # Logout
    # -------------------------
    page.once("dialog", lambda d: d.accept())
    page.click('#layoutLogoutBtn')
    page.wait_for_url('**/login', timeout=8000)

    # -------------------------
    # Old password should FAIL
    # -------------------------
    page.fill('#username', username)
    page.fill('#password', old_password)
    page.click('button[type="submit"]')
    page.wait_for_selector('#errorAlert', timeout=5000)

    # -------------------------
    # New password should PASS ✅
    # -------------------------
    page.fill('#username', username)
    page.fill('#password', new_password)
    page.click('button[type="submit"]')
    page.wait_for_url('**/dashboard', timeout=8000)
