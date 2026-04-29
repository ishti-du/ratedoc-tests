from playwright.sync_api import Page, expect
import random

BASE_URL = "http://159.89.231.16:3000"


def test_add_doctor_basic(page: Page):
    unique_name = f"Dr. Jooyoung Test {random.randint(1000, 9999)}"

    page.goto(f"{BASE_URL}/", wait_until="domcontentloaded")

    # Login with admin account
    page.get_by_role("link", name="Sign In").click()
    page.locator("input[type='email']").fill("admin@ratedoc.com")
    page.locator("input[type='password']").fill("DeyaJabeNa!023")
    page.locator("form").get_by_role("button", name="Sign In").click()

    expect(page.get_by_text("Logout", exact=False)).to_be_visible(timeout=10000)

    # Go to Add Provider page
    page.goto(f"{BASE_URL}/add-provider", wait_until="domcontentloaded")

    # Select Doctor tab
    page.get_by_role("tab", name="Doctor").click()

    # Fill required text fields
    page.get_by_placeholder("Dr. John Smith").fill(unique_name)
    page.get_by_placeholder("e.g., Cardiology, Neurology").fill("Dermatology")
    page.get_by_placeholder("e.g., MBBS, MD, FACC").fill("MBBS")
    page.get_by_placeholder("e.g., A-12345").fill("BMDC-12345")
    page.get_by_placeholder("https://example.com/photo.jpg").fill(
        "https://example.com/photo.jpg"
    )

    # Select dropdowns
    page.locator("select").nth(0).select_option(label="Male")
    page.locator("select").nth(1).select_option(label="Bangladesh")
    page.locator("select").nth(2).select_option(label="Dhaka")
    page.locator("select").nth(3).select_option(label="Dermatology")

    # Submit
    page.get_by_role("button", name="Submit Doctor").click()

    # Verify the site accepted the doctor submission
    expect(page.locator("body")).to_contain_text(
        "Doctor submitted and pending admin approval.", timeout=10000
    )
    expect(page.locator("body")).not_to_contain_text("Something went wrong")
    expect(page.locator("body")).not_to_contain_text("Error")