import random
from time import sleep
from bs4 import BeautifulSoup
from lxml import html
import json
from models.motherboard_item import MotherboardItem
import utils
import utils.download

start_url = "https://en.colorful.cn/en/Home/GetProductPageList?mid=84&categoryIds=&pageSize=6&pageIndex=%page_index%"

def start_parser_moterboard_list():
    motherboards_items = [] # MotherboardItem[]
    page = 1
    while True:
        url = start_url.replace('%page_index%', str(page))
        page += 1
        print("Start parsing: " + url)
        # sleep for random time
        sleep_rand = random.randint(1, 5)
        # download content
        content = utils.download.download_file(url, sleep_time=sleep_rand)
        if content is None:
            break

        # parse content
        tmp_motherboards_items = parse_content(content)
        if len(tmp_motherboards_items) == 0:
            break

        print("End parsing: " + url)

        # add to motherboards_items
        motherboards_items += tmp_motherboards_items
        

    return motherboards_items

def parse_content(content):
    json_content = json.loads(content)
    motherboards_items = []
    
    items = json_content["data"]
    if len(items) == 0 or items is None:
        return motherboards_items
    
    for item in items:
        # get item details
        orig_id = item["id"]
        name = item["title"]
        price = ""
        url = "https://en.colorful.cn/en/home/product?mid=84&id=" + str(orig_id)
        description = ""
        category = ""
        manufacturer = "colorful"
        
        # add to motherboards_items
        motherboards_items.append(MotherboardItem(0, orig_id, name, price, url, description, category, manufacturer))

    return motherboards_items