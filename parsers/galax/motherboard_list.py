import json

from bs4 import BeautifulSoup
from models.motherboard_item import MotherboardItem
import utils
import utils.download

start_url = "https://www.galax.com/en/motherboard.html?p=%page_index%"

def start_parser_moterboard_list():
    motherboards_items = [] # MotherboardItem[]
    motherboards_items_links = []
    page = 1
    while True:
        url = start_url.replace('%page_index%', str(page))
        page += 1

        # download content
        content = utils.download.download_file(url)
        if content is None:
            break

        # parse content
        tmp_motherboards_items = parse_content(content)
        if len(tmp_motherboards_items) == 0:
            break

        is_duplicate = False
        for item_tmp in tmp_motherboards_items:
            if item_tmp.link not in motherboards_items_links:
                motherboards_items_links.append(item_tmp.link)
            else:
                is_duplicate = True
                break

        if is_duplicate:
            break


        # add to motherboards_items
        motherboards_items += tmp_motherboards_items
        

    return motherboards_items

def parse_content(content):
    soup = BeautifulSoup(content, "html.parser")
    items = soup.select("#products-list > li.item")
    motherboards_items = []
    if len(items) == 0 or items is None:
        return motherboards_items
    
    for item in items:
        orig_id = ""
        name = item.select_one(".product-name span").text
        price = ""
        url = item.select_one("h2 a[href]").get("href")
        if url is not None and url != "" and not url.startswith("http"):
            url = "https://www.galax.com" + url

        description = item.select_one("div.desc")
        if description is not None:
            description = description.text

        category = ""
        manufacturer = "galax"

        # add to motherboards_items
        motherboards_items.append(MotherboardItem(0, orig_id, name, price, url, description, category, manufacturer))

    return motherboards_items