from playwright.sync_api import Page, expect

BASE_URL = "http://159.89.231.16:3000"


def select_gender_filter(page: Page, gender: str):
    page.get_by_text("All Genders", exact=True).click()
    page.get_by_role("option", name=gender, exact=True).click()
    page.wait_for_timeout(1500)


def test_doctors_gender_filter(page: Page):
    page.goto(f"{BASE_URL}/doctors", wait_until="domcontentloaded")

    # Test Male filter first
    select_gender_filter(page, "Male")
    expect(page.locator("body")).to_contain_text("Gender: Male", timeout=10000)
    expect(page.locator("body")).not_to_contain_text("Gender: Female")

    # Reset page and test Female filter
    page.goto(f"{BASE_URL}/doctors", wait_until="domcontentloaded")
    select_gender_filter(page, "Female")
    expect(page.locator("body")).to_contain_text("Gender: Female", timeout=10000)
    expect(page.locator("body")).not_to_contain_text("Gender: Male")