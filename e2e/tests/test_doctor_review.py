import os
import re

from playwright.sync_api import Page, expect


BASE_URL = os.getenv("RATEDOC_BASE_URL", "http://159.89.231.16:3000")


def test_doctor_review_sign_in_gate(page: Page):
    """Verify a public doctor page prompts users to sign in before writing a review."""
    page.goto(f"{BASE_URL}/doctor/dr-mohammad-rakibul-hasan-chowdhury-743cff31")

    expect(page.get_by_role("heading", name="Dr. Mohammad Rakibul Hasan Chowdhury")).to_be_visible()
    expect(page.get_by_text("Sign in to write a review")).to_be_visible()

    page.get_by_role("complementary").get_by_role("link", name=re.compile(r"Sign In", re.I)).click()

    expect(page).to_have_url(re.compile(r".*/auth$"))
    expect(page.get_by_role("heading", name="Welcome back")).to_be_visible()
    expect(page.get_by_label("Email")).to_be_visible()
    expect(page.get_by_label("Password")).to_be_visible()
