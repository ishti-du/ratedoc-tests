"""
Gabriel Silva – E2E Test: Doctor Review → Delete Review
========================================================
Test Case:
  1. Log in as a regular user.
  2. Navigate to a doctor's profile page.
  3. Submit a new review.
  4. Confirm the review appears on the page.
  5. Click the 'Delete Review' button and confirm the review is removed.

This test is self-contained: it creates its own review data and deletes it
afterwards, so it can be run in any order or repeatedly without side-effects.

Assumptions / adjust if needed:
  • Login endpoint is POST /api/v1/auth/login (used via the UI login form).
  • The test user credentials below must exist in the staging environment.
  • The doctor profile URL pattern is /doctors/{id} – update DOCTOR_URL if different.
  • Button / field selectors may need updating to match the actual DOM.
"""

import re
import pytest
from playwright.sync_api import Page, expect


BASE_URL    = "http://159.89.231.16:3000"
# Update with a real doctor page URL from the staging environment
DOCTOR_URL  = f"{BASE_URL}/doctors/1"
# Update with valid staging credentials
TEST_EMAIL    = "testuser@example.com"
TEST_PASSWORD = "Password123!"
REVIEW_TEXT   = "[Test] Automated review – will be deleted by this test."


# ── Helper ──────────────────────────────────────────────────────────────────────

def login(page: Page) -> None:
    """Navigate to the login page and authenticate as the test user."""
    page.goto(f"{BASE_URL}/login")
    # Adjust selectors to match the actual login form field names / IDs
    page.get_by_label(re.compile("email", re.IGNORECASE)).fill(TEST_EMAIL)
    page.get_by_label(re.compile("password", re.IGNORECASE)).fill(TEST_PASSWORD)
    page.get_by_role("button", name=re.compile("log.?in|sign.?in", re.IGNORECASE)).click()
    # Wait until redirected away from the login page
    page.wait_for_url(re.compile(r"(?!.*/login).*"), timeout=7000)


# ── Tests ───────────────────────────────────────────────────────────────────────

class TestDoctorReviewDelete:
    """End-to-end tests for creating and deleting a doctor review."""

    def test_create_review_appears_on_page(self, page: Page):
        """
        After submitting a review it should be visible in the reviews section.
        Cleans up by deleting the created review at the end.
        """
        login(page)
        page.goto(DOCTOR_URL)

        # ── Locate the review form ──────────────────────────────────────────────
        # Adjust the selector to match the actual textarea / input for review text
        review_textarea = page.get_by_placeholder(
            re.compile("write.*review|your.*review|comment", re.IGNORECASE)
        )
        if not review_textarea.is_visible():
            review_textarea = page.locator("textarea").first

        review_textarea.fill(REVIEW_TEXT)

        # Select a star rating if present (click the 4th star, for example)
        stars = page.locator("[aria-label*='star'], .star, [data-rating]")
        if stars.count() >= 4:
            stars.nth(3).click()  # 4th star (0-indexed)

        # Submit the review
        page.get_by_role("button", name=re.compile("submit|post|add review", re.IGNORECASE)).click()

        # ── Assert the review text appears in the reviews list ──────────────────
        page.wait_for_selector(f"text={REVIEW_TEXT}", timeout=7000)
        expect(page.get_by_text(REVIEW_TEXT)).to_be_visible()

        # ── Cleanup: delete the review we just created ──────────────────────────
        # This mirrors the delete test below – ensures no orphaned data is left
        _delete_review_by_text(page, REVIEW_TEXT)

    def test_delete_review_removes_it_from_page(self, page: Page):
        """
        Main test case:
          1. Create a review.
          2. Verify it is present.
          3. Click 'Delete Review'.
          4. Verify the review is no longer visible.
        """
        login(page)
        page.goto(DOCTOR_URL)

        # ── Step 1: Create the review ───────────────────────────────────────────
        review_textarea = page.get_by_placeholder(
            re.compile("write.*review|your.*review|comment", re.IGNORECASE)
        )
        if not review_textarea.is_visible():
            review_textarea = page.locator("textarea").first

        review_textarea.fill(REVIEW_TEXT)

        stars = page.locator("[aria-label*='star'], .star, [data-rating]")
        if stars.count() >= 4:
            stars.nth(3).click()

        page.get_by_role("button", name=re.compile("submit|post|add review", re.IGNORECASE)).click()

        # ── Step 2: Confirm review is visible ───────────────────────────────────
        page.wait_for_selector(f"text={REVIEW_TEXT}", timeout=7000)
        review_element = page.get_by_text(REVIEW_TEXT)
        expect(review_element).to_be_visible()

        # ── Step 3: Click 'Delete Review' on this specific review ───────────────
        _delete_review_by_text(page, REVIEW_TEXT)

        # ── Step 4: Confirm the review is gone ──────────────────────────────────
        # After deletion, the review text should no longer be in the DOM
        expect(page.get_by_text(REVIEW_TEXT)).not_to_be_visible(timeout=5000)


# ── Private helper ───────────────────────────────────────────────────────────────

def _delete_review_by_text(page: Page, review_text: str) -> None:
    """
    Locate the review card containing `review_text` and click its Delete button.

    Approach: find the container that holds the review text, then scope the
    'Delete' button search to that container so we don't accidentally delete
    a different review.
    """
    # Find the review card / list item that contains our text
    # Adjust the container selector (.review-card, li, article, etc.) as needed
    review_card = page.locator(
        "li, article, .review, .review-card, [data-testid='review']"
    ).filter(has_text=review_text).first

    expect(review_card).to_be_visible(timeout=5000)

    # Click the Delete button scoped to this card
    delete_btn = review_card.get_by_role(
        "button", name=re.compile("delete.*review|remove", re.IGNORECASE)
    )
    if not delete_btn.is_visible():
        # Some UIs show delete as a link or an icon button
        delete_btn = review_card.locator(
            "a, button, [data-action='delete']"
        ).filter(has_text=re.compile("delete", re.IGNORECASE)).first

    delete_btn.click()

    # Handle a confirmation dialog if present (e.g., "Are you sure?")
    confirm_btn = page.get_by_role(
        "button", name=re.compile("confirm|yes|ok|delete", re.IGNORECASE)
    )
    if confirm_btn.is_visible(timeout=2000):
        confirm_btn.click()
