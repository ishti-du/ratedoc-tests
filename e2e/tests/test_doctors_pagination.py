from playwright.sync_api import Page, expect
import re

DOCTORS_URL = "http://159.89.231.16:3000/doctors#"


def get_doctor_cards(page: Page):
    selectors = [
        ".doctor-card",
        "[data-testid='doctor-card']",
        "a[href*='/doctor/']",
        "a[href*='/doctors/']",
        "div:has(a[href*='/doctor/'])",
    ]
    for selector in selectors:
        locator = page.locator(selector)
        if locator.count() > 0:
            return locator
    return page.locator("main *")


def test_doctors_next_previous_pagination(page: Page):
    page.goto(DOCTORS_URL)
    page.wait_for_timeout(3000)

    expect(page).to_have_url(re.compile(r".*/doctors#?$"))

    cards = get_doctor_cards(page)
    expect(cards.first).to_be_visible()

    first_page_snapshot = cards.all_inner_texts()

    next_button = page.get_by_role("button", name="Next")
    if next_button.count() == 0:
        next_button = page.get_by_text("Next")

    expect(next_button.first).to_be_visible()
    next_button.first.click()
    page.wait_for_timeout(3000)

    second_page_snapshot = get_doctor_cards(page).all_inner_texts()

    assert first_page_snapshot != second_page_snapshot, ("Clicking Next did not change the doctor list.")

    previous_button = page.get_by_role("button", name="Previous")
    if previous_button.count() == 0:
        previous_button = page.get_by_text("Previous")

    expect(previous_button.first).to_be_visible()
    previous_button.first.click()
    page.wait_for_timeout(3000)

    returned_snapshot = get_doctor_cards(page).all_inner_texts()

    assert returned_snapshot == first_page_snapshot, ("Clicking Previous did not return to the original page contents.")
