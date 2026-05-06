from playwright.sync_api import sync_playwright, expect

def run_nirmal_tests():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # --- TASK 1: Specialization Search (Doctors Page) ---
        print("Starting Task 1: Specialization Search...")
        page.goto("http://159.89.231.16:3000/doctors")
        
        # 1. Click the first combobox (Specializations)
        dropdown = page.locator("button[role='combobox']").first
        dropdown.click()
        
        # 2. Select 'Urology'
        page.get_by_role("option", name="Urology", exact=True).click()
        
        # 3. Click the Search button
        search_btn = page.locator("button.bg-primary:has-text('Search')")
        search_btn.click()
        
# --- MULTI-PAGE CHECK LOGIC ---
        max_pages = 100 
        
        for i in range(1, max_pages + 1):
            print(f"\n--- Checking Page {i} ---")
            page.wait_for_timeout(3000) 
            
            # 4. Assertion: Confirm Urology is found
            expect(page.locator("body")).to_contain_text("Urology")
            
            # 5. BUG CHECK: Confirm Neurology is NOT found
            try:
                expect(page.locator("body")).not_to_contain_text("Neurology")
                print(f"Success: No 'Neurology' on page {i}.")
            except AssertionError:
                print(f"FAILED: Bug confirmed on page {i}! 'Neurology' appeared in Urology results.")
                break 

            # 6. Pagination: Click the Next link safely
            if i < max_pages:
                # Use .first just in case there are multiple pagination menus on the page
                next_button = page.locator("a[aria-label='Go to next page']").first
                
                if next_button.is_visible():
                    btn_class = next_button.get_attribute("class") or ""
                    
                    class_list = btn_class.split()
                    is_aria_disabled = next_button.get_attribute("aria-disabled") == "true"
                    
                    # Now it will only match the exact word, ignoring "disabled:pointer-events-none"
                    if "pointer-events-none" in class_list or is_aria_disabled:
                        print("Reached the last page. 'Next' button is disabled.")
                        break
                    else:
                        print("Moving to the next page...")
                        next_button.click()
                else:
                    print("Reached the last page. No 'Next' button found.")
                    break

        print("\n" + "-" * 30 + "\n")

        # --- TASK 2: Hospital Search (Hospitals Page) ---
        print("Starting Task 2: Hospital Search...")
        page.goto("http://159.89.231.16:3000/hospitals")
        
        hospital_search = page.locator("input[placeholder*='Search']")
        target_hospital = "Bangladesh Multicare Hospital"
        
        hospital_search.fill(target_hospital)
        hospital_search.press("Enter")
        
        page.wait_for_timeout(3000)
        
        expect(page.locator("body")).to_contain_text(target_hospital)
        print("Task 2 Complete.")

        browser.close()

if __name__ == "__main__":
    run_nirmal_tests()