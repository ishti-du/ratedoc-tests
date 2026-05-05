"""
Ian Grinarml – E2E Test: Claim Doctor Profile → Google Form Redirect
===============================================================================
Test Case: Ensure Claim Profile opens Google Form in new tab
What to Test: Clicking "Is This You? Claim Profile" should open a Google Form

This test verifies that when a user navigates to a doctor’s profile and clicks
the "Is This You? Claim Profile" button, a Google Form opens in a new browser tab.

Best Practice Applied:
  • We DO NOT log into Google (external service, unreliable for testing)
  • We ONLY verify that the correct Google Forms URL is opened
  • This keeps the test fast, stable, and CI-friendly

Assumptions / adjust if needed:
  • Login endpoint is handled via the UI login form.
  • The test user credentials below must exist and allow access to the Doctors page.
  • The Doctors page URL is /doctors.
  • Doctor cards use links with pattern /doctor/{slug}.
  • The "Claim Profile" button is an <a> tag with target="_blank".
  • The Google Form URL may be forms.gle or docs.google.com/forms.
"""


import re
import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://159.89.231.16:3000"

TEST_EMAIL = "admin@ratedoc.com"
TEST_PASSWORD = "DeyaJabeNa!023"


# ── Helper: Login to RateDoc ───────────────────────────────────────────────────

def login(page: Page) -> None:
    page.goto(BASE_URL)
    page.wait_for_load_state("domcontentloaded")

    # Click "Sign In" button
    page.locator("button").filter(
        has_text=re.compile("sign.?in", re.IGNORECASE)
    ).first.click()

    # Fill credentials
    page.locator("#email").fill(TEST_EMAIL)
    page.locator("#password").fill(TEST_PASSWORD)

    # Submit login form
    page.locator("form").get_by_role(
        "button", name=re.compile("log.?in|sign.?in", re.IGNORECASE)
    ).click()

    # Wait until redirected away from auth page
    page.wait_for_url(re.compile(r"(?!.*/auth).*"), timeout=7000)


# ── Test ────────────────────────────────────────────────────────────────────────

class TestClaimProfileGoogleForm:

    def test_claim_profile_opens_google_form(self, page: Page):
        # ── Step 1: Login ────────────────────────────────────────────────────
        login(page)

        # ── Step 2: Navigate to Doctors page ─────────────────────────────────
        page.locator("a[href='/doctors']").click()

        # Wait for doctor cards to appear
        doctor_cards = page.locator("a[href^='/doctor/']")
        expect(doctor_cards.first).to_be_visible()

        # ── Step 3: Open first doctor profile ────────────────────────────────
        doctor_cards.first.click()
        page.wait_for_load_state("domcontentloaded")

        # ── Step 4: Click "Claim Profile" and capture new tab ────────────────
        with page.context.expect_page() as new_page_info:
            page.locator("a").filter(
                has_text=re.compile("claim profile|is this you", re.IGNORECASE)
            ).click()

        google_form_page = new_page_info.value

        # Wait for new tab to fully load
        google_form_page.wait_for_load_state()

        # ── Step 5: Validate redirect is a Google Form ───────────────────────
        expect(google_form_page).to_have_url(
            re.compile(r"(forms\.gle|docs\.google\.com/forms)")
        )

        # Additional safety assertion (helps debugging failures)
        assert "google" in google_form_page.url.lower(), (
            f"Expected a Google Form URL, but got: {google_form_page.url}"
        )
