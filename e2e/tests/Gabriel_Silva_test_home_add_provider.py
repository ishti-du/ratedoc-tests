"""
Gabriel Silva – E2E Test: Home page → Add Provider
===================================================
Test Case:
  Check that clicking the "Add Provider" button on the home page
  navigates the user to the correct provider-submission form.

Assumptions / adjust if needed:
  • The button text is "Add Provider" (or similar – update the locator below).
  • After clicking, the URL changes to a route containing "add-provider" or similar,
    AND a form element is rendered on the page.
  • If the app requires login to reach the form, uncomment the login helper.
"""

import re
import pytest
from playwright.sync_api import Page, expect


BASE_URL = "http://159.89.231.16:3000"


class TestHomeAddProvider:
    """Tests for the 'Add Provider' button on the home page."""

    def test_add_provider_button_is_visible(self, page: Page):
        """The 'Add Provider' button should be visible on the home page."""
        page.goto(BASE_URL)
        # Adjust the selector to match the actual button text / aria-label
        add_provider_btn = page.get_by_role("button", name=re.compile("add provider", re.IGNORECASE))
        # Fall back to a link if the element is an <a> tag
        if not add_provider_btn.is_visible():
            add_provider_btn = page.get_by_role("link", name=re.compile("add provider", re.IGNORECASE))
        expect(add_provider_btn).to_be_visible()

    def test_add_provider_button_navigates_to_form(self, page: Page):
        """
        Clicking 'Add Provider' should take the user to the provider submission form.
        Validates both the URL change and that a form is rendered.
        """
        page.goto(BASE_URL)

        # ── Click the button ────────────────────────────────────────────────────
        # Try button first; fall back to link if rendered as <a>
        add_provider_btn = page.get_by_role("button", name=re.compile("add provider", re.IGNORECASE))
        if not add_provider_btn.is_visible():
            add_provider_btn = page.get_by_role("link", name=re.compile("add provider", re.IGNORECASE))

        add_provider_btn.click()

        # ── URL assertion ───────────────────────────────────────────────────────
        # The destination URL should contain "add" or "provider" or "register"
        # Update the pattern below if the actual route is different
        expect(page).to_have_url(
            re.compile(r"(add.?provider|provider.?add|register.?provider|provider.?register)", re.IGNORECASE),
            timeout=5000,
        )

        # ── Form assertion ──────────────────────────────────────────────────────
        # At least one <form> element should be present on the destination page
        expect(page.locator("form").first).to_be_visible()

    def test_add_provider_form_has_required_fields(self, page: Page):
        """
        The provider submission form should contain the expected input fields
        (name, specialty, contact, etc.). Adjust field locators to match the
        actual form.
        """
        page.goto(BASE_URL)

        add_provider_btn = page.get_by_role("button", name=re.compile("add provider", re.IGNORECASE))
        if not add_provider_btn.is_visible():
            add_provider_btn = page.get_by_role("link", name=re.compile("add provider", re.IGNORECASE))

        add_provider_btn.click()

        # Wait for the form to be present before asserting fields
        page.wait_for_selector("form", timeout=5000)

        # Assert at minimum that the form has at least one text input
        inputs = page.locator("form input[type='text'], form input:not([type])")
        assert inputs.count() > 0, "Expected at least one text input in the Add Provider form"
