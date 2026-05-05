from playwright.sync_api import Page


def test_mohamed_affiliated_hospitals_filter_bug_exists(page: Page):
    page.set_default_timeout(15000)

    selected_city = "Narayanganj"

    page.goto("https://ratedoctor.io/", wait_until="domcontentloaded")

    # Sign in
    page.get_by_text("Sign In", exact=False).first.click()
    page.locator("input[type='email']").fill("parumpudici6@gmail.com")
    page.locator("input[type='password']").fill("Parum1234")
    page.locator("button:has-text('Sign In')").last.click()

    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1000)

    # Go to Add Provider
    page.get_by_text("Add Provider", exact=False).click()
    page.wait_for_timeout(1000)

    # Doctor tab
    page.get_by_role("tab", name="Doctor").click()

    # Select country
    page.get_by_label("Country").click()
    page.locator("[role='option']").filter(has_text="Bangladesh").first.click()

    # Select city
    page.get_by_label("City").click()
    page.locator("[role='option']").filter(has_text=selected_city).first.click()

    page.wait_for_timeout(1000)

    # Scroll to Affiliated Hospitals
    page.get_by_text("Affiliated Hospitals", exact=False).scroll_into_view_if_needed()

    # Get all hospital location texts (like "Khulna, Bangladesh")
    hospital_locations = page.locator("text=/.*, Bangladesh/").all_inner_texts()

    # Separate correct vs incorrect
    correct_city_locations = [
        loc for loc in hospital_locations if selected_city in loc
    ]

    wrong_city_locations = [
        loc for loc in hospital_locations if selected_city not in loc
    ]

    # If bug exists → print helpful QA-style message
    if wrong_city_locations:
        print("\n ERROR FOUND:")
        print(f"Selected city: {selected_city}")

        print("\n Expected result:")
        print(f"Only hospitals from '{selected_city}, Bangladesh' should be listed.")

        if correct_city_locations:
            print("\n Example of correct entries:")
            for loc in correct_city_locations[:5]:
                print(f"- {loc}")
        else:
            print("\n No hospitals from the selected city were found at all.")

        print("\n issue:")
        print("Hospitals from other cities are being shown --> filtering is broken.")

    # Test PASSES when bug is found
    assert len(wrong_city_locations) > 0, (
        "Bug was not found. All displayed hospitals matched the selected city."
    )