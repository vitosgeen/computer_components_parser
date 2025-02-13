import random
import time
from bs4 import BeautifulSoup

from models.manufacturer import Manufacturer
from models.motherboard_overview import MotherboardOverview
import utils
import utils.download
import utils.utils

pages_for_missing = [
    "https://www.gigabyte.com/Motherboard/B650M-C-V2-rev-10",
    "https://www.gigabyte.com/Motherboard/A620M-DS3H-rev-10",
]

def start_parser_motherboard_pages(mbir):
    # get all biostar motherboard items from db
    motherboard_items = mbir.getAllMotherboardsByManufacturer(Manufacturer().BIOSTAR)
    motherboard_overviews_result = []
    it_was = False
    for motherboard_item in motherboard_items:
        print("start_parser_motherboard_page: ", motherboard_item.link)
        # it's for speed up parsing and testing and debugging and development only.
        # remove this line in production
        # if motherboard_item.link == "https://www.biostar.com/Motherboard/GP-OP-AMP-rev-10":
        #     it_was = True
        # if not it_was:
        #     continue
        # remove this line in production
        # start parse biostar motherboard page
        if "GC-TPM" in motherboard_item.link:
            continue
        if "-Bridge" in motherboard_item.link:
            continue
        if "MiniSAS" in motherboard_item.link:
            continue
        if "GP-OP-AMP" in motherboard_item.link:
            continue
        motherboard_overviews = start_parser_motherboard_page(motherboard_item)
        if motherboard_overviews is None:
            continue
        print("motherboard_overviews: ", len(motherboard_overviews))
        for motherboard_overview in motherboard_overviews:
            motherboard_overview.mb_item_id = motherboard_item.id
            motherboard_overviews_result.append(motherboard_overview)

    return motherboard_overviews_result
        
def start_parser_motherboard_page(motherboard_item):

    print("start_parser_motherboard_page: ", motherboard_item.link, motherboard_item.id)

    motherboard_overviews = []
    # get content from overview page like motherboard_item.link
    content = utils.download.download_file_by_selenium_unvisible(motherboard_item.link)
    if content is None:
        return motherboard_overviews

    is_missing = page_for_missing(motherboard_item.link)
    # parse content from overview page find type link_overview, link_technical_spec, link_support
    motherboard_overviews_links = parse_motherboard_overview_links(content, motherboard_item)
    if len(motherboard_overviews_links) == 0:
        print("Error: biostar motherboard overview links not found")
        exit()
    motherboard_overviews += motherboard_overviews_links
    motherboard_overviews_model = parse_motherboard_model(content, motherboard_item)
    if len(motherboard_overviews_model) == 0:
        print("Error: biostar motherboard model not found")
        exit()
    motherboard_overviews += motherboard_overviews_model
    # motherboard_overviews_name = parse_motherboard_name(content, motherboard_item)
    # if len(motherboard_overviews_name) == 0:
    #     print("Error: biostar motherboard name not found")
    #     exit()
    # motherboard_overviews += motherboard_overviews_name
    motherboard_overviews_description = parse_motherboard_description(content, motherboard_item)
    if len(motherboard_overviews_description) == 0 and is_missing == False:
        print("Error: biostar motherboard description not found")
        exit()
    motherboard_overviews += motherboard_overviews_description
    motherboard_overviews_image = parse_motherboard_image(content, motherboard_item)
    if len(motherboard_overviews_image) == 0 and is_missing == False:
        print("Error: biostar motherboard image not found")
        exit()
    motherboard_overviews += motherboard_overviews_image

    return motherboard_overviews

def parse_motherboard_overview_links(content, motherboard_item):
    links_selectors = [
        ".category-controller .m_category .m4-init .drag-container li",
    ]
    soup = BeautifulSoup(content, "html.parser")
    motherboard_overview = []
    for selector in links_selectors:
        items = soup.select(selector)
        if len(items) == 0:
            print("Error: biostar motherboard overview links not found (selector: %s)" % selector)
            continue
        # find link_overview, link_technical_spec, link_support
        for item in items:
            type_item = ""
            if "overview" in item.text.lower():
                type_item = MotherboardOverview.TYPE_LINK_OVERVIEW
            elif "tech" in item.text.lower() or "spec" in item.text.lower():
                type_item = MotherboardOverview.TYPE_LINK_TECHNICAL_SPEC
            elif "support" in item.text.lower():
                type_item = MotherboardOverview.TYPE_LINK_SUPPORT
            else:
                continue
            
            href = item.get("route")
            if href is None:
                continue
            if href.find("http") == -1:
                href = utils.utils.get_url_without_last_part(motherboard_item.link) + "/" + href
            print("parse_motherboard_overview_links: ", type_item, href)
            motherboard_overview.append(MotherboardOverview(0, motherboard_item.id, type_item, href))

    if len(motherboard_overview) == 0:
        print("Error: biostar motherboard overview links not found")
        exit()
    return motherboard_overview

