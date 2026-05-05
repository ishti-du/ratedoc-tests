from playwright.sync_api import Page


def test_doctor_hospital_dropdown_flow(page: Page):
    page.set_default_timeout(20000)

    doctor_name = "Mohammad Rakibul Hasan Chowdhury"

    page.goto("https://ratedoctor.io/", wait_until="domcontentloaded")

    # Sign in
    page.get_by_text("Sign In", exact=False).first.click()
    page.locator("input[type='email']").fill("parumpudici6@gmail.com")
    page.locator("input[type='password']").fill("Parum1234" \
    "")
    page.locator("button:has-text('Sign In')").last.click()

    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1000)

    # Search doctor
    page.locator("nav").get_by_text("Doctors", exact=True).click()
    page.locator("input").first.fill(doctor_name)
    page.locator("input").first.press("Enter")

    page.wait_for_timeout(2000)

    # Click doctor result
    page.get_by_text(doctor_name, exact=False).first.click()

    page.wait_for_timeout(2000)

    # Open hospital dropdown
    page.get_by_text("Select a hospital", exact=False).click()

    page.wait_for_timeout(2000)

    # Read dropdown text from visible page
    page_text = page.locator("body").inner_text()

    # Requirement: dropdown should list affiliated hospitals
    assert "Chevron Clinical Laboratory, Halishahar" in page_text
    assert "Institute of Health Technology, Chittagong" in page_text

    # Make sure it is only the 2 real hospital options
    assert "Chevron Clinical Laboratory, Halishahar" in page_text
    assert "Institute of Health Technology, Chittagong" in page_text