import json
from models.motherboard_item import MotherboardItem
import utils
import utils.download

start_url = "https://odinapi.asus.com/recent-data/apiv2/SeriesFilterResult?SystemCode=asus&WebsiteCode=global&ProductLevel1Code=motherboards-components&ProductLevel2Code=motherboards&PageSize=20&CategoryName=Intel&SeriesName=&SubSeriesName=&Spec=&SubSpec=&PriceMin=&PriceMax=&Sort=Recommend&siteID=www&sitelang=&PageIndex=%page_index%"

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
        

    return motherboards_items

def parse_content(content):
    json_content = json.loads(content)
    motherboards_items = []
    
    items = json_content["Result"]["ProductList"]
    if len(items) == 0 or items is None:
        return motherboards_items
    
    for item in items:
        # get item details
        orig_id = item["ProductID"]
        name = item["Name"]
        price = item["Price"]
        url = item["ProductURL"]
        description = item["ModelSpec"]
        category = item["CategoryName"]
        manufacturer = "Asus"
        
        # add to motherboards_items
        motherboards_items.append(MotherboardItem(0, orig_id, name, price, url, description, category, manufacturer))

    return motherboards_items