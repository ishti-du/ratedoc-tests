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


BASE_URL        = "http://159.89.231.16:3000"
# Update with the correct add provider URL
ADD_PROVIDER_URL = f"{BASE_URL}/admin/providers/add"
# Update with valid staging admin credentials
TEST_EMAIL    = "testuser@example.com"
TEST_PASSWORD = "Password123!"
# Minimum expected number of hospitals (should be > 100)
MIN_HOSPITALS   = 101


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

class TestAddProviderDoctorAffiliatedHospitals:
    """End-to-end tests for adding a doctor provider and checking affiliated hospitals list."""

    def test_affiliated_hospitals_list_is_complete(self, page: Page):
        """
        Navigate to add provider page, select doctor type, and verify that
        the affiliated hospitals checkbox list contains all hospitals (more than 100).
        """
        login(page)
        page.goto(ADD_PROVIDER_URL)

        # ── Select provider type as Doctor ──────────────────────────────────────
        # Adjust selector to match the provider type selection (dropdown, radio, etc.)
        doctor_option = page.get_by_label(re.compile("doctor|provider type", re.IGNORECASE))
        if doctor_option.is_visible():
            doctor_option.select_option("doctor")  # or click if radio
        else:
            page.get_by_text(re.compile("doctor", re.IGNORECASE)).click()

        # Wait for the form to update with doctor-specific fields
        page.wait_for_timeout(1000)  # Adjust if needed

        # ── Locate the affiliated hospitals section ─────────────────────────────
        # Adjust selector for the hospitals list container
        hospitals_section = page.locator(
            "[data-testid='affiliated-hospitals'], .hospitals-list, #hospitals"
        ).first

        # Find all checkboxes or options in the hospitals list
        hospital_checkboxes = hospitals_section.locator("input[type='checkbox']")
        # If not checkboxes, perhaps options in a select
        if hospital_checkboxes.count() == 0:
            hospital_checkboxes = page.locator("select[name*='hospital'] option")

        # Count the number of hospitals
        num_hospitals = hospital_checkboxes.count()

        # ── Assert that the list is complete (not truncated to 100) ─────────────
        assert num_hospitals >= MIN_HOSPITALS, (
            f"Affiliated hospitals list has only {num_hospitals} items, "
            f"expected at least {MIN_HOSPITALS} (indicating the list is complete)"
        )

        # Optional: Verify that the list is visible and interactive
        expect(hospitals_section).to_be_visible()
<parameter name="filePath">/workspaces/ratedoc-tests/e2e/tests/Ian_Grinarml_test_add_provider_doctor_affiliated_hospitals.py