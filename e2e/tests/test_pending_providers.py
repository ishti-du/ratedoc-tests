import json
import random
import pytest
from pathlib import Path
from playwright.sync_api import sync_playwright

# Config
BASE_URL   = "http://159.89.231.16:3000"
CREDS_FILE = Path(__file__).parent / "credentials.json"
WAIT       = 2000  # ms between actions


def load_credentials():
    with open(CREDS_FILE) as f:
        return json.load(f)


# Helper functions
def user_login(page):
    """Log in using the regular user credentials from credentials.json."""
    creds = load_credentials()
    page.goto(f"{BASE_URL}/auth")
    page.wait_for_load_state("networkidle")

    email_input = page.locator("input[type='email'], input[name='email']")
    email_input.wait_for(state="visible")
    email_input.click()
    email_input.fill(creds["email"])

    pw_input = page.locator("input[type='password'], input[name='password']")
    pw_input.wait_for(state="visible")
    pw_input.click()
    pw_input.fill(creds["password"])

    with page.expect_navigation(wait_until="networkidle", timeout=15000):
        pw_input.press("Enter")


def admin_login(page):
    """Log in using the admin credentials from credentials.json."""
    creds = load_credentials()
    page.goto(f"{BASE_URL}/auth")
    page.wait_for_load_state("networkidle")

    email_input = page.locator("input[type='email'], input[name='email']")
    email_input.wait_for(state="visible")
    email_input.click()
    email_input.fill(creds["admin"])

    pw_input = page.locator("input[type='password'], input[name='password']")
    pw_input.wait_for(state="visible")
    pw_input.click()
    pw_input.fill(creds["admin_password"])

    with page.expect_navigation(wait_until="networkidle", timeout=15000):
        pw_input.press("Enter")


def logout(page):
    """Log out by clicking the Logout button at the top of the page."""
    logout_btn = page.locator("button:has-text('Logout')").first
    logout_btn.wait_for(state="visible", timeout=10000)
    logout_btn.click()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(WAIT)


def submit_diagnostic_center(page, center_name):
    """
    As a logged-in user, navigate to /add-provider, click the Diagnostic
    Center tab, fill in Center Name / City / Address, and submit.
    """
    page.goto(f"{BASE_URL}/add-provider")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(WAIT)

    # Click the Diagnostic Center tab (Radix UI — id ends with -trigger-diagnostic)
    diag_tab = page.locator("button[role='tab'][id$='-trigger-diagnostic']").first
    diag_tab.wait_for(state="visible", timeout=10000)
    diag_tab.click()
    page.wait_for_timeout(WAIT)

    # Fill Center Name
    center_name_input = page.locator("#diagnostic-name")
    center_name_input.wait_for(state="visible", timeout=10000)
    center_name_input.click()
    center_name_input.fill(center_name)

    # Open the City combobox and pick a random option
    city_trigger = page.locator("#diagnostic-city")
    city_trigger.wait_for(state="visible", timeout=10000)
    city_trigger.click()
    page.wait_for_timeout(500)

    city_options = page.locator("[role='option']").all()
    if city_options:
        random.choice(city_options).click()
    page.wait_for_timeout(500)

    # Fill Address (textarea, not input)
    address_input = page.locator("#diagnostic-address")
    address_input.wait_for(state="visible", timeout=10000)
    address_input.click()
    address_input.fill("123")

    # Submit
    submit_btn = page.locator(
        "button[type='submit']:has-text('Submit Diagnostic Center')"
    ).first
    submit_btn.wait_for(state="visible", timeout=10000)
    submit_btn.click()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(WAIT)


def get_pending_approve_buttons(page):
    """Return a locator for all Approve buttons currently on the page."""
    return page.locator("button:has(svg.lucide-circle-check-big)")


def get_first_pending_provider_info(page):
    """
    Extract the display name AND profile href of the first provider in the
    pending list. Returns a dict: {"name": str, "profile_url": str|None}.
    """
    name = None
    profile_url = None

    name_candidates = [
        "table tbody tr:first-child td:nth-child(1)",
        "table tbody tr:first-child td:nth-child(2)",
        "[class*='card']:first-child h3",
        "[class*='card']:first-child h2",
        "[class*='provider']:first-child [class*='name']",
    ]
    for selector in name_candidates:
        loc = page.locator(selector).first
        if loc.count() > 0:
            raw = loc.inner_text().strip()
            candidate = raw.split("\n")[0].strip()
            if candidate:
                name = candidate
                break

    profile_loc = page.locator(
        "table tbody tr:first-child a[href*='/doctor/'], "
        "table tbody tr:first-child a[href*='/provider/']"
    ).first
    if profile_loc.count() > 0:
        href = profile_loc.get_attribute("href")
        if href:
            profile_url = href if href.startswith("http") else f"{BASE_URL}{href}"

    return {"name": name, "profile_url": profile_url}


