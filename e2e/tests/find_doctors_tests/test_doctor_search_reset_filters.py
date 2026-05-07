from playwright.sync_api import Page, expect


def test_doctor_hospital_dropdown_flow(page: Page):
    page.set_default_timeout(20000)

    doctor_name = "Khaled Mohsin"

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

    # Search doctor by location
    page.locator("button:has-text('Location')").first.click()

    dropdown = page.locator("[data-radix-popper-content-wrapper]")
    dropdown.wait_for(state="visible")

    dhaka_option = dropdown.get_by_text("Dhaka", exact=False)
    expect(dhaka_option).to_be_visible()
    dhaka_option.click(force=True)

    page.locator("button:has-text('All Specialization')").first.click()

    dropdown = page.locator("[data-radix-popper-content-wrapper]")
    dropdown.wait_for(state="visible")

    denist_option = dropdown.get_by_text("Dentist", exact=False)
    expect(denist_option).to_be_visible()
    denist_option.click(force=True)

    page.locator("input").first.press("Enter")

    page.wait_for_timeout(1000)

    page_text = page.locator("body").inner_text()

    assert "No doctors found matching your criteria" in page_text

    page.locator("button:has-text('Clear Filters')").first.click()

    # Search doctor
    page.locator("nav").get_by_text("Doctors", exact=True).click()
    page.locator("input").first.fill(doctor_name)

    # Search doctor by location
    page.locator("button:has-text('Location')").first.click()

    dropdown = page.locator("[data-radix-popper-content-wrapper]")
    dropdown.wait_for(state="visible")

    dhaka_option = dropdown.get_by_text("Dhaka", exact=False)
    expect(dhaka_option).to_be_visible()
    dhaka_option.click(force=True)

    # Click doctor result
    page.get_by_text(doctor_name, exact=False).first.click()

    page.wait_for_timeout(2000)

    # Open hospital dropdown
    page.get_by_text("Select a hospital", exact=False).click()

    page.wait_for_timeout(2000)

    # Read dropdown text from visible page
    page_text = page.locator("body").inner_text()

    # Requirement: dropdown should list affiliated hospitals
    assert "Dr. Md. Khaled Mohsin" in page_text
    assert "Dhaka, Bangladesh" in page_text
    assert "Cardiology" in page_text
    assert "Affiliated Hospitals: Bangladesh Specialized Hospita" in page_text