import pytest
import re
from playwright.sync_api import Page, expect, sync_playwright

@pytest.fixture(scope="session", params=["chromium"])
def browser_context(request):
    with sync_playwright() as p:
        browser = getattr(p, request.param).launch(headless=True)
        context = browser.new_context()
        yield context


@pytest.fixture
def page(browser_context):
    page = browser_context.new_page()
    yield page
    page.close()

# otevření yt playlistu z IT průvodce
def test_to_youtube(page: Page):
    page.goto("https://engeto.cz/")
    
    it_guide_btn = page.locator(".area-pruvodce a[href*='jak-zacit-v-it/']").nth(0)
    it_guide_btn.click()
    youtube_btn = page.locator("div.media-content:nth-child(4) a[href*='youtube.com']")

    with page.context.expect_page() as popup:
        youtube_btn.scroll_into_view_if_needed()
        youtube_btn.click(force=True)  

    new_page = popup.value
    new_page.wait_for_load_state()

    cookie_texts = ["Odmítnout vše", "Reject all", "Decline all", "Reject everything"]
    for text in cookie_texts:
        cookies_button = new_page.locator(".KZ9vpc", has_text=text)
        if cookies_button.count() > 0 and cookies_button.is_visible():
            cookies_button.scroll_into_view_if_needed()
            cookies_button.click()
    
    new_page.wait_for_url(re.compile(r".*youtube\.com/playlist.*"), timeout=15000)
    expect(new_page).to_have_url(re.compile(r".*youtube\.com/playlist.*"))

# kontrola přesměrování na kurz "Testování softwaru"
def test_open_course(page: Page):
    page.goto("https://engeto.cz/")
    show_course_btn = page.locator(".area-kurzy a[href='https://engeto.cz/prehled-kurzu/']")
    show_course_btn.hover()
    show_course_btn.scroll_into_view_if_needed()

    course_button = page.locator(".area-kurzy a[href='https://engeto.cz/testovani-softwaru/']")
    course_button.wait_for()
    course_button.click()
    expect(page).to_have_url("https://engeto.cz/testovani-softwaru/")

# kontrola mobilního menu
def test_mobile_menu(page: Page):
    page.set_viewport_size({"width": 375, "height": 812})
    page.goto("https://engeto.cz/")
    mobile_menu = page.locator(".mobile-menu-toggle")
    mobile_menu.click()

    navigation = page.locator("#top-menu")
    expect(navigation).to_be_visible()
