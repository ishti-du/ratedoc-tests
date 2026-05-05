from playwright.sync_api import Page, expect


HOSPITAL_URL = "http://159.89.231.16:3000/hospital/former-professor-principal-brahmanbaria-medical-college-003f8e57"


def test_list_doctors_popup_navigates_to_doctor_page(page: Page):
    page.goto(HOSPITAL_URL)
    page.wait_for_timeout(3000)

    list_doctors_button = page.get_by_role("button", name="List Doctors")
    if list_doctors_button.count() == 0:
        list_doctors_button = page.get_by_text("List Doctors")

    expect(list_doctors_button.first).to_be_visible(timeout=10000)
    list_doctors_button.first.click()
    page.wait_for_timeout(1500)

    popup_title = page.get_by_text("Doctors At This Hospital")
    expect(popup_title.first).to_be_visible(timeout=10000)

    empty_state = page.get_by_text("No doctors are linked to this hospital yet.")
    assert not (empty_state.count() > 0 and empty_state.first.is_visible()), (
        "This hospital has no linked doctors in the current database. "
        "Replace HOSPITAL_URL with a hospital page that has at least one listed doctor."
    )

    doctor_link = page.locator(
        "[role='dialog'] a[href*='/doctor/'], "
        "[role='dialog'] a[href*='/doctors/'], "
        "a[href*='/doctor/'], "
        "a[href*='/doctors/']"
    ).first

    expect(doctor_link).to_be_visible(timeout=10000)

    selected_href = doctor_link.get_attribute("href")
    doctor_link.click()
    page.wait_for_timeout(3000)

    assert ("/doctor/" in page.url) or ("/doctors/" in page.url), (f"Expected to navigate to a doctor page, but landed on: {page.url}")

    if selected_href:
        expected_slug = selected_href.rstrip("/").split("/")[-1]
        assert expected_slug in page.url, ("Clicked doctor link, but landed on a different page than expected.")
