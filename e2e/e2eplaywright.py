from playwright.sync_api import sync_playwright, expect

def run_nirmal_tests():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # --- TASK 1: Specialization Search (Doctors Page) ---
        print("Starting Task 1: Specialization Search...")
        page.goto("http://159.89.231.16:3000/doctors")

        dropdown = page.locator("button[role='combobox']").first
        dropdown.click()

        page.get_by_role("option", name="Urology", exact=True).click()

        search_btn = page.locator("button.bg-primary:has-text('Search')")
        search_btn.click()

        # Wait for the initial set of doctor cards to load
        page.wait_for_selector("a.group.block")

        max_pages = 100

        for i in range(1, max_pages + 1):
            print(f"\n--- Checking Page {i} ---")

            # Ensure the doctor elements are fully interactive on the active page
            page.wait_for_selector("a.group.block")

            doctor_cards = page.locator("a.group.block")
            card_count = doctor_cards.count()

            if card_count == 0:
                raise Exception(f"No doctors found on page {i}")

            for j in range(card_count):
                card = doctor_cards.nth(j)

                # Locate the specific specialization badge based on the DOM structure
                specialty_badge = card.locator("div:has(svg.lucide-stethoscope)").first
                expect(specialty_badge).to_be_visible()

                badge_text = specialty_badge.inner_text().strip()

                if "Urology" not in badge_text:
                    doctor_name = card.locator("img").get_attribute("alt") or f"Doctor {j+1}"
                    raise AssertionError(
                        f"❌ FAILED: {doctor_name} on page {i} has '{badge_text}' instead of 'Urology'"
                    )

                if "Neurology" in badge_text:
                    raise AssertionError(
                        f"🐞 BUG: Doctor {j+1} shows 'Neurology' in Urology results (Page {i})"
                    )

            print(f"✅ Page {i} passed")

            # --- Pagination (Upgraded to avoid sticking) ---
            next_button = page.locator("a[aria-label='Go to next page']").first

            if not next_button.is_visible():
                print("Reached last page (no next button found).")
                break

            # Check if button is disabled via attributes before clicking
            btn_class = next_button.get_attribute("class") or ""
            is_aria_disabled = next_button.get_attribute("aria-disabled") == "true"
            if "pointer-events-none" in btn_class.split() or is_aria_disabled:
                print("Reached the last page. Next button is disabled.")
                break

            # Reference the current top doctor element so we can watch it disappear
            old_first_card = page.locator("a.group.block").first

            print(f"Clicking next... transitioning from Page {i} to Page {i+1}")
            next_button.click()

            # STRATEGY: Wait for the old card to completely detach/vanish from the DOM.
            # This forces Playwright to wait until the fresh network data replaces the UI.
            try:
                old_first_card.wait_for(state="detached", timeout=5000)
            except Exception:
                # Fallback if the same exact doctor happens to be first on the next page too
                print("Content did not detach quickly; performing a short timeout fallback.")
                page.wait_for_timeout(1500)

        print("\n🎉 Task 1 completed!")

        # --- TASK 2: Hospital Search (Hospitals Page) ---
        print("\nStarting Task 2: Hospital Search...")
        page.goto("http://159.89.231.16:3000/hospitals")

        hospital_search = page.locator("input[placeholder*='Search']")
        target_hospital = "Bangladesh Multicare Hospital"

        hospital_search.fill(target_hospital)
        hospital_search.press("Enter")

        page.wait_for_selector("body")
        expect(page.locator("body")).to_contain_text(target_hospital)

        print("✅ Task 2 Complete.")

        browser.close()

if __name__ == "__main__":
    run_nirmal_tests()