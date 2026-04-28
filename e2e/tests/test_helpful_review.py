import json
import pytest
from pathlib import Path
from playwright.sync_api import sync_playwright

# Config
BASE_URL   = "http://159.89.231.16:3000"
DOCTOR_URL = f"{BASE_URL}/doctor/dr-mohammad-rakibul-hasan-chowdhury-743cff31"
CREDS_FILE = Path(__file__).parent / "credentials.json"
WAIT       = 2000  # ms between actions 


def load_credentials():
    with open(CREDS_FILE) as f:
        return json.load(f)


# Helper functions
def login(page):
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


def go_to_reviews(page):
    page.goto(DOCTOR_URL)
    page.wait_for_load_state("networkidle")
    reviews_tab = page.locator(
        "button:has-text('Reviews'), a:has-text('Reviews'), [role='tab']:has-text('Reviews')"
    )
    if reviews_tab.count() > 0:
        reviews_tab.first.click()
        page.wait_for_timeout(WAIT)


def get_helpful_btn(page):
    return page.locator("button").filter(has_text="Helpful").filter(has_not_text="Not").first


def get_not_helpful_btn(page):
    return page.locator("button:has-text('Not Helpful'), button:has-text('Not helpful')").first


def parse_count(btn):
    text = btn.inner_text()
    if "(" in text and ")" in text:
        inside = text[text.index("(") + 1 : text.index(")")].strip()
        if inside.isdigit():
            return int(inside)
    return 0

def ensure_off(btn, page):
    """
    Ensure a button is in the clean (unvoted) state
    click and check — if count went UP it was OFF (now ON), so click again to turn OFF
    If count went DOWN it was ON (now OFF)
    """
    before = parse_count(btn)
    btn.click()
    page.wait_for_timeout(WAIT)
    after = parse_count(btn)

    if after > before:
        # it was OFF, click again to turn OFF
        btn.click()
        page.wait_for_timeout(WAIT)
    # else: it was ON, iturn it OFF 


def ensure_both_off(page):
    """Ensure both Helpful and Not Helpful are OFF before a test."""
    ensure_off(get_not_helpful_btn(page), page)
    ensure_off(get_helpful_btn(page), page)


# Fixture
@pytest.fixture(scope="module")
def browser_ctx():
    """Opens Playwright browser context"""
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False, slow_mo=800)
        ctx = browser.new_context()
        yield ctx
        ctx.close()
        browser.close()


@pytest.fixture(scope="module")
def page(browser_ctx):
    """
    Creates a new page from the shared browser context, performs login, and
    navigates to the reviews section once for the entire module. Asserts that
    login succeeded before yielding.
    """
    p = browser_ctx.new_page()
    login(p)
    assert "/auth" not in p.url, f"Login failed — still on: {p.url}"
    go_to_reviews(p)
    yield p
    p.close()


