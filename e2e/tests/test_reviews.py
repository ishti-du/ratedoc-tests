import re
import time

from playwright.sync_api import Page, expect

from conftest import app_url

REVIEW_DOCTOR = {
    "name": "Dr. John Smith",
    "slug": "dr-john-smith-7a055de9",
}


def review_form(page: Page):
    return page.locator("form").filter(has_text=re.compile("Write a Review for", re.I))


def open_reviews_tab(page: Page, base_url: str) -> None:
    page.goto(app_url(base_url, f"/doctor/{REVIEW_DOCTOR['slug']}"))
    expect(page.get_by_role("heading", name=REVIEW_DOCTOR["name"], exact=True)).to_be_visible(
        timeout=30_000
    )

    reviews_tab = page.get_by_role("tab", name=re.compile("reviews", re.I))
    if reviews_tab.is_visible(timeout=5_000):
        reviews_tab.click()

    expect(page.get_by_text(re.compile("Write a Review for", re.I))).to_be_visible(timeout=15_000)
    expect(page.get_by_role("button", name=re.compile(r"^(Submit Review|Update Review)$"))).to_be_visible(
        timeout=15_000
    )


def set_rating(page: Page, label: str, rating: int) -> None:
    label_node = review_form(page).get_by_text(label, exact=False).first
    group = label_node.locator("xpath=ancestor::div[contains(@class, 'mb-4')][1]")
    rating_row = group.get_by_text("Poor").locator("xpath=ancestor::div[contains(@class, 'flex')][1]")
    rating_row.get_by_role("button").nth(rating - 1).click()


def fill_review_form(page: Page, comment: str, rating: int) -> None:
    form = review_form(page)
    set_rating(page, "Listens & Answers Questions", rating)
    set_rating(page, "Explains Treatment Options", rating)
    set_rating(page, "Provides Effective Treatment", rating)
    set_rating(page, "Office Staff Cooperation", rating)
    form.locator('input[type="date"]').fill(time.strftime("%Y-%m-%d"))
    set_rating(page, "Your Overall Rating", rating)
    form.get_by_placeholder("Share your experience...").fill(comment)


def delete_existing_review_if_present(page: Page) -> None:
    update_button = page.get_by_role("button", name="Update Review")
    if not update_button.is_visible(timeout=5_000):
        return

    delete_button = page.get_by_role("button", name="Delete Review")
    expect(delete_button).to_be_visible(timeout=15_000)

    page.once("dialog", lambda dialog: dialog.accept())
    with page.expect_response(
        lambda response: "/api/v1/reviews/" in response.url
        and response.request.method == "DELETE"
        and response.ok,
        timeout=30_000,
    ):
        delete_button.click()

    expect(page.get_by_role("button", name="Submit Review")).to_be_visible(timeout=15_000)


def test_signed_in_user_can_create_review(logged_in_page: Page, base_url: str):
    page = logged_in_page
    open_reviews_tab(page, base_url)
    delete_existing_review_if_present(page)

    comment = f"E2E create review {int(time.time() * 1000)} with a clear helpful comment."
    fill_review_form(page, comment=comment, rating=4)

    with page.expect_response(
        lambda response: "/api/v1/reviews" in response.url
        and response.request.method == "POST"
        and response.ok,
        timeout=30_000,
    ):
        page.get_by_role("button", name="Submit Review").click()

    expect(page.get_by_role("button", name="Update Review")).to_be_visible(timeout=15_000)
    expect(review_form(page).get_by_placeholder("Share your experience...")).to_have_value(comment)


def test_signed_in_user_can_update_review(logged_in_page: Page, base_url: str):
    page = logged_in_page
    open_reviews_tab(page, base_url)

    update_button = page.get_by_role("button", name="Update Review")
    if not update_button.is_visible(timeout=5_000):
        setup_comment = f"E2E setup review {int(time.time() * 1000)} before update."
        fill_review_form(page, comment=setup_comment, rating=3)
        with page.expect_response(
            lambda response: "/api/v1/reviews" in response.url
            and response.request.method == "POST"
            and response.ok,
            timeout=30_000,
        ):
            page.get_by_role("button", name="Submit Review").click()
        expect(update_button).to_be_visible(timeout=15_000)

    updated_comment = f"E2E updated review {int(time.time() * 1000)} with a new rating."
    fill_review_form(page, comment=updated_comment, rating=5)

    with page.expect_response(
        lambda response: "/api/v1/reviews/" in response.url
        and response.request.method == "PUT"
        and response.ok,
        timeout=30_000,
    ):
        update_button.click()

    expect(review_form(page).get_by_placeholder("Share your experience...")).to_have_value(updated_comment)
    expect(
        page.get_by_role("tabpanel", name=re.compile("Reviews", re.I)).get_by_text(updated_comment)
    ).to_be_visible(timeout=15_000)
