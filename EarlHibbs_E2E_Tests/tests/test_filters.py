import re
import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://159.89.231.16:3000"


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def search_for_hospitals(page: Page) -> None:
    search_inputs = [
        page.get_by_placeholder(re.compile("search", re.I)),
        page.get_by_role("textbox", name=re.compile("search", re.I)),
        page.locator("input[type='search']"),
        page.locator("input[placeholder*='search' i]"),
    ]

    for locator in search_inputs:
        try:
            if locator.count() > 0:
                locator.first.fill("hospital")
                break
        except Exception:
            pass

    search_buttons = [
        page.get_by_role("button", name=re.compile("^search$", re.I)),
        page.get_by_text(re.compile("^search$", re.I)),
    ]

    for locator in search_buttons:
        try:
            if locator.count() > 0:
                locator.first.click()
                return
        except Exception:
            pass


def get_filter_button(page: Page, label: str):
    pattern = re.compile(f"^{re.escape(label)}$", re.I)
    btn = page.get_by_role("button", name=pattern)
    if btn.count() == 0:
        btn = page.get_by_text(pattern)
    return btn.first


def extract_integers(page: Page, pattern: str) -> list[int]:
    body_text = page.locator("body").inner_text()
    return [int(m) for m in re.findall(pattern, body_text, flags=re.I) if m.isdigit() or m.lstrip("-").isdigit()]


def extract_floats(page: Page, pattern: str) -> list[float]:
    body_text = page.locator("body").inner_text()
    results = []
    for m in re.findall(pattern, body_text):
        try:
            results.append(float(m))
        except ValueError:
            pass
    return results


# ---------------------------------------------------------------------------
# Test
# ---------------------------------------------------------------------------

@pytest.mark.ui
def test_hospitals_filters_most_reviews_and_highest_reviews(page: Page):
    page.goto(f"{BASE_URL}/hospitals")

    search_for_hospitals(page)
    expect(page.locator("body")).to_be_visible()

    most_reviews_btn = get_filter_button(page, "most reviews")
    expect(most_reviews_btn).to_be_visible()
    most_reviews_btn.click()
    page.wait_for_timeout(1500)

    review_counts = extract_integers(page, r"(\d+)\s+reviews?")
    assert review_counts, "No review counts found after applying 'Most Reviews' filter."
    assert review_counts == sorted(review_counts, reverse=True), (
        f"'Most Reviews' did not sort descending. Got: {review_counts}"
    )

    highest_reviews_btn = get_filter_button(page, "highest reviews")
    expect(highest_reviews_btn).to_be_visible()
    highest_reviews_btn.click()
    page.wait_for_timeout(1500)

    rating_values = extract_floats(page, r"\b([0-5]\.\d)\b")
    assert rating_values, "No rating values found after applying 'Highest Reviews' filter."
    assert rating_values == sorted(rating_values, reverse=True), (
        f"'Highest Reviews' did not sort descending. Got: {rating_values}"
    )
