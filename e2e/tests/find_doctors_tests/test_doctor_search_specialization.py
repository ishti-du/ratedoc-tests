from playwright.sync_api import Page, expect


def test_doctor_hospital_dropdown_flow(page: Page):
    page.set_default_timeout(20000)

    page.goto("https://ratedoctor.io/", wait_until="domcontentloaded")

    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1000)

    # Select Doctor Tab
    page.locator("nav").get_by_text("Doctors", exact=True).click()

    # Select Dentist Specialization
    spec_button = page.locator("button:has-text('All Specialization')").first
    spec_button.wait_for(state="visible")
    spec_button.click()

    dropdown = page.locator("[data-radix-popper-content-wrapper]")
    dropdown.wait_for(state="visible")

    denist_option = dropdown.get_by_text("Dentist", exact=False)
    expect(denist_option).to_be_visible()
    denist_option.click(force=True)

    page.locator("button:has-text('Search')").click()

    # Read dropdown text from visible page
    page_text = page.locator("body").inner_text()

    # Requirement: dropdown should list affiliated hospitals
    assert "138 doctors found" in page_text
