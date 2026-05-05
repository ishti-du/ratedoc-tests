from playwright.sync_api import Page, expect


def test_doctor_hospital_dropdown_flow(page: Page):
    page.set_default_timeout(20000)

    page.goto("https://ratedoctor.io/", wait_until="domcontentloaded")

    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1000)

    # Select Doctor Tab
    page.locator("nav").get_by_text("Doctors", exact=True).click()

    # Select Dentist Specialization
    gender_button = page.locator("button:has-text('All Genders')").first
    gender_button.wait_for(state="visible")
    gender_button.click()

    dropdown = page.locator("[data-radix-popper-content-wrapper]")
    dropdown.wait_for(state="visible")

    other_option = dropdown.get_by_text("Other", exact=True)
    expect(other_option).to_be_visible()
    other_option.click(force=True)

    # Read dropdown text from visible page
    page_text = page.locator("body").inner_text()

    # Requirement: Female doctors should only be appearing
    assert "Gender: Female" not in page_text
    assert "Gender: Male" not in page_text
