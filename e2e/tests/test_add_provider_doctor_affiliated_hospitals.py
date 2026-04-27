"""
Ian Grinarml – E2E Test: Add Provider - Doctor → Affiliated Hospitals Complete
================================================================================
Test Case: Ensure Affiliated Hospitals list is complete
What to Test: Affiliated Hospitals Checkbox List should have All the hospitals, not only 100

This test verifies that when adding a doctor provider, the affiliated hospitals
list includes all hospitals in the system, not just the first 100.

Assumptions / adjust if needed:
  • Login endpoint is POST /api/v1/auth/login (used via the UI login form).
  • The test user credentials below must exist in the staging environment and have permission to add providers.
  • The add provider URL pattern is /admin/providers/add – update ADD_PROVIDER_URL if different.
  • Button / field selectors may need updating to match the actual DOM.
  • Assumes there are more than 100 hospitals in the system.
"""

import re
import pytest
from playwright.sync_api import Page, expect


BASE_URL        = "http://159.89.231.16:3000/auth"
# Update with the correct add provider URL
ADD_PROVIDER_URL = f"{BASE_URL}/admin/providers/add"
# Update with valid staging admin credentials
TEST_EMAIL    = "admin@ratedoc.com"
TEST_PASSWORD = "DeyaJabeNa!023"
# Minimum expected number of hospitals (should be > 100)
MIN_HOSPITALS   = 101


# ── Helper ──────────────────────────────────────────────────────────────────────

def login(page: Page) -> None:
    """Fill login form and authenticate as the test user."""
    page.wait_for_load_state("domcontentloaded")
    # Fill email and password using IDs
    page.locator("#email").fill(TEST_EMAIL)
    page.locator("#password").fill(TEST_PASSWORD)
    # Click the form submit button (scope to form to avoid ambiguity)
    page.locator("form").get_by_role("button", name=re.compile("log.?in|sign.?in", re.IGNORECASE)).click()
    # Wait until redirected away from the login page
    page.wait_for_url(re.compile(r"(?!.*/auth).*"), timeout=7000)


# ── Tests ───────────────────────────────────────────────────────────────────────

class TestAddProviderDoctorAffiliatedHospitals:
    """End-to-end tests for adding a doctor provider and checking affiliated hospitals list."""

    def test_affiliated_hospitals_list_is_complete(self, page: Page):
        """
        Navigate to homepage, sign in, access admin, add provider, select doctor, and verify that
        the affiliated hospitals checkbox list contains all hospitals (more than 100).
        """
        # Start from homepage
        page.goto(BASE_URL)
        page.wait_for_load_state("domcontentloaded")

        # Click sign in button (adjust selector as needed)
        sign_in_button = page.locator("button").filter(has_text=re.compile("sign.?in", re.IGNORECASE)).first
        sign_in_button.click()

        # Now login
        login(page)

        # After login, click admin button (adjust selector)
        admin_button = page.locator("button").filter(has_text="Admin").first
        admin_button.click()

        # Click add provider link (it's an <a>, not button)
        add_provider_link = page.locator("a").filter(has_text=re.compile("add provider", re.IGNORECASE)).first
        add_provider_link.click()

        # ── Select provider type as Doctor ──────────────────────────────────────
        # The provider type selector uses tabs; click the Doctor tab
        doctor_tab = page.locator("button[role='tab']").filter(has_text="Doctor").first
        doctor_tab.click()

        # Wait for the form to update with doctor-specific fields
        page.wait_for_timeout(500)  # Adjust if needed

        # ── Locate the affiliated hospitals section ─────────────────────────────
        # The number is displayed in a span like "100 hospital(s)"
        hospitals_span = page.locator("span").filter(has_text="hospital(s)").first
        span_text = hospitals_span.text_content()
        num_hospitals = int(span_text.split()[0])

        # ── Assert that the list is complete (not truncated to 100) ─────────────
        assert num_hospitals > 100, (
            f"Affiliated hospitals list shows only {num_hospitals} hospitals, "
            f"expected more than 100 (indicating the list is complete)"
        )