import threading

import pytest
from playwright.sync_api import expect, sync_playwright
from werkzeug.serving import make_server

from app import create_app

PORT = 5055


@pytest.fixture(scope="module")
def live_url():
    app = create_app({"TESTING": True})
    server = make_server("127.0.0.1", PORT, app)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{PORT}"
    server.shutdown()


@pytest.mark.e2e
def test_submit_valid_borehole_form_shows_success(live_url):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(live_url + "/")
        page.fill("#name", "BH-E2E-01")
        page.fill("#latitude", "-6.3")
        page.fill("#longitude", "107.1")
        page.fill("#total_depth", "10")
        page.click("#submit")
        expect(page.locator("#result")).to_contain_text("BH-E2E-01")
        browser.close()


@pytest.mark.e2e
def test_submit_negative_depth_shows_error(live_url):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(live_url + "/")
        page.fill("#name", "BH-E2E-02")
        page.fill("#latitude", "-6.3")
        page.fill("#longitude", "107.1")
        page.fill("#total_depth", "-3")
        page.click("#submit")
        expect(page.locator("#error")).to_contain_text("negative")
        browser.close()
