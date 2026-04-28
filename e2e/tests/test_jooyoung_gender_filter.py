from playwright.sync_api import Page, expect

BASE_URL = "http://159.89.231.16:3000"


def test_doctors_page_contains_gender_info(page: Page):
    page.goto(f"{BASE_URL}/doctors", wait_until="domcontentloaded")
    page.wait_for_load_state("networkidle")

    # Verify doctor cards display gender information
    expect(page.locator("body")).to_contain_text("Gender:")