import pytest
from playwright.sync_api import Page, expect


BASE_URL = "http://159.89.231.16:3000/doctors"


@pytest.fixture(autouse=True)
def navigate(page: Page):
    page.goto(BASE_URL)
    page.wait_for_selector(".animate-fade-in")


def get_ratings(page: Page) -> list[float]:
    """Extract the numeric rating from each doctor card."""
    cards = page.locator(".animate-fade-in")
    ratings = []
    for card in cards.all():
        rating_text = card.locator(".text-sm.font-medium.text-foreground").inner_text()
        try:
            ratings.append(float(rating_text))
        except ValueError:
            ratings.append(0.0)
    return ratings


def get_review_counts(page: Page) -> list[int]:
    """Extract the review count from each doctor card (e.g. '3 reviews' -> 3)."""
    cards = page.locator(".animate-fade-in")
    counts = []
    for card in cards.all():
        # Target the span that specifically contains "review" text
        review_text = card.locator("span.text-sm.text-muted-foreground").inner_text()
        try:
            counts.append(int(review_text.split()[0]))
        except (ValueError, IndexError):
            counts.append(0)
    return counts


def test_sort_by_highest_rated(page: Page):
    # Open the sort dropdown — it defaults to "Highest Rated"
    # but we'll explicitly select it to confirm it works
    sort_dropdown = page.locator('button[role="combobox"]').filter(has_text="Highest Rated")
    sort_dropdown.click()
    page.get_by_role("option", name="Highest Rated").click()
    page.wait_for_timeout(500)

    # Cards should still be present
    expect(page.locator(".animate-fade-in")).not_to_have_count(0)

    # Ratings should be in descending order
    ratings = get_ratings(page)
    assert ratings == sorted(ratings, reverse=True), (
        f"Doctors are not sorted by highest rating. Got: {ratings}"
    )


def test_sort_by_most_reviews(page: Page):
    # Switch to "Most Reviews"
    sort_dropdown = page.locator('button[role="combobox"]').filter(has_text="Highest Rated")
    sort_dropdown.click()
    page.get_by_role("option", name="Most Reviews").click()
    page.wait_for_timeout(500)

    # Cards should still be present
    expect(page.locator(".animate-fade-in")).not_to_have_count(0)

    # Review counts should be in descending order
    counts = get_review_counts(page)
    assert counts == sorted(counts, reverse=True), (
        f"Doctors are not sorted by most reviews. Got: {counts}"
    )


def test_switching_between_sort_options(page: Page):
    """Switching sort options should always keep cards visible."""
    sort_dropdown = page.locator('button[role="combobox"]').filter(has_text="Highest Rated")

    # Switch to Most Reviews
    sort_dropdown.click()
    page.get_by_role("option", name="Most Reviews").click()
    page.wait_for_timeout(500)
    expect(page.locator(".animate-fade-in")).not_to_have_count(0)

    # Switch back to Highest Rated
    page.locator('button[role="combobox"]').filter(has_text="Most Reviews").click()
    page.get_by_role("option", name="Highest Rated").click()
    page.wait_for_timeout(500)
    expect(page.locator(".animate-fade-in")).not_to_have_count(0)