import json
import re

from playwright.sync_api import Page, Route, expect

DEPARTMENTS = [
    {
        "id": 1,
        "name": "Gastroenterology",
        "description": "Digestive system, stomach pain, abdomen, and intestinal concerns",
    },
    {
        "id": 2,
        "name": "Cardiology",
        "description": "Heart, chest pain, blood pressure, and cardiovascular concerns",
    },
]


def fulfill_departments(route: Route) -> None:
    route.fulfill(
        status=200,
        content_type="application/json",
        body=json.dumps(DEPARTMENTS),
    )


def test_stomach_suggests_gastroenterology(page: Page, base_url: str):
    page.route("**/api/v1/departments**", fulfill_departments)
    page.goto(base_url)

    search_input = page.get_by_placeholder("Search by disease or condition...")
    expect(search_input).to_be_visible(timeout=15_000)
    search_input.fill("Stomach")

    expect(page.get_by_role("button", name=re.compile("Gastroenterology", re.I))).to_be_visible(
        timeout=10_000
    )


def test_heart_suggests_cardiology(page: Page, base_url: str):
    page.route("**/api/v1/departments**", fulfill_departments)
    page.goto(base_url)

    search_input = page.get_by_placeholder("Search by disease or condition...")
    expect(search_input).to_be_visible(timeout=15_000)
    search_input.fill("Heart")

    expect(page.get_by_role("button", name=re.compile("Cardiology", re.I))).to_be_visible(
        timeout=10_000
    )
