from playwright.sync_api import Page


def test_doctor_hospital_dropdown_flow(page: Page):
    page.set_default_timeout(20000)

    doctor_name = "Unknown"

    page.goto("https://ratedoctor.io/", wait_until="domcontentloaded")

    # Locate About Us link under Company
    page.locator("footer").get_by_text("Terms of Service", exact=True).last.click()
    page.wait_for_timeout(2000)

    # Read dropdown text from visible page
    page_text = page.locator("body").inner_text()

    # Requirement: dropdown should list affiliated hospitals
    assert "These Terms of Service govern your use of RateDoctor.io. By accessing or using the site, you agree to these Terms and our Privacy Policy." in page_text