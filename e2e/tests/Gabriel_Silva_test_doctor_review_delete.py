"""
Gabriel Silva – E2E Test: Doctor Review → Delete Review
========================================================
Test Case:
  1. Log in as a regular user.
  2. Navigate to a doctor's profile page.
  3. Submit a new review (all required fields filled).
  4. Confirm the review was saved (form switches to edit mode).
  5. Click the 'Delete Review' button and confirm the review is removed.

This test is self-contained: it creates its own review and deletes it,
so it can be run repeatedly without leaving leftover data.

Credentials and DOCTOR_URL below must match the staging environment.
"""

import re
from playwright.sync_api import Page, expect


BASE_URL       = "http://159.89.231.16:3000"
DOCTOR_URL     = f"{BASE_URL}/doctor/dr-john-smith-7a055de9"
TEST_EMAIL     = "tests1234@gmail.com"
TEST_PASSWORD  = "abc123456"
REVIEW_TEXT    = "[Test] Automated review – will be deleted by this test."


def login(page: Page) -> None:
    """Navigate to /auth and log in with the test account."""
    page.goto(f"{BASE_URL}/auth")
    page.locator("input[type='email']").fill(TEST_EMAIL)
    page.locator("input[type='password']").fill(TEST_PASSWORD)
    # Two "Sign In" buttons exist (nav + form) – scope to the form's submit button
    page.locator("form").get_by_role("button", name="Sign In").click()
    # Wait for redirect to home page (login always goes to "/" when no prior location)
    page.wait_for_url(f"{BASE_URL}/", timeout=10000)


def wait_for_review_form(page: Page, timeout: int = 15000) -> None:
    """Wait until the review form textarea is visible (auth + doctor data both loaded)."""
    page.get_by_placeholder("Share your experience...").wait_for(
        state="visible", timeout=timeout
    )


def cleanup_existing_review(page: Page) -> None:
    """If the test user already has a review for this doctor, delete it first."""
    wait_for_review_form(page)

    delete_btn = page.get_by_role("button", name="Delete Review")
    if not delete_btn.is_visible():
        return

    page.once("dialog", lambda d: d.accept())
    delete_btn.click()
    # Wait for form to return to new-review mode (Submit Review button reappears)
    page.get_by_role("button", name="Submit Review").wait_for(
        state="visible", timeout=10000
    )


def click_star(page: Page, label_text: str, star_num: int = 4) -> None:
    """Click the Nth star in the rating section identified by label_text."""
    # Narrow to the mb-4 div that contains this label AND has star buttons
    section = (
        page.locator(".mb-4")
        .filter(has_text=label_text)
        .filter(has=page.locator("button[type='button']:not([aria-label])"))
        .first
    )
    section.locator("button[type='button']:not([aria-label])").nth(star_num - 1).click()


def submit_review(page: Page) -> None:
    """Fill all required fields and submit the review form."""
    # Wait for the form to be ready (confirms auth resolved + doctor data loaded)
    wait_for_review_form(page)

    # Visit Date (required)
    page.locator("input[type='date']").fill("2025-01-15")

    # Four required sub-ratings – click the 4th star (4 out of 5)
    for label in [
        "Listens & Answers Questions",
        "Explains Treatment Options",
        "Provides Effective Treatment",
        "Office Staff Cooperation",
    ]:
        click_star(page, label, star_num=4)

    # Overall Rating (required) – click the 4th star
    click_star(page, "Your Overall Rating", star_num=4)

    # Optional comment – used to verify the review was saved
    page.get_by_placeholder("Share your experience...").fill(REVIEW_TEXT)

    # Submit
    page.get_by_role("button", name="Submit Review").click()


def delete_review(page: Page) -> None:
    """Wait for 'Delete Review' button and click it, accepting the confirm dialog."""
    delete_btn = page.get_by_role("button", name="Delete Review")
    expect(delete_btn).to_be_visible(timeout=10000)

    # Register dialog handler before clicking
    page.once("dialog", lambda d: d.accept())
    delete_btn.click()


class TestDoctorReviewDelete:
    """End-to-end tests for creating and deleting a doctor review."""

    def test_create_review_appears_on_page(self, page: Page):
        """
        After submitting a review the form should switch to edit mode,
        showing the saved comment and a 'Delete Review' button.
        Cleans up by deleting the review at the end.
        """
        login(page)
        page.goto(DOCTOR_URL)

        # Remove any leftover review from a previous failed run
        cleanup_existing_review(page)

        submit_review(page)

        # After submission TanStack Query refetches and the form enters edit mode.
        # The 'Delete Review' button appearing confirms the review was saved.
        expect(page.get_by_role("button", name="Delete Review")).to_be_visible(timeout=10000)

        # The comment textarea should contain the text we just submitted
        expect(page.locator("form textarea")).to_have_value(REVIEW_TEXT, timeout=5000)

        # Cleanup – delete the review we just created
        delete_review(page)

    def test_delete_review_removes_it_from_page(self, page: Page):
        """
        Main test case:
          1. Create a review.
          2. Verify it is saved (edit mode active, comment in textarea).
          3. Click Delete Review and confirm.
          4. Verify the review is gone (form back to new-review mode).
        """
        login(page)
        page.goto(DOCTOR_URL)

        # Remove any leftover review from a previous failed run
        cleanup_existing_review(page)

        # Step 1: create the review
        submit_review(page)

        # Step 2: confirm it was saved
        expect(page.get_by_role("button", name="Delete Review")).to_be_visible(timeout=10000)
        expect(page.locator("form textarea")).to_have_value(REVIEW_TEXT, timeout=5000)

        # Step 3: delete it
        delete_review(page)

        # Step 4: 'Delete Review' button should be gone (form back to new-review mode)
        expect(page.get_by_role("button", name="Delete Review")).not_to_be_visible(timeout=8000)
        # The textarea should be cleared
        expect(page.locator("form textarea")).to_have_value("", timeout=5000)
