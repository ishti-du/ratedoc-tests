from playwright.sync_api import Page, expect

def test_review_count_match(page: Page):
    doctor_name = "Dr. Mohammad Rakibul Hasan Chowdhury"

    # Go to homepage
    page.goto("http://159.89.231.16:3000/", wait_until="networkidle")

    # Search
    search_input = page.get_by_placeholder("Search...")
    search_input.fill(doctor_name)
    search_input.press("Enter")

    # Wait for results
    doctor_card = page.locator(".doctor-card").first
    expect(doctor_card).to_be_visible()

    # Extract review count from search results
    search_review_text = doctor_card.locator(".text-gray-600").inner_text()

    # Click the doctor
    doctor_card.click()

    # Extract review count from profile page
    profile_review_text = page.locator("span.text-gray-600").first.inner_text()

    # Helper to extract numbers
    def extract_number(text):
        return int("".join(filter(str.isdigit, text)))

    search_count = extract_number(search_review_text)
    profile_count = extract_number(profile_review_text)

    # Assert match
    assert search_count == profile_count, f"Review count mismatch: search={search_count}, profile={profile_count}"