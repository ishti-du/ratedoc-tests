from playwright.sync_api import Page, expect


BASE_URL = "http://159.89.231.16:3000"
DOCTOR_URL = f"{BASE_URL}/doctor/dr-john-smith-7a055de9"
EMAIL = "erandvejseli@gmail.com"
PASSWORD = "erand2002"


def test_helpful_button_only_works_when_logged_in(page: Page):
    """
    Test that only logged-in users can click Helpful / Not Helpful.
    - Logged-out users should NOT be able to vote (redirected or blocked).
    - Logged-in users SHOULD be able to click Helpful or Not Helpful.
    """
    page.set_default_timeout(20000)

    # ----------------------------------------------------------------
    # PART 1: Logged-out user should NOT be able to vote
    # ----------------------------------------------------------------
    page.goto(DOCTOR_URL, wait_until="domcontentloaded")
    page.wait_for_timeout(2000)

    # Click the Reviews tab first to reveal the Helpful/Not Helpful buttons
    page.locator("button", has_text="Reviews").first.click()
    page.wait_for_timeout(1500)

    # Now find and click the Helpful button
    helpful_btn = page.locator("button", has_text="Helpful (").first
    helpful_btn.wait_for(state="visible", timeout=10000)
    helpful_btn.click()
    page.wait_for_timeout(2000)

    # Should be redirected to /auth
    current_url = page.url
    page_text = page.locator("body").inner_text()

    logged_out_blocked = (
        "/auth" in current_url or
        "sign in" in page_text.lower() or
        "login" in page_text.lower() or
        "log in" in page_text.lower()
    )
    assert logged_out_blocked, (
        f"Expected logged-out user to be blocked from voting, "
        f"but got URL: {current_url}"
    )

    # ----------------------------------------------------------------
    # PART 2: Logged-in user SHOULD be able to vote
    # ----------------------------------------------------------------
    page.goto(f"{BASE_URL}/auth", wait_until="domcontentloaded")
    page.wait_for_timeout(1000)

    page.locator("input[type='email']").fill(EMAIL)
    page.locator("input[type='password']").fill(PASSWORD)

    page.locator("button:has-text('Sign In')").last.click()
    page.wait_for_timeout(2000)

    print("URL after login:", page.url)
    print(page.locator("body").inner_text()[:500])

    # Navigate back to doctor profile
    page.goto(DOCTOR_URL, wait_until="domcontentloaded")
    page.wait_for_timeout(2000)

    # Click Reviews tab to reveal the buttons
    page.locator("button", has_text="Reviews").first.click()
    page.wait_for_timeout(1500)

    # Helpful button should now be visible
    helpful_btn_logged_in = page.locator("button", has_text="Helpful (").first
    helpful_btn_logged_in.wait_for(state="visible", timeout=10000)

    # Click Helpful — should NOT redirect to login
    helpful_btn_logged_in.click()
    page.wait_for_timeout(2000)

    # Confirm we stayed on the doctor page
    assert "/doctor/" in page.url, (
        f"Expected to stay on doctor page after voting, but got: {page.url}"
    )

    # Confirm no login prompt appeared
    assert "/auth" not in page.url, (
        "Logged-in user was unexpectedly redirected to login after voting."
    )