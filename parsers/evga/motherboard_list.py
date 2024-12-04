from bs4 import BeautifulSoup
from lxml import html
import json
from models.motherboard_item import MotherboardItem
import utils
import utils.download

start_url = "https://www.evga.com/products/productlist.aspx?type=%page_index%"

def start_parser_moterboard_list():
    motherboards_items = [] # MotherboardItem[]
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

        # add to motherboards_items
        motherboards_items += tmp_motherboards_items
        break
        

    return motherboards_items

def parse_content(content):
    soup = BeautifulSoup(content, "html.parser")
    items = soup.select("#ctl00_LFrame_prdList_rlvProdList_ctrl0_pnlGroupContainer > ul > li")
    motherboards_items = []
    if len(items) == 0 or items is None:
        return motherboards_items
    
    for item in items:
        # get item details
        orig_id = item.select_one("p.pl-list-pn")
        if orig_id is not None:
            orig_id = orig_id.text
        name = item.select_one("div.pl-list-pname")
        if name is not None:
            name = name.text
        price = item.select_one(".pl-list-price span")
        if price is not None:
            price = price.text
        url = item.select_one("a[href]")
        if url is not None:
            url = url["href"]
        if url is not None and url != "" and not url.startswith("http"):
            url = "https://www.evga.com" + url
        description = ""
        category = ""
        manufacturer = "evga"

        # add to motherboards_items
        motherboards_items.append(MotherboardItem(0, orig_id, name, price, url, description, category, manufacturer))

    return motherboards_items