# Test Cases
class TestHelpfulToggle:

    def test_helpful_button_is_visible(self, page):
        btn  = get_helpful_btn(page)
        text = btn.inner_text()
        assert btn.is_visible(), "Helpful button not found."
        assert "(" in text and ")" in text, f"No count in button text: '{text}'"

    def test_not_helpful_button_is_visible(self, page):
        btn  = get_not_helpful_btn(page)
        text = btn.inner_text()
        assert btn.is_visible(), "Not Helpful button not found."
        assert "(" in text and ")" in text, f"No count in button text: '{text}'"

    def test_helpful_click_once_increments_by_1(self, page):
        """Helpful(1) Not Helpful(0) -> click Helpful -> Helpful(2) Not Helpful(0)"""
        ensure_both_off(page)

        h_before = parse_count(get_helpful_btn(page))

        get_helpful_btn(page).click()
        page.wait_for_timeout(WAIT)

        h_after = parse_count(get_helpful_btn(page))
        assert h_after == h_before + 1, (
            f"Expected H {h_before} -> {h_before + 1}, got {h_after}"
        )

    def test_helpful_second_click_toggles_off(self, page):
        """Helpful(2) -> click Helpful -> Helpful(1)  [continues from previous test, Helpful is ON]"""
        h_before = parse_count(get_helpful_btn(page))

        get_helpful_btn(page).click()
        page.wait_for_timeout(WAIT)

        h_after = parse_count(get_helpful_btn(page))
        assert h_after == h_before - 1, (
            f"Expected H {h_before} -> {h_before - 1} after toggle OFF, got {h_after}"
        )

    def test_not_helpful_click_once_increments_by_1(self, page):
        """Helpful(1) Not Helpful(0) -> click Not Helpful -> Helpful(1) Not Helpful(1)"""
        ensure_both_off(page)

        h_before  = parse_count(get_helpful_btn(page))
        nh_before = parse_count(get_not_helpful_btn(page))

        get_not_helpful_btn(page).click()
        page.wait_for_timeout(WAIT)

        h_after  = parse_count(get_helpful_btn(page))
        nh_after = parse_count(get_not_helpful_btn(page))

        assert nh_after == nh_before + 1, (
            f"Expected NH {nh_before} -> {nh_before + 1}, got {nh_after}"
        )
        assert h_after == h_before, (
            f"Helpful should stay at {h_before}, got {h_after}"
        )

    def test_not_helpful_second_click_toggles_off(self, page):
        """
        Helpful(1) Not Helpful(1) -> click Not Helpful -> Helpful(1) Not Helpful(0)  
        [continues from previous test, Not Helpful is ON]
        """
        h_before  = parse_count(get_helpful_btn(page))
        nh_before = parse_count(get_not_helpful_btn(page))

        get_not_helpful_btn(page).click()
        page.wait_for_timeout(WAIT)

        h_after  = parse_count(get_helpful_btn(page))
        nh_after = parse_count(get_not_helpful_btn(page))

        assert nh_after == nh_before - 1, (
            f"Expected NH {nh_before} -> {nh_before - 1} after toggle OFF, got {nh_after}"
        )
        assert h_after == h_before, (
            f"Helpful should stay at {h_before}, got {h_after}"
        )

    def test_switching_helpful_to_not_helpful(self, page):
        """
        Helpful(1) Not Helpful(0) -> click Helpful -> Helpful(2) Not Helpful(0) -> 
        click Not Helpful -> Helpful(1) Not Helpful(1)
        """
        ensure_both_off(page)

        h_before  = parse_count(get_helpful_btn(page))
        nh_before = parse_count(get_not_helpful_btn(page))

        get_helpful_btn(page).click()
        page.wait_for_timeout(WAIT)

        h_mid  = parse_count(get_helpful_btn(page))
        nh_mid = parse_count(get_not_helpful_btn(page))
        assert h_mid == h_before + 1, f"After voting H: expected {h_before + 1}, got {h_mid}"
        assert nh_mid == nh_before,   f"NH should stay {nh_before}, got {nh_mid}"

        get_not_helpful_btn(page).click()
        page.wait_for_timeout(WAIT)

        h_after  = parse_count(get_helpful_btn(page))
        nh_after = parse_count(get_not_helpful_btn(page))
        assert h_after == h_before,       f"After switch H->NH: expected H={h_before}, got {h_after}"
        assert nh_after == nh_before + 1, f"After switch H->NH: expected NH={nh_before + 1}, got {nh_after}"

    def test_switching_not_helpful_to_helpful(self, page):
        """
        Helpful(1) Not Helpful(1) -> click Helpful -> Helpful(2) Not Helpful(0)  
        [continues from previous test, Not Helpful is toggle ON]
        """
        h_before  = parse_count(get_helpful_btn(page))
        nh_before = parse_count(get_not_helpful_btn(page))

        get_helpful_btn(page).click()
        page.wait_for_timeout(WAIT)

        h_after  = parse_count(get_helpful_btn(page))
        nh_after = parse_count(get_not_helpful_btn(page))

        assert h_after == h_before + 1,   f"Expected H={h_before + 1}, got {h_after}"
        assert nh_after == nh_before - 1, f"Expected NH={nh_before - 1}, got {nh_after}"

    def test_both_buttons_never_exceed_total(self, page):
        """Total Helpful + Not Helpful must never exceed [original total] + 1 after switching."""
        ensure_both_off(page)

        h_before     = parse_count(get_helpful_btn(page))
        nh_before    = parse_count(get_not_helpful_btn(page))
        total_before = h_before + nh_before

        get_helpful_btn(page).click()
        page.wait_for_timeout(WAIT)
        get_not_helpful_btn(page).click()
        page.wait_for_timeout(WAIT)

        h_after     = parse_count(get_helpful_btn(page))
        nh_after    = parse_count(get_not_helpful_btn(page))
        total_after = h_after + nh_after

        assert total_after <= total_before + 1, (
            f"Total votes exceeded: {total_before} -> {total_after} (H={h_after}, NH={nh_after})"
        )

    def test_helpful_clicks_count_max_1(self, page):
        """5 clicks on Helpful must not push count above baseline + 1."""
        ensure_both_off(page)
        h_before = parse_count(get_helpful_btn(page))

        for _ in range(5):
            get_helpful_btn(page).click()
            page.wait_for_timeout(300)

        page.wait_for_timeout(WAIT)
        h_final = parse_count(get_helpful_btn(page))

        assert h_final <= h_before + 1, (
            f"Clicks pushed count too high: {h_before} -> {h_final}"
        )

    def test_not_helpful_clicks_count_max_1(self, page):
        """5 clicks on Not Helpful must not push count above baseline + 1."""
        ensure_both_off(page)
        nh_before = parse_count(get_not_helpful_btn(page))

        for _ in range(5):
            get_not_helpful_btn(page).click()
            page.wait_for_timeout(300)

        page.wait_for_timeout(WAIT)
        nh_final = parse_count(get_not_helpful_btn(page))

        assert nh_final <= nh_before + 1, (
            f"Clicks pushed count too high: {nh_before} -> {nh_final}"
        )

    def test_count_does_not_accumulate_across_toggles(self, page):
        """Toggle Helpful ON/OFF 3 times then ON — count must not exceed start + 1."""
        ensure_both_off(page)
        h_before = parse_count(get_helpful_btn(page))

        for _ in range(3):
            get_helpful_btn(page).click()   # ON
            page.wait_for_timeout(WAIT)
            get_helpful_btn(page).click()   # OFF
            page.wait_for_timeout(WAIT)

        get_helpful_btn(page).click()       # final ON
        page.wait_for_timeout(WAIT)

        h_final = parse_count(get_helpful_btn(page))
        assert h_final <= h_before + 1, (
            f"Count accumulated across cycles: {h_before} -> {h_final}"
        )