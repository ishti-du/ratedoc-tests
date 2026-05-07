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

    female_option = dropdown.get_by_text("Female", exact=False)
    expect(female_option).to_be_visible()
    female_option.click(force=True)

    # Read dropdown text from visible page
    page_text = page.locator("body").inner_text()

    # Requirement: Female doctors should only be appearing
    assert "Gender: Male" not in page_text
    assert "Gender: Other" not in page_text
    assert "Gender: Female" in page_text
