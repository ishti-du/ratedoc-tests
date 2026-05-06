import os
from urllib.parse import urljoin

import pytest
from playwright.sync_api import Page, expect


TEST_USER = {
    "email": os.getenv("TEST_USER_EMAIL", "samshtram@gamil.com"),
    "password": os.getenv("TEST_USER_PASSWORD", "beansandcheese"),
    "name": "Sam",
}


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    slow_mo = int(os.getenv("PLAYWRIGHT_SLOW_MO", "0"))
    return {
        **browser_type_launch_args,
        "slow_mo": slow_mo,
    }


def app_url(base_url: str, path: str = "/") -> str:
    return urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))


def login(page: Page, base_url: str) -> None:
    page.goto(app_url(base_url, "/auth"))

    expect(page.get_by_role("heading", name="Welcome back")).to_be_visible(timeout=30_000)
    form = page.locator("form")
    form.get_by_label("Email").fill(TEST_USER["email"])
    form.get_by_label("Password").fill(TEST_USER["password"])

    with page.expect_navigation(wait_until="domcontentloaded", timeout=30_000):
        form.get_by_role("button", name="Sign In").click()


@pytest.fixture
def logged_in_page(page: Page, base_url: str) -> Page:
    login(page, base_url)
    return page
