"""
Ian Grinarml – E2E Test: Claim Doctor Profile → Google Form Redirect
===============================================================================
Test Case: Ensure Claim Profile opens Google Form in new tab
What to Test: Clicking "Is This You? Claim Profile" should open a Google Form

This test verifies that when a user navigates to a doctor’s profile and clicks
the "Is This You? Claim Profile" button, a Google Form opens in a new browser tab.

Assumptions / adjust if needed:
  • Login endpoint is POST /api/v1/auth/login (used via the UI login form).
  • The test user credentials below must exist and allow access to the Doctors page.
  • The Doctors page URL is /doctors – update selector if navigation differs.
  • Doctor cards use links with pattern /doctor/{slug}.
  • The first available doctor profile is used for testing.
  • The "Claim Profile" button is an <a> tag with target="_blank".
  • The Google Form URL may be forms.gle or docs.google.com/forms.
  • Button text and selectors may need updating to match the actual DOM.
"""


import re
import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://159.89.231.16:3000"

TEST_EMAIL = "admin@ratedoc.com"
TEST_PASSWORD = "DeyaJabeNa!023"


# ── Helper ──────────────────────────────────────────────────────────────────────

def login(page: Page) -> None:
    page.goto(BASE_URL)
    page.wait_for_load_state("domcontentloaded")

    # Click sign in
    page.locator("button").filter(
        has_text=re.compile("sign.?in", re.IGNORECASE)
    ).first.click()

    # Fill credentials
    page.locator("#email").fill(TEST_EMAIL)
    page.locator("#password").fill(TEST_PASSWORD)

    # Submit
    page.locator("form").get_by_role(
        "button", name=re.compile("log.?in|sign.?in", re.IGNORECASE)
    ).click()

    page.wait_for_url(re.compile(r"(?!.*/auth).*"), timeout=7000)


# ── Test ────────────────────────────────────────────────────────────────────────

class TestClaimProfileGoogleForm:

    def test_claim_profile_opens_google_form(self, page: Page):
        # Login first
        login(page)

        # ── Click Doctors tab ────────────────────────────────────────────────
        page.locator("a[href='/doctors']").click()

        # Wait for doctor cards to load
        doctor_cards = page.locator("a[href^='/doctor/']")
        expect(doctor_cards.first).to_be_visible()

        # ── Click first doctor ───────────────────────────────────────────────
        doctor_cards.first.click()

        # Wait for profile page
        page.wait_for_load_state("domcontentloaded")

        # ── Prepare to catch new tab (IMPORTANT) ─────────────────────────────
        with page.context.expect_page() as new_page_info:
            page.locator("a").filter(
                has_text=re.compile("claim profile|is this you", re.IGNORECASE)
            ).click()

        google_form_page = new_page_info.value

        # Wait for it to load
        google_form_page.wait_for_load_state()

        # ── Assertion ────────────────────────────────────────────────────────
        expect(google_form_page).to_have_url(re.compile(r"forms\.gle|docs\.google\.com/forms"))

        # Optional: extra strong validation
        assert "google" in google_form_page.url.lower(), (
            f"Expected Google Form, but got: {google_form_page.url}"
        )