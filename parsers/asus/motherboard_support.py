import random
from bs4 import BeautifulSoup

from models.manufacturer import Manufacturer
from models.motherboard_overview import MotherboardOverview
from models.motherboard_techspec import MotherboardTechSpec
from models.motherboard_support import MotherboardSupport
import utils
import utils.download

def start_parser_motherboard_support(mbir, mbor):
    # get all asus motherboard items from db
    motherboard_items = mbir.getAllMotherboardsByManufacturer(Manufacturer().ASUS)
    motherboard_support_result = []
    for motherboard_item in motherboard_items:
        # get motherboard_overview by mb_item_id and type link_support
        motherboard_overviews = mbor.getOverviewsByMbItemIdType(motherboard_item.id, MotherboardOverview.TYPE_LINK_SUPPORT)
        if motherboard_overviews is None:
            continue

        for motherboard_overview in motherboard_overviews:
            # start parse asus motherboard techspec page
            motherboard_support = start_parser_motherboard_support_page(motherboard_overview)
            if motherboard_support is None:
                continue
            for motherboard_support_row in motherboard_support:
                motherboard_support_row.mb_item_id = motherboard_item.id
                motherboard_support_result.append(motherboard_support_row)

    return motherboard_support_result

def start_parser_motherboard_support_page(motherboard_overview):
    if motherboard_overview.type != MotherboardOverview.TYPE_LINK_SUPPORT:
        print("start_parser_motherboard_support_page: not a support link", motherboard_overview.text)
        return
    # if motherboard_overview.text doesn't have /spec/ in it, return
    if "http" not in motherboard_overview.text:
        print("start_parser_motherboard_support_page: is bad link", motherboard_overview.text)
        return
    
    print("start_parser_motherboard_support_page: ", motherboard_overview.text)

    motherboard_support = []

    # random int for sleep time
    sleep_delay = random.randint(1, 5)

    # get content from overview page like motherboard_overview.text
    content = utils.download.download_file(motherboard_overview.text, sleep_time=sleep_delay)
    if content is None:
        return

    # parse content from support page
    motherboard_support += parse_motherboard_support_page(content, motherboard_overview)

    return motherboard_support

def parse_motherboard_support_page(content, motherboard_overview):
    pass