from playwright.sync_api import Page, expect


def test_doctor_hospital_dropdown_flow(page: Page):
    page.set_default_timeout(20000)

    doctor_name = "Shaukat Haidar"

    page.goto("https://ratedoctor.io/", wait_until="domcontentloaded")

    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1000)

    # Select Doctor Tab
    page.locator("nav").get_by_text("Doctors", exact=True).click()

    # Select Dentist Specialization
    sort_button = page.locator("button:has-text('Highest Rated')").first
    sort_button.wait_for(state="visible")
    sort_button.click()

    dropdown = page.locator("[data-radix-popper-content-wrapper]")
    dropdown.wait_for(state="visible")

    reviews_option = dropdown.get_by_text("Most Reviews", exact=False)
    expect(reviews_option ).to_be_visible()
    reviews_option .click(force=True)

    page.get_by_text(doctor_name, exact=False).first.click()
    page.wait_for_timeout(2000)

    # Read dropdown text from visible page
    page_text = page.locator("body").inner_text()

    # Requirement: Doctor should be appearing first with highest rated
    assert "Dr. Md. Shaukat Haidar" in page_text
    assert "Unknown, Bangladesh" in page_text
    assert "Dermatology" in page_text
