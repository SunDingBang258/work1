
import re
from playwright.sync_api import expect


def test_edits_car(page, live_server):
    # 1. 创建汽车
    page.goto(f"{live_server}/cars/new")
    page.get_by_label("Make", exact=True).fill("Honda")
    page.get_by_label("Model", exact=True).fill("Civic")
    page.get_by_label("Year", exact=True).fill("2022")
    page.get_by_label("Color", exact=False).fill("Blue")

    page.get_by_role("button", name="Create car").click()
    expect(page).to_have_url(re.compile(r"/cars/\d+$"))

    # 2. 进入编辑页面并修改数据

    page.get_by_role("link", name="Edit car").click()
    
    # 等待编辑页面加载完原始数据，再修改表单
    save_button = page.get_by_role("button", name="Save changes")
    expect(save_button).to_be_enabled()
    
    page.get_by_label("Model", exact=True).fill("Accord")
    page.get_by_label("Year", exact=True).fill("2023")
    
    # 确认填写的值没有被异步加载覆盖
    expect(page.get_by_label("Model", exact=True)).to_have_value("Accord")
    expect(page.get_by_label("Year", exact=True)).to_have_value("2023")
#####
    page.get_by_role("button", name="Save changes").click()
    expect(page).to_have_url(re.compile(r"/cars/\d+$"))
    expect(page.get_by_role("heading", name="Honda Accord")).to_be_visible()
    page.reload()
    expect(page.locator("#car-model")).to_have_text("Accord")
    expect(page.locator("#car-year")).to_have_text("2023")

    # # 3. 捕获保存操作发出的 PUT 请求
    # with page.expect_response(
    #     lambda response: "/api/cars/" in response.url
    #     and response.request.method == "PUT"
    # ) as response_info:
    #     page.get_by_role("button", name="Save changes").click()

    # put_response = response_info.value

    # # 4. 检查保存请求的状态
    # assert put_response.status == 200, (
    #     f"PUT failed: status={put_response.status}, "
    #     f"body={put_response.text()}"
    # )

    # # 5. 确认保存后回到汽车详情页面
    # expect(page).to_have_url(re.compile(r"/cars/\d+$"))

    # car_id = page.url.rstrip("/").split("/")[-1]

    # # 6. 独立请求 API，检查后端实际保存的数据
    # api_response = page.request.get(
    #     f"{live_server}/api/cars/{car_id}"
    # )

    # assert api_response.status == 200, (
    #     f"GET failed: status={api_response.status}, "
    #     f"body={api_response.text()}"
    # )

    # saved_car = api_response.json()

    # assert saved_car["model"] == "Accord", (
    #     f"Model was not saved: {saved_car}"
    # )
    # assert saved_car["year"] == 2023, (
    #     f"Year was not saved: {saved_car}"
    # )

    # # 7. 检查详情页面显示正确
    # expect(
    #     page.get_by_role("heading", name="Honda Accord")
    # ).to_be_visible()

    # # 8. 刷新页面，检查数据是否仍然存在
    # page.reload()

    # expect(page.locator("#car-model")).to_have_text("Accord")
    # expect(page.locator("#car-year")).to_have_text("2023")
