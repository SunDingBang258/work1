import re
from playwright.sync_api import expect
def test_user_creates_car_in_browser(page, live_server):
     page.goto(f"{live_server}/cars/new")
     page.get_by_label("Make", exact=True).fill("Toyota")
     page.get_by_label("Model", exact=True).fill("Yaris")
     page.get_by_label("Year", exact=True).fill("2020")
     page.get_by_label("Color", exact=False).fill("Blue")
     page.get_by_role("button", name="Create car").click()
     expect(page).to_have_url(re.compile(r"/cars/\d+$"))
     expect(page.get_by_role("heading", name="Toyota Yaris")).to_be_visible()