def approve_first_provider(page):
    """Click the first Approve button and wait for the UI to update."""
    approve_btn = get_pending_approve_buttons(page).first
    approve_btn.wait_for(state="visible", timeout=10000)
    approve_btn.click()
    page.wait_for_timeout(WAIT)


def click_view_site(page):
    """Click the View Site button to return to the public-facing site."""
    view_site_btn = page.locator("button:has-text('View Site')").first
    view_site_btn.wait_for(state="visible", timeout=10000)
    view_site_btn.click()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(WAIT)


def search_provider_public(page, name):
    """
    Type a provider name into the public site search box and press Enter.
    Then click the 'All' filter tab so all provider types are shown.
    """
    search_input = page.locator(
        "input[placeholder*='disease'], "
        "input[placeholder*='condition'], "
        "input[placeholder*='Search']"
    ).first
    search_input.wait_for(state="visible", timeout=10000)
    search_input.click()
    search_input.fill(name)
    search_input.press("Enter")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(WAIT)

    # Click the "All" tab 
    all_btn = page.locator("button[role='tab'][id$='-trigger-all']").first
    all_btn.wait_for(state="visible", timeout=10000)
    all_btn.click()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(WAIT)


# Fixture
@pytest.fixture(scope="module")
def browser_ctx():
    """Launches a shared Chromium browser context for the module."""
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False, slow_mo=800)
        ctx = browser.new_context()
        yield ctx
        ctx.close()
        browser.close()


@pytest.fixture(scope="module")
def page(browser_ctx):
    """
    Single page used for the entire module:
      1. Log in as regular user → submit a test Diagnostic Center → logout.
      2. Log in as admin → navigate to /admin/providers.
    """
    p = browser_ctx.new_page()

    # submit the test provider
    user_login(p)
    assert "/auth" not in p.url, f"User login failed — still on: {p.url}"

    center_name = f"Test Diagnostic Center {random.randint(1000, 9999)}"
    TestPendingProviders.submitted_provider_name = center_name
    submit_diagnostic_center(p, center_name)
    print(f"\n[SETUP] Submitted provider as user: '{center_name}'")

    # logout
    logout(p)

    # Admin
    admin_login(p)
    assert "/auth" not in p.url, f"Admin login failed — still on: {p.url}"
    p.goto(f"{BASE_URL}/admin/providers")
    p.wait_for_load_state("networkidle")
    p.wait_for_timeout(WAIT)

    yield p
    p.close()


# ---------------------------------------------------------------------------
# Test Cases
# ---------------------------------------------------------------------------

