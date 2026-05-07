from playwright.sync_api import Page, expect

def test_admin_approves_doctor(page: Page):
    admin_email = "admin@ratedoc.com"
    admin_password = "DeyaJabeNa!023"


    doctor_url = "http://159.89.231.16:3000/doctor/dr-mohammad-rakibul-hasan-chowdhury-743cff31"
    expected_name = "Dr. Mohammad Rakibul Hasan Chowdhury"

    #Login as admin
    page.goto("http://159.89.231.16:3000/auth", wait_until="networkidle")
    print("Logging in as admin...")

    page.fill("input[name='Email']", admin_email)
    page.fill("input[name='Password']", admin_password)
    page.click("button[type='submit']")

    #Wait for dashboard
    page.wait_for_selector("text=Dashboard")

    # Go to Pending Doctors
    page.click("text=Pending Doctors")

    #Approves the doctor (adjust selector if needed)
    approve_buttons = page.locator("button:has-text('Approve')")
    count = approve_buttons.count()

    assert count > 0, "No pending doctors found"

    #Approves all pending doctors
    print("Approving pending doctors...")
    for i in range(count):
        approve_buttons.nth(i).click()
        page.wait_for_timeout(500)
    print(f"Found {count} pending doctors")

    #Navigates to the doctor profile page
    print("Navigating to doctor profile...")
    page.goto(doctor_url, wait_until="networkidle")

    #Verify doctor name
    name_locator = page.locator("h1")  # adjust if needed
    expect(name_locator).to_contain_text(expected_name)

    #Verify hospital count
    hospital_count_locator = page.locator("div:has-text('Affiliated Hospitals')")
    hospital_count_text = hospital_count_locator.text_content()
    print(f"Hospital count: {hospital_count}")

    #Extract number
    import re
    match = re.search(r"\((\d+)\)", hospital_count_text)
    assert match, "Could not find hospital count"
    hospital_count = int(match.group(1))

    assert hospital_count >= 1, "Hospital count should be at least 1"