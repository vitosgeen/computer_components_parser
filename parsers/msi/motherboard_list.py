from lxml import html
import json

from models.motherboard_item import MotherboardItem
from models.manufacturer import Manufacturer
import utils
import utils.download

start_url = "https://www.msi.com/api/v1/product/getProductList?product_line=mb&page_size=12&sort=default&page_number=%page_index%"

def start_parser_moterboard_list():
    motherboards_items = [] # MotherboardItem[]
    page = 1
    while True:
        url = start_url.replace('%page_index%', str(page))
        page += 1

        # download content
        content = utils.download.download_file_by_selenium(url)
        if content is None:
            break

        # parse content
        tmp_motherboards_items = parse_content(content)
        if len(tmp_motherboards_items) == 0:
            break

        # add to motherboards_items
        motherboards_items += tmp_motherboards_items
        

    return motherboards_items

def parse_content(content):
    tree = html.fromstring(content)
    text = tree.xpath('//pre/text()')
    if len(text) == 0:
        return None
    json_content = json.loads(text[0])
    motherboards_items = []
    
    items = json_content["result"]["getProductList"]
    if len(items) == 0 or items is None:
        return motherboards_items
    
    for item in items:
        # get item details
        orig_id = item["id"]
        name = item["title"]
        price = ""
        url = "https://www.msi.com/Motherboard/" + item["link"]
        description = item["desc"]
        category = ""
        manufacturer = Manufacturer().MSI
        
        # add to motherboards_items
        motherboards_items.append(MotherboardItem(0, orig_id, name, price, url, description, category, manufacturer))

    return motherboards_items