class TestPendingProviders:
    """
    End-to-end tests for the Pending Providers admin workflow.

    Setup (fixture):
      - Logs in as a regular user, submits a Diagnostic Center, logs out.
      - Logs in as admin and lands on /admin/providers.

    Tests:
      1.  Sidebar tab is visible.
      2.  At least one pending provider exists.
      3.  Capture the first pending provider's name + profile URL.
      4.  Approve the provider — pending count decreases by 1.
      5.  Stats / page state reflects the approval.
      6.  View Site returns to the public site.
      7.  Search shows the newly approved provider (All filter).
      8.  Navigate to provider profile (search result click or direct URL).
      9.  Cleanup — delete the provider via Manage Providers.
    """

    submitted_provider_name = None   # set in fixture before tests run
    approved_provider_name  = None   # get from test 3
    approved_provider_url   = None   # get from test 3

    # Check to see if Pending Providers tab exists
    def test_pending_providers_tab_is_visible(self, page):
        """The Pending Providers sidebar link should be visible."""
        pending_tab = page.locator(
            "a[href='/admin/providers'], "
            "a:has-text('Pending Providers'), "
            "div:has(svg.lucide-file-check):has-text('Pending Providers')"
        ).first
        assert pending_tab.is_visible(), (
            "Pending Providers sidebar tab not visible. "
            f"Current URL: {page.url}"
        )

    # Check that at least 1 pending provider
    def test_at_least_one_pending_provider_exists(self, page):
        """There must be at least one Approve button visible."""
        btns = get_pending_approve_buttons(page)
        assert btns.count() > 0, (
            "No pending providers found. "
            f"Current URL: {page.url}. "
            "The provider submitted in setup may not have appeared yet."
        )

    # Get provider name for future tests
    def test_get_pending_provider_name(self, page):
        """Extract and store the first pending provider's name and profile URL."""
        info = get_first_pending_provider_info(page)
        assert info["name"], (
            "Could not extract a provider name from the pending list. "
            "Adjust the selectors in get_first_pending_provider_info()."
        )
        TestPendingProviders.approved_provider_name = info["name"]
        TestPendingProviders.approved_provider_url  = info["profile_url"]
        print(f"\n[INFO] Provider to approve: '{info['name']}'")
        print(f"[INFO] Profile URL: {info['profile_url']}")

    # Approve provider 
    def test_approve_first_provider_decreases_pending_count(self, page):
        """
        Clicking Approve removes the row — Approve button count must drop by 1.
        Re-navigates to /admin/providers after approval if needed.
        """
        before_count = get_pending_approve_buttons(page).count()
        assert before_count > 0, "No Approve buttons found before approving."

        approve_first_provider(page)

        # if "/admin/providers" not in page.url:
        #     page.goto(f"{BASE_URL}/admin/providers")
        #     page.wait_for_load_state("networkidle")
        #     page.wait_for_timeout(WAIT)

        after_count = get_pending_approve_buttons(page).count()
        assert after_count == before_count - 1, (
            f"Expected Approve button count to drop from {before_count} "
            f"to {before_count - 1}, but got {after_count}."
        )

    # View Site after approval
    def test_view_site_navigates_to_main(self, page):
        """Clicking View Site should land on the public-facing site."""
        click_view_site(page)
        assert BASE_URL in page.url, (
            f"Expected to land on main site ({BASE_URL}), but URL is: {page.url}"
        )

    # Search for the approved provider
    def test_search_shows_approved_provider(self, page):
        """
        Search for the approved provider by name, click the 'All' filter
        tab, and assert at least one matching result appears.
        """
        provider_name = TestPendingProviders.approved_provider_name
        assert provider_name, "No provider name captured — cannot run search test."

        search_provider_public(page, provider_name)

        results = page.locator(
            "a, [class*='card'], [class*='result'], [class*='doctor'], div, li"
        ).filter(has_text=provider_name)

        assert results.count() > 0, (
            f"No search results found for '{provider_name}' on the public site "
            "after clicking the 'All' filter. The provider may not be indexed yet."
        )
        print(f"\n[INFO] Search result count for '{provider_name}': {results.count()}")

    # Open provider after search
    def test_click_provider_opens_profile(self, page):
        """
        Click the first search result containing the provider name.
        Fallback: navigate directly to the profile URL captured pre-approval.
        """
        provider_name = TestPendingProviders.approved_provider_name
        profile_url   = TestPendingProviders.approved_provider_url
        assert provider_name, "No provider name captured."

        result = page.locator(
            "a, [class*='card'], [class*='result'], [class*='doctor']"
        ).filter(has_text=provider_name).first

        if result.count() > 0 and result.is_visible():
            result.click()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(WAIT)
        elif profile_url:
            print(f"\n[INFO] No clickable result — navigating directly to {profile_url}")
            page.goto(profile_url)
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(WAIT)
        else:
            pytest.fail(
                f"Cannot open profile for '{provider_name}': "
                "no search result visible and no profile URL was captured."
            )

        assert provider_name in page.inner_text("body"), (
            f"Provider name '{provider_name}' not found on profile page. "
            f"Current URL: {page.url}"
        )

    # cleanup 
    def test_cleanup_delete_approved_provider(self, page):
        """
        Navigate directly to Admin > Manage Providers, search for the
        approved provider, click 'Diagnostic Center' to filter, then
        delete via the trash button.
        """
        provider_name = TestPendingProviders.approved_provider_name
        assert provider_name, "No provider name captured — cannot run cleanup."

        # 1. Go directly to Manage Providers page
        page.goto(f"{BASE_URL}/admin/manage-providers")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(WAIT)

        # 2. Search for the provider by name
        name_search = page.locator("input[placeholder='Search by name...']").first
        name_search.wait_for(state="visible", timeout=10000)
        name_search.click()
        name_search.fill(provider_name)
        name_search.press("Enter")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(WAIT)

        # 3. Click 'Diagnostic Center' filter button to surface the provider
        diag_btn = page.locator(
            "button:has-text('Diagnostic Center'), "
            "[role='tab']:has-text('Diagnostic Center'), "
            "a:has-text('Diagnostic Center')"
        ).first
        if diag_btn.count() > 0 and diag_btn.is_visible():
            diag_btn.click()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(WAIT)

        # 4. Click the trash icon button
        trash_btn = page.locator("button:has(svg.lucide-trash2)").first
        trash_btn.wait_for(state="visible", timeout=10000)
        trash_btn.click()
        page.wait_for_timeout(WAIT)

        # 5. Confirm deletion dialog if present
        confirm_btn = page.locator(
            "button:has-text('Confirm'), button:has-text('Yes'), "
            "[role='alertdialog'] button:has-text('Delete'), "
            "[role='dialog'] button:has-text('Delete')"
        ).first
        if confirm_btn.count() > 0 and confirm_btn.is_visible():
            confirm_btn.click()
            page.wait_for_timeout(WAIT)

        # 6. Re-search to confirm provider is gone
        name_search2 = page.locator("input[placeholder='Search by name...']").first
        if name_search2.count() > 0 and name_search2.is_visible():
            name_search2.fill(provider_name)
            name_search2.press("Enter")
            page.wait_for_timeout(WAIT)

        remaining = page.locator(f"text='{provider_name}'").count()
        assert remaining == 0, (
            f"Provider '{provider_name}' is still visible after deletion."
        )
        print(f"\n[INFO] Successfully deleted provider: '{provider_name}'")