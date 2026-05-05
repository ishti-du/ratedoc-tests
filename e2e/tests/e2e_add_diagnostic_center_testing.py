import pytest
from playwright.sync_api import Page, expect


BASE_URL = "http://159.89.231.16:3000"


def test_submit_diagnostic_center(page: Page):
    # Login first
    page.goto(f"{BASE_URL}/auth")
    page.locator("#email").fill("avik@example.com")
    page.locator("#password").fill("password123")
    page.locator("form").get_by_role("button", name="Sign In").click()

    # Wait for redirect after login
    page.wait_for_url(f"{BASE_URL}/", timeout=5000)

    # Navigate to the add provider page
    page.goto(f"{BASE_URL}/add-provider")

    # Click the Diagnostic Center tab
    page.get_by_role("tab", name="Diagnostic Center").click()

    # Fill in a unique center name using timestamp to avoid duplicates
    unique_name = f"Test Diagnostic Center {int(page.evaluate('Date.now()'))}"
    page.locator("#diagnostic-name").fill(unique_name)

    # Select a city
    page.locator("#diagnostic-city").click()
    page.get_by_role("option", name="Dhaka").click()

    # Fill in the address
    page.locator("#diagnostic-address").fill("123 Test Street, Dhaka")

    # Fill in optional fields
    page.locator("#diagnostic-phone").fill("+880 1234 567890")
    page.locator("#diagnostic-website").fill("https://testdiagnostic.com")
    page.locator("#diagnostic-map").fill("https://maps.google.com/?q=Dhaka")

    # Submit the form
    page.get_by_role("button", name="Submit Diagnostic Center").click()

    # Assert success message appears
    expect(page.get_by_text("Diagnostic center submitted and pending admin approval")).to_be_visible(timeout=5000)