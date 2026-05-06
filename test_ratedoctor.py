from playwright.sync_api import Page

BASE_URL = "https://ratedoctor.io/diagnostics"
TEST_CITY = "Cumilla"


def open_diagnostics_page(page: Page):
    page.goto(BASE_URL, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)


def search_by_location(page: Page, city: str):
    # Open Location dropdown
    page.get_by_text("Location", exact=True).click()
    page.wait_for_timeout(1000)

    # Select Cumilla
    page.get_by_text(city, exact=True).click()
    page.wait_for_timeout(1000)

    # Click Search
    page.get_by_role("button", name="Search").click()
    page.wait_for_timeout(4000)


def get_locations(page: Page):
    return page.locator("text=/.*, Bangladesh/").all_inner_texts()


def assert_only_city_results(locations, city):
    assert len(locations) > 0, "No diagnostic centers were found."

    wrong_locations = [loc for loc in locations if city not in loc]

    assert len(wrong_locations) == 0, (
        f"Expected only {city} results, but found non-{city} results: {wrong_locations[:5]}"
    )


def test_43_location_search_works(page: Page):
    page.set_default_timeout(30000)

    open_diagnostics_page(page)
    search_by_location(page, TEST_CITY)

    locations = get_locations(page)

    print("\nTEST 43 - Location Search works")
    for loc in locations[:10]:
        print("-", loc)

    assert_only_city_results(locations, TEST_CITY)


def test_44_filters_work(page: Page):
    page.set_default_timeout(30000)

    open_diagnostics_page(page)
    search_by_location(page, TEST_CITY)

    # Open sort dropdown
    sort_dropdown = page.get_by_text("Highest Rated", exact=True).last
    sort_dropdown.click()
    page.wait_for_timeout(1000)

    # Click Most Reviews
    page.get_by_text("Most Reviews", exact=True).click()
    page.wait_for_timeout(3000)

    most_reviews_locations = get_locations(page)

    print("\nTEST 44 - Most Reviews Filter")
    for loc in most_reviews_locations[:10]:
        print("-", loc)

    assert_only_city_results(most_reviews_locations, TEST_CITY)

    # Open sort dropdown again
    page.get_by_text("Most Reviews", exact=True).last.click()
    page.wait_for_timeout(1000)

    # Click Highest Rated
    page.get_by_text("Highest Rated", exact=True).last.click()
    page.wait_for_timeout(3000)

    highest_locations = get_locations(page)

    print("\nTEST 44 - Highest Rated Filter")
    for loc in highest_locations[:10]:
        print("-", loc)

    assert_only_city_results(highest_locations, TEST_CITY)