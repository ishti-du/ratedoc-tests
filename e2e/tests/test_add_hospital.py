import os
import re

from playwright.sync_api import Page, expect


BASE_URL = os.getenv("RATEDOC_BASE_URL", "http://159.89.231.16:3000")


def test_hospital_add_provider_entry_point(page: Page):
    """Verify the public hospital page exposes the add-provider sign-in gate."""
    page.goto(f"{BASE_URL}/hospitals")

    expect(page.get_by_role("heading", name="Find a Hospital")).to_be_visible()
    expect(page.get_by_text("Explore hospital ratings, services, and patient experiences")).to_be_visible()

    page.get_by_role("link", name=re.compile(r"Add Provider", re.I)).click()

    expect(page).to_have_url(re.compile(r".*/auth$"))
    expect(page.get_by_role("heading", name="Welcome back")).to_be_visible()
    expect(page.get_by_label("Email")).to_be_visible()
    expect(page.get_by_label("Password")).to_be_visible()
