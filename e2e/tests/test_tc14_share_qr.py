import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://159.89.231.16:3000"

# TC14 - share button on doctor page should open a QR code popup
# Abel Prasad

def test_share_button_visible(page: Page):
    page.goto(f"{BASE_URL}/doctor/dr-mohammad-rakibul-hasan-chowdhury-743cff31")
    page.wait_for_load_state("networkidle")

    share_btn = page.get_by_role("button", name="Share")
    expect(share_btn).to_be_visible()

def test_share_button_opens_popup(page: Page):
    page.goto(f"{BASE_URL}/doctor/dr-mohammad-rakibul-hasan-chowdhury-743cff31")
    page.wait_for_load_state("networkidle")

    page.get_by_role("button", name="Share").click()

    modal = page.locator(".fixed, [role='dialog'], dialog").first
    expect(modal).to_be_visible(timeout=5000)

def test_share_popup_has_qr_code(page: Page):
    page.goto(f"{BASE_URL}/doctor/dr-mohammad-rakibul-hasan-chowdhury-743cff31")
    page.wait_for_load_state("networkidle")

    page.get_by_role("button", name="Share").click()

    # there should be a qr code image in the popup
    qr = page.locator("img[src*='qr'], canvas, svg").first
    expect(qr).to_be_visible(timeout=5000)

def test_share_popup_title(page: Page):
    page.goto(f"{BASE_URL}/doctor/dr-mohammad-rakibul-hasan-chowdhury-743cff31")
    page.wait_for_load_state("networkidle")

    page.get_by_role("button", name="Share").click()

    expect(page.get_by_text("Share this provider")).to_be_visible(timeout=5000)

def test_share_popup_close(page: Page):
    page.goto(f"{BASE_URL}/doctor/dr-mohammad-rakibul-hasan-chowdhury-743cff31")
    page.wait_for_load_state("networkidle")

    page.get_by_role("button", name="Share").click()
    expect(page.get_by_text("Share this provider")).to_be_visible(timeout=5000)

    page.keyboard.press("Escape")
    expect(page.get_by_text("Share this provider")).to_be_hidden(timeout=3000)