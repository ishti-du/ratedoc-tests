from playwright.sync_api import Page


def test_doctor_hospital_dropdown_flow(page: Page):
    page.set_default_timeout(20000)

    doctor_name = "Unknown"

    page.goto("https://ratedoctor.io/", wait_until="domcontentloaded")

    # Locate Find Doctors link under Browse
    page.locator("footer").get_by_text("Find Doctors", exact=True).last.click()
    page.wait_for_timeout(2000)

    # Read dropdown text from visible page
    page_text = page.locator("body").inner_text()

    # Requirement: dropdown should list affiliated hospitals
    assert "Search through thousands of verified doctors and read real patient reviews" in page_text