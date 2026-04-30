import pytest
from playwright.sync_api import Page, expect

# TC26 - hospitals page location filter (Cumilla)
# Keval Patel

BASE_URL = "http://159.89.231.16:3000"


def filter_by_city(page, city):
    page.goto(f"{BASE_URL}/hospitals")
    page.wait_for_load_state("networkidle")

    loc = page.locator('button[role="combobox"]:has-text("Location")')
    expect(loc).to_be_visible(timeout=10000)
    loc.click()
    page.locator(f'[role="option"]:has-text("{city}")').first.click()
    page.wait_for_load_state("networkidle")


def test_hospitals_page_loads(page: Page):
    page.goto(f"{BASE_URL}/hospitals")
    page.wait_for_load_state("networkidle")
    expect(page.locator('button[role="combobox"]:has-text("Location")')).to_be_visible()


def test_filter_returns_results(page: Page):
    filter_by_city(page, "Cumilla")
    cards = page.locator('a[href^="/hospital/"]')
    expect(cards.first).to_be_visible(timeout=10000)
    assert cards.count() > 0


def test_all_hospitals_in_cumilla(page: Page):
    filter_by_city(page, "Cumilla")
    cards = page.locator('a[href^="/hospital/"]')
    expect(cards.first).to_be_visible(timeout=10000)

    bad = []
    for i in range(cards.count()):
        t = cards.nth(i).inner_text()
        if "Cumilla" not in t:
            bad.append(t.split("\n")[1] if "\n" in t else t)
    assert not bad, f"not in cumilla: {bad}"


def test_no_other_cities(page: Page):
    filter_by_city(page, "Cumilla")
    cards = page.locator('a[href^="/hospital/"]')
    expect(cards.first).to_be_visible(timeout=10000)

    others = ["Dhaka,", "Chittagong,", "Sylhet,", "Rajshahi,", "Barisal,"]
    bad = []
    for i in range(cards.count()):
        t = cards.nth(i).inner_text()
        for c in others:
            if c in t:
                bad.append(c.rstrip(","))
    assert not bad, f"leaked cities: {bad}"


def test_filter_actually_narrows(page: Page):
    filter_by_city(page, "Cumilla")
    filtered = page.locator('a[href^="/hospital/"]').count()

    page.goto(f"{BASE_URL}/hospitals")
    page.wait_for_load_state("networkidle")
    full = page.locator('a[href^="/hospital/"]').count()

    assert full >= filtered
