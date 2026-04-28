import pytest
from playwright.sync_api import Page, expect

# TC7 - home page specialization filter (Cardiology)
# Keval Patel

BASE_URL = "http://159.89.231.16:3000"


def pick_spec_and_search(page, spec):
    page.goto(f"{BASE_URL}/")
    page.wait_for_load_state("networkidle")

    combo = page.get_by_role("combobox").filter(has_text="Select Specialization")
    expect(combo).to_be_visible(timeout=10000)
    combo.click()
    page.get_by_role("option", name=spec, exact=True).click()
    page.get_by_role("button", name="Search", exact=True).click()
    page.wait_for_load_state("networkidle")


def test_search_url(page: Page):
    pick_spec_and_search(page, "Cardiology")
    assert "/search" in page.url
    assert "Cardiology" in page.url
    assert "type=doctor" in page.url


def test_results_show_up(page: Page):
    pick_spec_and_search(page, "Cardiology")
    cards = page.locator('a[href^="/doctor/"]')
    expect(cards.first).to_be_visible(timeout=10000)
    assert cards.count() > 0


@pytest.mark.xfail(reason="bug: dermatology doctors leak into Cardiology search")
def test_all_results_are_cardiology(page: Page):
    pick_spec_and_search(page, "Cardiology")

    cards = page.locator('a[href^="/doctor/"]')
    expect(cards.first).to_be_visible(timeout=10000)

    bad = []
    for i in range(cards.count()):
        t = cards.nth(i).inner_text()
        if "Cardiology" not in t:
            bad.append(t.split("\n")[0:3])
    assert not bad, f"non-cardiology results: {bad}"


@pytest.mark.xfail(reason="same bug as above - other specs show up")
def test_no_other_specs(page: Page):
    pick_spec_and_search(page, "Cardiology")
    cards = page.locator('a[href^="/doctor/"]')
    expect(cards.first).to_be_visible(timeout=10000)

    forbidden = ["Dermatology", "Rheumatology", "Pediatrics", "Oncology"]
    bad = []
    for i in range(cards.count()):
        t = cards.nth(i).inner_text()
        for f in forbidden:
            if f in t:
                bad.append(f)
    assert not bad, f"found: {bad}"
