from playwright.sync_api import Page

BASE_URL = "http://159.89.231.16:3000"
ADD_PROVIDER_URL = f"{BASE_URL}/add-provider"
EMAIL = "erandvejseli@gmail.com"
PASSWORD = "erand2002"

DUPLICATE_DOCTOR_NAME = "Dr. John Smith"


def test_duplicate_doctor_submission_should_fail(page: Page):
    """
    Test that submitting a doctor that already exists should fail.
    Duplicate doctors should NOT be submitted for admin approval.
    """
    page.set_default_timeout(20000)

    # Step 1: Log in
    page.goto(f"{BASE_URL}/auth", wait_until="domcontentloaded")
    page.wait_for_timeout(1000)

    page.locator("input[type='email']").fill(EMAIL)
    page.locator("input[type='password']").fill(PASSWORD)
    page.locator("button:has-text('Sign In')").last.click()
    page.wait_for_timeout(2000)

    assert "/auth" not in page.url, f"Login failed. Still on: {page.url}"

    # Step 2: Go to Add Provider and select Doctor
    page.goto(ADD_PROVIDER_URL, wait_until="domcontentloaded")
    page.wait_for_timeout(1500)

    page.locator("button", has_text="Doctor").first.click()
    page.wait_for_timeout(1000)

    # Step 3: Fill duplicate doctor form
    page.locator("input[placeholder='Dr. John Smith']").fill(DUPLICATE_DOCTOR_NAME)

    # Gender
    page.locator("select").nth(0).select_option(index=0)
    page.wait_for_timeout(500)

    # Country
    page.locator("select").nth(1).select_option(label="Bangladesh")
    page.wait_for_timeout(500)

    # City
    page.locator("select").nth(2).select_option(index=1)
    page.wait_for_timeout(500)

    # Department
    page.locator("select").nth(3).select_option(index=1)
    page.wait_for_timeout(500)

    page.locator("input[placeholder='e.g., Cardiology, Neurology']").fill("Dermatology")
    page.locator("input[placeholder='e.g., MBBS, MD, FACC']").fill("MBBS")

    # Step 4: Submit
    page.locator("button", has_text="Submit Doctor").click()
    page.wait_for_timeout(3000)

    # Step 5: Verify duplicate was rejected
    page_text = page.locator("body").inner_text()

    duplicate_error_shown = (
        "already exists" in page_text.lower() or
        "duplicate" in page_text.lower() or
        "already been submitted" in page_text.lower() or
        "doctor already" in page_text.lower() or
        "exists" in page_text.lower() or
        "failed" in page_text.lower() or
        "error" in page_text.lower()
    )

    assert duplicate_error_shown, (
        f"Expected duplicate doctor submission to be rejected, "
        f"but the system allowed it.\nPage snippet:\n{page_text[:300]}"
    )