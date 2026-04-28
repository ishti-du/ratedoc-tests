"""
Gabriel Silva – E2E Test: Home page → Add Provider
===================================================
Test Case:
  Check that clicking the "Add Provider" button on the home page
  navigates the user to the correct provider-submission form.

Notes:
  - The app requires authentication before showing the provider form.
  - Login is performed as a pre-condition for navigation tests.
  - Credentials below must exist in the staging environment.
"""

import re
import pytest
from playwright.sync_api import Page, expect


BASE_URL       = "http://159.89.231.16:3000"
TEST_EMAIL     = "tests1234@gmail.com"
TEST_PASSWORD  = "abc123456"


def login(page: Page) -> None:
    """Log in so the app does not redirect to /auth mid-test."""
    page.goto(f"{BASE_URL}/auth")
    page.locator("input[type='email']").fill(TEST_EMAIL)
    page.locator("input[type='password']").fill(TEST_PASSWORD)
    # Two "Sign In" buttons exist (nav + form) – scope to the form's submit button
    page.locator("form").get_by_role("button", name="Sign In").click()
    # Wait for redirect to home page (login always goes to "/" when no prior location)
    page.wait_for_url(f"{BASE_URL}/", timeout=10000)


class TestHomeAddProvider:
    """Tests for the 'Add Provider' button on the home page."""

    def test_add_provider_button_is_visible(self, page: Page):
        """The 'Add Provider' button should be visible on the home page."""
        login(page)
        page.goto(BASE_URL)

        # Try button first; fall back to link if the element is an <a> tag
        add_provider_btn = page.get_by_role("button", name=re.compile("add provider", re.IGNORECASE))
        if not add_provider_btn.is_visible():
            add_provider_btn = page.get_by_role("link", name=re.compile("add provider", re.IGNORECASE))

        expect(add_provider_btn).to_be_visible()

    def test_add_provider_button_navigates_to_form(self, page: Page):
        """
        Clicking 'Add Provider' should navigate to the provider submission form.
        Validates both the URL change and that a form is rendered on the page.
        """
        login(page)
        page.goto(BASE_URL)

        # Click the button (falls back to link if rendered as <a>)
        add_provider_btn = page.get_by_role("button", name=re.compile("add provider", re.IGNORECASE))
        if not add_provider_btn.is_visible():
            add_provider_btn = page.get_by_role("link", name=re.compile("add provider", re.IGNORECASE))

        add_provider_btn.click()

        # URL should change away from the home page
        expect(page).not_to_have_url(BASE_URL, timeout=5000)

        # At least one <form> element should appear on the destination page
        expect(page.locator("form").first).to_be_visible(timeout=5000)

    def test_add_provider_form_has_required_fields(self, page: Page):
        """
        The provider submission form should contain at least one input field.
        """
        login(page)
        page.goto(BASE_URL)

        add_provider_btn = page.get_by_role("button", name=re.compile("add provider", re.IGNORECASE))
        if not add_provider_btn.is_visible():
            add_provider_btn = page.get_by_role("link", name=re.compile("add provider", re.IGNORECASE))

        add_provider_btn.click()

        # Wait for the form to appear
        page.wait_for_selector("form", timeout=5000)

        # Assert the form has at least one input field
        inputs = page.locator("form input")
        assert inputs.count() > 0, "Expected at least one input in the Add Provider form"
