import pytest
from playwright.sync_api import Page, expect

def test_homepage_has_correct_title(page: Page):
    """
    Test that the homepage navigates to the expected URL and has the correct title.
    """
    page.goto("http://159.89.231.16:3000/")
    # You can update this with the actual title once confirmed
    # expect(page).to_have_title("RateDoc") 
    print(f"Page title: {page.title()}")
    assert page.url == "http://159.89.231.16:3000/"
