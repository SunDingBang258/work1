import re
from playwright.sync_api import expect
def test_edits_car(page, live_server):
    page.goto(f"{live_server}/cars/new")
    page.get_by_label("Make", exact=True).fill("Honda")
    page.get_by_label("Model", exact=True).fill("Civic")
    page.get_by_label("Year", exact=True).fill("2022")
    page.get_by_label("Color", exact=False).fill("Blue")
    page.get_by_role("button", name="Create car").click()
    expect(page).to_have_url(re.compile(r"/cars/\d+$"))
    # expect(
    #     page.get_by_role("button", name="Edit car")
    # ).to_be_visible()
    page.get_by_role("link", name="Edit car").click()
    page.get_by_label("Model", exact=True).fill("Accord")
    page.get_by_label("Year", exact=True).fill("2023")
    # page.get_by_role("button", name="Save changes").click()

    with page.expect_response(
        lambda response: "/api/cars/" in response.url
        and response.request.method == "PUT"
    ) as response_info:
        page.get_by_role("button", name="Save changes").click()
    
    response = response_info.value
    
    print("PUT status:", response.status, flush=True)
    print("PUT response:", response.text(), flush=True)
    
    expect(page).to_have_url(re.compile(r"/cars/\d+$"))
    
    car_id = page.url.rstrip("/").split("/")[-1]
    api_response = page.request.get(
        f"{live_server}/api/cars/{car_id}"
    )
    
    print("GET status:", api_response.status, flush=True)
    print("GET response:", api_response.text(), flush=True)
    
    expect(page.get_by_role("heading", name="Honda Accord")).to_be_visible()
    
    # expect(page).to_have_url(re.compile(r"/cars/\d+$"))
    # expect(page.get_by_role("heading", name="Honda Accord")).to_be_visible()
    page.reload()
    expect(page.locator("#car-model")).to_have_text("Accord")
    expect(page.locator("#car-year")).to_have_text("2023")

    response = response_info.value
    
    car_id = page.url.rstrip("/").split("/")[-1]
    api_response = page.request.get(
        f"{live_server}/api/cars/{car_id}"
    )
    
    assert response.status == 200, (
        f"PUT failed: status={response.status}, body={response.text()}"
    )
    
    assert api_response.status == 200, (
        f"GET failed: status={api_response.status}, "
        f"body={api_response.text()}"
    )
    
    assert "Accord" in api_response.text(), (
        f"PUT returned {response.text()}; "
        f"GET returned {api_response.text()}"
    )