def parse_motherboard_name(content, motherboard_item):
    motherboard_overview = []
    soup = BeautifulSoup(content, "html.parser")
    names_selectors = [
        "#model-header .header-sub-title"
        # "titlle"
    ]
    for selector in names_selectors:
        name_elements = soup.select(selector)
        if len(name_elements) == 0:
            print("Error: biostar motherboard name not found (selector: %s)" % selector)
            continue
        for name_element in name_elements:
            if name_element is None or name_element.text == "":
                continue
            # if text contains "logo" that just replace it with one space
            name_element_text = name_element.text
            if "logo" in name_element.text.lower():
                name_element_text = name_element_text.replace("logo", " ")
            if "Compare" in name_element.text:
                name_element_text = name_element_text.replace("Compare", " ")
            print("parse_motherboard_name: ", name_element_text.strip())
            motherboard_overview.append(MotherboardOverview(0, motherboard_item.id, MotherboardOverview.TYPE_NAME, name_element_text.strip()))

    if len(motherboard_overview) == 0:
        print("Error: biostar motherboard name not found")
        exit()
    
    return motherboard_overview

def parse_motherboard_model(content, motherboard_item):
    motherboard_overview = []
    soup = BeautifulSoup(content, "html.parser")
    models_selectors = [
        ".info-block .info-text .main p",
    ]
    for selector in models_selectors:
        model_elements = soup.select(selector)
        if len(model_elements) == 0:
            print("Error: biostar motherboard model not found (selector: %s)" % selector)
            continue
        for model_element in model_elements:
            print("parse_motherboard_model: ", model_element.text)
            motherboard_overview.append(MotherboardOverview(0, motherboard_item.id, MotherboardOverview.TYPE_MODEL, model_element.text))

    return motherboard_overview

def parse_motherboard_description(content, motherboard_item):
    description_selectors = [
        ".info-block .info-text .text ul li",
        ".info-detail-wrap .box-inner .text-wrap .text",
    ]
    soup = BeautifulSoup(content, "html.parser")
    motherboard_overview = []

    for selector in description_selectors:
        description_elements = soup.select(selector)
        if len(description_elements) == 0:
            print("Error: biostar motherboard description not found (selector: %s)" % selector)
            continue
        for description_element in description_elements:
            # check length of text
            if len(description_element.text) < 10:
                continue
            motherboard_overview.append(MotherboardOverview(0, motherboard_item.id, MotherboardOverview.TYPE_DESCRIPTION, description_element.text))

    return motherboard_overview

def parse_motherboard_image(content, motherboard_item):
    image_selectors = [
        ".swiper-block .swiper-main img",
    ]
    soup = BeautifulSoup(content, "html.parser")
    motherboard_overview = []

    for selector in image_selectors:
        image_elements = soup.select(selector)
        if len(image_elements) == 0:
            print("Error: biostar motherboard image not found (selector: %s)" % selector)
            continue
        for image_element in image_elements:
            src = ""
            #if has srcset
            if image_element.get("srcset") is not None:
                src = image_element.get("srcset")
            # if has data-src
            elif image_element.get("data-src") is not None:
                src = image_element.get("data-src")
            # if has src
            elif image_element.get("src") is not None:
                src = image_element.get("src")
            else:
                continue

            # if src is started with // add https: to src
            if src.find("//") == 0:
                src = "https:" + src

            # if src is not started with http add origin to src
            if src.find("http") == -1:
                src = utils.utils.get_origin(motherboard_item.link) + src

            motherboard_overview.append(MotherboardOverview(0, motherboard_item.id, MotherboardOverview.TYPE_IMAGE, src))
    return motherboard_overview

def page_for_missing(link):
    for page in pages_for_missing:
        if page in link:
            return True
    return False