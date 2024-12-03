import random
from time import sleep
from bs4 import BeautifulSoup
from lxml import html
import json
from models.motherboard_item import MotherboardItem
import utils
import utils.download

start_url = "https://www.gigabyte.com/Ajax/Product/GetConsumerListPageInfo"

def start_parser_moterboard_list():
    motherboards_items = [] # MotherboardItem[]
    page = 1
    while True:
        # sleep for 3 - 8 seconds
        rand_sleep = random.randint(1, 4)

        # download content
        print(f"Start scrape Page: {page}" + "url: " + start_url)
        content = utils.download.download_file(start_url, type="post", data_post={"ClassKey": 2, "PageNumber": page, "PageSize": 12}, sleep_time=rand_sleep)
        if content is None:
            break

        print(f"End scrape Page: {page}" + "url: " + start_url)

        page += 1

        # parse content
        tmp_motherboards_items = parse_content(content)
        if len(tmp_motherboards_items) == 0:
            break

        # add to motherboards_items
        motherboards_items += tmp_motherboards_items
        

    return motherboards_items

def parse_content(content):
    # parse content to get items list of motherboards from gigabyte website with beautifulsoup
    soup = BeautifulSoup(content, "html.parser")
    items = soup.select("div.product_list_box")
    motherboards_items = []
    if len(items) == 0 or items is None:
        return motherboards_items
    
    for item in items:
        # get item details
        orig_id = item.select_one("input.compareCheckBox")
        if orig_id is not None:
            orig_id = orig_id["product-num"]
        else:
            orig_id = ""
        name = item.select_one("div.product_info_text_col a").text
        price = ""
        url = item.select_one("div.product_info_text_col a")["href"]
        if url is not None and url != "" and not url.startswith("http") and url.startswith("/"):
            url = "https://www.gigabyte.com" + url
        description = item.select_one("div.product_info_summary div.gs-summary div")
        if description is not None:
            description = description.text
        else:
            description = ""
        category = ""
        manufacturer = "gigabyte"

        # add to motherboards_items
        motherboards_items.append(MotherboardItem(0, orig_id, name, price, url, description, category, manufacturer))

    return motherboards_items