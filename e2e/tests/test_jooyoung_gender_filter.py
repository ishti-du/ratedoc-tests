from playwright.sync_api import Page, expect

BASE_URL = "http://159.89.231.16:3000"


def normalize_gender(text: str) -> str:
    return text.lower().replace("_", " ").strip()


def select_gender_filter(page: Page, gender: str):
    page.get_by_text("All Genders", exact=True).click()
    page.get_by_role("option", name=gender, exact=True).click()
    page.wait_for_timeout(1500)


def assert_all_results_match_gender(page: Page, expected_gender: str):
    gender_texts = page.locator("text=/Gender:/").all_inner_texts()

    assert len(gender_texts) > 0, f"No doctor results found for {expected_gender}"

    for gender_text in gender_texts:
        actual_gender = gender_text.replace("Gender:", "").strip()
        assert normalize_gender(actual_gender) == normalize_gender(expected_gender), (
            f"Expected only {expected_gender}, but found {actual_gender}"
        )


def test_doctors_gender_filter_all_options(page: Page):
    genders_to_test = ["Male", "Female"]

    for gender in genders_to_test:
        page.goto(f"{BASE_URL}/doctors", wait_until="domcontentloaded")

        select_gender_filter(page, gender)

        expect(page.locator("body")).to_contain_text(f"Gender: {gender}", timeout=10000)
        assert_all_results_match_gender(page, gender)