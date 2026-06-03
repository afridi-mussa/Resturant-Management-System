"""
Captures screenshots of the running BistroSaaS site using Playwright and saves
them into docs/screenshots/. Requires the dev server to be running.

Usage:
    1. Start the server:  python manage.py runserver 8011
    2. Run:               python docs/capture_screenshots.py
"""
import json
import os
import urllib.request

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8011"
ADMIN = ("demo_admin", "BistroDemo2026")
CUSTOMER = ("demo_customer", "BistroDemo2026")

SHOTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
os.makedirs(SHOTS_DIR, exist_ok=True)


def first_item_id():
    try:
        with urllib.request.urlopen(BASE + "/api/menu/?format=json") as resp:
            data = json.load(resp)
        return data[0]["id"] if data else None
    except Exception:
        return None


def login(page, username, password):
    page.goto(BASE + "/login/")
    page.fill('input[name="username"]', username)
    page.fill('input[name="password"]', password)
    page.click('button[type="submit"]')
    page.wait_for_load_state("networkidle")


def shot(page, url, filename, full_page=True):
    page.goto(BASE + url)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(700)
    path = os.path.join(SHOTS_DIR, filename)
    page.screenshot(path=path, full_page=full_page)
    print("Captured:", filename)


def main():
    item_id = first_item_id()
    with sync_playwright() as p:
        browser = p.chromium.launch()

        # ---- Public pages (no login) ----
        pub = browser.new_context(viewport={"width": 1366, "height": 900})
        page = pub.new_page()
        shot(page, "/", "01_menu_page.png")
        shot(page, "/register/", "02_register.png")
        shot(page, "/login/", "03_login.png")
        if item_id:
            shot(page, f"/menu/{item_id}/", "04_item_detail.png")
        shot(page, "/api/menu/", "11_api.png")
        pub.close()

        # ---- Customer pages ----
        cust = browser.new_context(viewport={"width": 1366, "height": 900})
        cpage = cust.new_page()
        login(cpage, *CUSTOMER)
        shot(cpage, "/order/place/", "06_place_order.png")
        shot(cpage, "/my-orders/", "07_my_orders.png")
        shot(cpage, "/profile/", "09_profile.png")
        cust.close()

        # ---- Admin pages ----
        adm = browser.new_context(viewport={"width": 1366, "height": 900})
        apage = adm.new_page()
        login(apage, *ADMIN)
        shot(apage, "/menu/add/", "05_add_item.png")
        shot(apage, "/manage/orders/", "08_manage_orders.png")
        shot(apage, "/admin/", "10_admin.png")
        adm.close()

        browser.close()
    print("All screenshots saved in:", SHOTS_DIR)


if __name__ == "__main__":
    main()
