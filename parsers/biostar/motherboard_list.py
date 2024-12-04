import os
import random
from time import sleep
from bs4 import BeautifulSoup
import certifi
from lxml import html
import json
from models.motherboard_item import MotherboardItem
import utils
import utils.download

# TODO: fix TLS Warnings

start_url = "https://www.biostar.com.tw/app/en/mb/index.php"
category_url = "https://www.biostar.com.tw/app/en/mb/_product_list.php"
certificate_file = "biostar_cacert.pem"

def start_parser_moterboard_list():
    motherboards_items = [] # MotherboardItem[]

    current_dir = os.path.dirname(os.path.realpath(__file__))
    certificate_path = current_dir + "/../../certificates/" + certificate_file

    # check if certificate file exists
    if not os.path.exists(certificate_path):
        certificate_path = certifi.where()

    # download start_url
    content = utils.download.download_file(start_url, verify=False)
    categories = parse_category(content)

    for category in categories:
        # sleep for 3 - 8 seconds
        rand_sleep = random.randint(1, 4)

        # download content
        print(f"Start scrape Category: {category['name']}" + "url: " + start_url)
        data = {
            "product_name": '["'+category['name']+'"]',
            "product_group": '["'+category['group']+'"]',
        }
        content = utils.download.download_file(category_url, type="post", data_post=data, sleep_time=rand_sleep, verify=False)
        if content is None:
            break

        print(f"End scrape Category: {category['name']}" + "url: " + start_url)

        # parse content
        tmp_motherboards_items = parse_content(content)
        if len(tmp_motherboards_items) == 0:
            break

        # add to motherboards_items
        motherboards_items += tmp_motherboards_items
    
    # page = 1
    # while True:
    #     # sleep for 3 - 8 seconds
    #     rand_sleep = random.randint(1, 4)

    #     # download content
    #     print(f"Start scrape Page: {page}" + "url: " + start_url)
    #     content = utils.download.download_file(start_url, type="post", data_post={"ClassKey": 2, "PageNumber": page, "PageSize": 12}, sleep_time=rand_sleep)
    #     if content is None:
    #         break

    #     print(f"End scrape Page: {page}" + "url: " + start_url)

    #     page += 1

    #     # parse content
    #     tmp_motherboards_items = parse_content(content)
    #     if len(tmp_motherboards_items) == 0:
    #         break

    #     # add to motherboards_items
    #     motherboards_items += tmp_motherboards_items
        

    return motherboards_items

def parse_category(content):
    soup = BeautifulSoup(content, "html.parser")
    items = soup.select("div.pr-filter-box .condition-wrap input[name='s_category']")
    categories = []
    if len(items) == 0 or items is None:
        return categories
    for item in items:
        categories.append({
            "name": item["value"],
            "group": item["name"]
        })
    return categories

def parse_content(content):
    # parse content to get items list of motherboards from gigabyte website with beautifulsoup
    soup = BeautifulSoup(content, "html.parser")
    items = soup.select(".pr-box")
    motherboards_items = []
    if len(items) == 0 or items is None:
        return motherboards_items
    
    for item in items:
        # get item details
        orig_id = item.select_one("a")["pr-id"]
        name = item.select_one("div.name").text
        price = ""
        url = item.select_one("a")["href"] 
        if url is not None and url != "" and not url.startswith("http"):
            url = "https://www.biostar.com.tw/app/en/mb/" + url
        description = ""
        category = ""
        manufacturer = "biostar"

        # add to motherboards_items
        motherboards_items.append(MotherboardItem(0, orig_id, name, price, url, description, category, manufacturer))

    return motherboards_items