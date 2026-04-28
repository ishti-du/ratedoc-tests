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

Pre-test cleanup uses the admin API to remove any stuck review (e.g. one
that was rejected by admin tests), because the user endpoint only returns
approved reviews and a rejected review blocks new creation.
"""

import re
import requests as http
from playwright.sync_api import Page, expect


BASE_URL        = "http://159.89.231.16:3000"
API_URL         = "http://159.89.231.16:3001"
DOCTOR_SLUG     = "dr-john-smith-7a055de9"
DOCTOR_URL      = f"{BASE_URL}/doctor/{DOCTOR_SLUG}"
TEST_EMAIL      = "tests1234@gmail.com"
TEST_PASSWORD   = "abc123456"
TEST_USER_ID    = "615cae14-9a22-450a-9cc2-3f551f8bac29"
ADMIN_EMAIL     = "admin@ratedoc.com"
ADMIN_PASSWORD  = "DeyaJabeNa!023"
REVIEW_TEXT     = "[Test] Automated review – will be deleted by this test."


# ---------------------------------------------------------------------------
# API-level cleanup (runs before browser opens, handles any review status)
# ---------------------------------------------------------------------------

def api_delete_stuck_reviews() -> None:
    """
    Use the admin API to delete any review the test user left on this doctor.
    Needed because the user endpoint only returns approved reviews, but a
    rejected/pending review still blocks new creation with 'already submitted'.
    """
    resp = http.post(
        f"{API_URL}/api/v1/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=10,
    )
    token = resp.json().get("access_token", "")
    if not token:
        return

    headers = {"Authorization": f"Bearer {token}"}
    reviews = http.get(
        f"{API_URL}/api/v1/admin/reviews",
        params={"provider_slug": DOCTOR_SLUG, "size": 100},
        headers=headers,
        timeout=10,
    ).json().get("items", [])

    for review in reviews:
        if review.get("user_id") == TEST_USER_ID:
            http.delete(
                f"{API_URL}/api/v1/admin/reviews/{review['id']}",
                headers=headers,
                timeout=10,
            )


# ---------------------------------------------------------------------------
# Browser helpers
# ---------------------------------------------------------------------------

def login(page: Page) -> None:
    """Navigate to /auth and log in with the test account."""
    page.goto(f"{BASE_URL}/auth")
    page.locator("input[type='email']").fill(TEST_EMAIL)
    page.locator("input[type='password']").fill(TEST_PASSWORD)
    # Two "Sign In" buttons exist (nav + form) – scope to the form's submit button
    page.locator("form").get_by_role("button", name="Sign In").click()
    # Wait for redirect to home page (login always goes to "/" when no prior location)
    page.wait_for_url(f"{BASE_URL}/", timeout=10000)


def wait_for_form_stable(page: Page, timeout: int = 15000) -> None:
    """
    Wait until the review form is fully initialised:
      - textarea visible (auth resolved + doctor data loaded)
      - action button visible (useUserReviewForProvider query completed)
    The second check prevents a race where the form renders in new-review mode
    before the user's existing review is fetched, causing cleanup to be skipped.
    """
    page.get_by_placeholder("Share your experience...").wait_for(
        state="visible", timeout=timeout
    )
    # Either "Submit Review" (new mode) or "Update Review" (edit mode) must appear
    page.locator(
        "button:has-text('Submit Review'), button:has-text('Update Review')"
    ).first.wait_for(state="visible", timeout=timeout)


def cleanup_ui_review(page: Page) -> None:
    """If the form is in edit mode (user has an approved review), delete it via the UI."""
    wait_for_form_stable(page)

    delete_btn = page.get_by_role("button", name="Delete Review")
    if not delete_btn.is_visible():
        return

    page.once("dialog", lambda d: d.accept())
    delete_btn.click()
    # Wait for form to return to new-review mode
    page.get_by_role("button", name="Submit Review").wait_for(
        state="visible", timeout=10000
    )


def click_star(page: Page, label_text: str, star_num: int = 4) -> None:
    """Click the Nth star in the rating section identified by label_text."""
    section = (
        page.locator(".mb-4")
        .filter(has_text=label_text)
        .filter(has=page.locator("button[type='button']:not([aria-label])"))
        .first
    )
    section.locator("button[type='button']:not([aria-label])").nth(star_num - 1).click()


def submit_review(page: Page) -> None:
    """Fill all required fields and submit the review form."""
    wait_for_form_stable(page)

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

    # Overall Rating (required)
    click_star(page, "Your Overall Rating", star_num=4)

    # Optional comment – used to verify the review was saved
    page.get_by_placeholder("Share your experience...").fill(REVIEW_TEXT)

    # Submit
    page.get_by_role("button", name="Submit Review").click()


def delete_review(page: Page) -> None:
    """Wait for 'Delete Review' button and click it, accepting the confirm dialog."""
    delete_btn = page.get_by_role("button", name="Delete Review")
    expect(delete_btn).to_be_visible(timeout=10000)

    page.once("dialog", lambda d: d.accept())
    delete_btn.click()


# ---------------------------------------------------------------------------
# Test class
# ---------------------------------------------------------------------------

class TestDoctorReviewDelete:
    """End-to-end tests for creating and deleting a doctor review."""

    def test_create_review_appears_on_page(self, page: Page):
        """
        After submitting a review the form should switch to edit mode,
        showing the saved comment and a 'Delete Review' button.
        Cleans up by deleting the review at the end.
        """
        # API-level cleanup handles stuck reviews in any status (pending/rejected)
        api_delete_stuck_reviews()

        login(page)
        page.goto(DOCTOR_URL)

        # UI-level cleanup handles an approved leftover review (visible in the form)
        cleanup_ui_review(page)

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
        # API-level cleanup handles stuck reviews in any status (pending/rejected)
        api_delete_stuck_reviews()

        login(page)
        page.goto(DOCTOR_URL)

        # UI-level cleanup handles an approved leftover review (visible in the form)
        cleanup_ui_review(page)

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
