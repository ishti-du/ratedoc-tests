import re
import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://159.89.231.16:3000"


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def click_search_by_disease(page: Page) -> None:
    candidates = [
        page.get_by_label(re.compile("search by disease", re.I)),
        page.get_by_role("radio",    name=re.compile("search by disease", re.I)),
        page.get_by_role("checkbox", name=re.compile("search by disease", re.I)),
        page.get_by_role("button",   name=re.compile("search by disease", re.I)),
        page.get_by_text(re.compile("^search by disease$", re.I)),
    ]

    for locator in candidates:
        try:
            if locator.count() > 0:
                locator.first.click()
                return
        except Exception:
            pass

    raise AssertionError("Could not find a 'Search by disease' control on the home page.")


def get_specialization_dropdown(page: Page):
    candidates = [
        page.get_by_label(re.compile("specialization", re.I)),
        page.get_by_role("combobox", name=re.compile("specialization", re.I)),
        page.locator("select[name*='special' i]"),
        page.locator("[id*='special' i]"),
        page.locator("select"),  # fallback: any <select>
    ]

    for locator in candidates:
        try:
            if locator.count() > 0:
                return locator.first
        except Exception:
            pass

    raise AssertionError("Could not find the specialization dropdown on the home page.")


# ---------------------------------------------------------------------------
# Test
# ---------------------------------------------------------------------------

@pytest.mark.ui
def test_specialization_dropdown_disabled_when_search_by_disease_selected(page: Page):
    page.goto(BASE_URL)

    dropdown = get_specialization_dropdown(page)
    expect(dropdown).to_be_visible()

    click_search_by_disease(page)

    expect(dropdown).to_be_disabled()
