import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://159.89.231.16:3000"

# TC29 - list doctors button on hospital page opens a popup
# Abel Prasad

def test_list_doctors_button_visible(page: Page):
    page.goto(f"{BASE_URL}/hospital/bangladesh-multicare-hospital-0cab9d03")
    page.wait_for_load_state("networkidle")

    btn = page.get_by_role("button", name="List Doctors")
    expect(btn).to_be_visible()

def test_list_doctors_opens_popup(page: Page):
    page.goto(f"{BASE_URL}/hospital/bangladesh-multicare-hospital-0cab9d03")
    page.wait_for_load_state("networkidle")

    page.get_by_role("button", name="List Doctors").click()

    modal = page.locator(".fixed, [role='dialog'], dialog").first
    expect(modal).to_be_visible(timeout=5000)

def test_list_doctors_popup_title(page: Page):
    page.goto(f"{BASE_URL}/hospital/bangladesh-multicare-hospital-0cab9d03")
    page.wait_for_load_state("networkidle")

    page.get_by_role("button", name="List Doctors").click()

    expect(page.get_by_text("Doctors At This Hospital")).to_be_visible(timeout=5000)

def test_list_doctors_popup_has_content(page: Page):
    # just check the popup renders with some text in it
    page.goto(f"{BASE_URL}/hospital/bangladesh-multicare-hospital-0cab9d03")
    page.wait_for_load_state("networkidle")

    page.get_by_role("button", name="List Doctors").click()

    expect(page.get_by_text("Doctors At This Hospital")).to_be_visible(timeout=5000)
    content = page.locator("body").inner_text()
    assert "Doctors At This Hospital" in content

def test_list_doctors_popup_closes(page: Page):
    page.goto(f"{BASE_URL}/hospital/bangladesh-multicare-hospital-0cab9d03")
    page.wait_for_load_state("networkidle")

    page.get_by_role("button", name="List Doctors").click()
    expect(page.get_by_text("Doctors At This Hospital")).to_be_visible(timeout=5000)

    page.keyboard.press("Escape")
    expect(page.get_by_text("Doctors At This Hospital")).to_be_hidden(timeout=3000)