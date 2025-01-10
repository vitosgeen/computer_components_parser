import random
from bs4 import BeautifulSoup

from models.manufacturer import Manufacturer
from models.motherboard_overview import MotherboardOverview
import utils
import utils.download
import utils.utils

def start_parser_motherboard_pages(mbir):
    # get all asus motherboard items from db
    motherboard_items = mbir.getAllMotherboardsByManufacturer(Manufacturer().ASUS)
    motherboard_overviews_result = []
    for motherboard_item in motherboard_items:
        # start parse asus motherboard page
        motherboard_overviews = start_parser_motherboard_page(motherboard_item)
        if motherboard_overviews is None:
            continue
        for motherboard_overview in motherboard_overviews:
            motherboard_overview.mb_item_id = motherboard_item.id
            motherboard_overviews_result.append(motherboard_overview)
    
    return motherboard_overviews_result
        
def start_parser_motherboard_page(motherboard_item):

    print("start_parser_motherboard_page: ", motherboard_item.link)

    motherboard_overviews = []

    # random int for sleep time
    sleep_delay = random.randint(1, 5)

    # get content from overview page like motherboard_item.link
    content = utils.download.download_file(motherboard_item.link, sleep_time=sleep_delay)
    if content is None:
        return
    
    # parse content from overview page find type link_overview, link_technical_spec, link_support
    motherboard_overviews += parse_motherboard_overview_links(content, motherboard_item)
    motherboard_overviews += parse_motherboard_model(content, motherboard_item)
    motherboard_overviews += parse_motherboard_name(content, motherboard_item)
    motherboard_overviews += parse_motherboard_description(content, motherboard_item)
    motherboard_overviews += parse_motherboard_image(content, motherboard_item)

    return motherboard_overviews

def parse_motherboard_overview_page(motherboard):
    pass

def parse_motherboard_technical_spec_page(motherboard):
    pass

def parse_motherboard_support_page(motherboard):
    pass

def parse_motherboard_overview_links(content, motherboard_item):
    links_selectors = [
        "ul.mainTab li a[href]",
        "ul.tabList li a",
    ]
    soup = BeautifulSoup(content, "html.parser")
    motherboard_overview = []
    for selector in links_selectors:
        items = soup.select(selector)
        if len(items) == 0:
            print("Error: asus motherboard overview links not found (selector: %s)" % selector)
            continue
        # find link_overview, link_technical_spec, link_support
        for item in items:
            type_item = ""
            if "overview" in item.text.lower():
                type_item = MotherboardOverview.TYPE_LINK_OVERVIEW
            elif "features" in item.text.lower() or "spec" in item.text.lower():
                type_item = MotherboardOverview.TYPE_LINK_TECHNICAL_SPEC
            elif "tech" in item.text.lower() or "spec" in item.text.lower():
                type_item = MotherboardOverview.TYPE_LINK_TECHNICAL_SPEC
            elif "support" in item.text.lower():
                type_item = MotherboardOverview.TYPE_LINK_SUPPORT
            else:
                continue
            
            href = item.get("href")
            if href is None:
                continue
            if href.find("http") == -1:
                href = utils.utils.get_domain(motherboard_item.link) + href
            motherboard_overview.append(MotherboardOverview(0, motherboard_item.id, type_item, href))
        


    if len(motherboard_overview) == 0:
        print("Error: asus motherboard overview links not found")
        exit()
    return motherboard_overview

def parse_motherboard_name(content, motherboard_item):
    motherboard_overview = []
    soup = BeautifulSoup(content, "html.parser")
    names_selectors = [
        "div[role=main] .KvSummary__productHeadiing__UPRDo",
        "div[role=main] h2.content__title",
        "div[role=main] .kv_info h1",
        "div[role=main] h1.tuf-title",
        ".product-content h1",
        "div[role=main]  h1.txt-linear_blue",
        "#sec-kv figure h1",
        "h1.product-title",
        "h1[class*=\"modelName\"]"
        # "titlle"
    ]
    for selector in names_selectors:
        name_elements = soup.select(selector)
        if len(name_elements) == 0:
            print("Error: asus motherboard name not found (selector: %s)" % selector)
            continue
        for name_element in name_elements:
            # if text contains "logo" that just replace it with one space
            if "logo" in name_element.text.lower():
                name_element.text = name_element.text.replace("logo", " ")
            motherboard_overview.append(MotherboardOverview(0, motherboard_item.id, MotherboardOverview.TYPE_NAME, name_element.text))

    if len(motherboard_overview) == 0:
        print("Error: asus motherboard name not found")
        exit()
    
    return motherboard_overview

def parse_motherboard_model(content, motherboard_item):
    motherboard_overview = []
    soup = BeautifulSoup(content, "html.parser")
    models_selectors = [
        "div[role=main] h1"
    ]
    for selector in models_selectors:
        model_elements = soup.select(selector)
        if len(model_elements) == 0:
            print("Error: asus motherboard model not found (selector: %s)" % selector)
            continue
        for model_element in model_elements:
            class_model = model_element.get("class")
            if class_model is None:
                continue
            # class_model to string
            class_model = " ".join(class_model)
            if "modelName" in class_model:
                motherboard_overview.append(MotherboardOverview(0, motherboard_item.id, MotherboardOverview.TYPE_MODEL, model_element.text))
                break

    if len(motherboard_overview) == 0 and motherboard_item.link.find("rog") != -1:
        return motherboard_overview
        
    if len(motherboard_overview) == 0:
        print("Error: asus motherboard model not found")
        exit()
    
    return motherboard_overview

def parse_motherboard_description(content, motherboard_item):
    description_selectors = [
        "div[role=main] .KvSummary__productIntro__1WXF- ul li",
        "div[role=main] #hd .text-content",
        "div[role=main] .content__info",
        "div[role=main] .kv_info p",
        "#kv.active .text p",
        "#sec-kv figure p",
        "div[role=main] section#kv .text h6",
        "div#sectionOverview .msect div.text div.descr:nth-of-type(1) p:not([class=\"point\"])",
        "div[role=main] section#sectionOverview > span > div:nth-of-type(1) > div:nth-of-type(1) p",
        # "meta[name=description]"
    ]
    soup = BeautifulSoup(content, "html.parser")
    motherboard_overview = []

    for selector in description_selectors:
        description_elements = soup.select(selector)
        if len(description_elements) == 0:
            print("Error: asus motherboard description not found (selector: %s)" % selector)
            continue
        for description_element in description_elements:
            motherboard_overview.append(MotherboardOverview(0, motherboard_item.id, MotherboardOverview.TYPE_DESCRIPTION, description_element.text))

    if len(motherboard_overview) == 0 and motherboard_item.link.find("rog") != -1:
        return motherboard_overview
    if len(motherboard_overview) == 0:
        print("Error: asus motherboard description not found")
        exit()
    return motherboard_overview

def parse_motherboard_image(content, motherboard_item):
    image_selectors = [
        "#galleryThumbnails picture source",
        ".chart__img .figure__img img",
        "#sec-spec .section-content figure img",
        "#tuf-spec .image img",
        "#pageContent-spec figure img",
        "div[class*=\"KvSummary__imageWrapper\"] picture img",
        "#hd #kv img[alt]:not([alt=\"\"],[src*=\"icon\"])",
        "div[class*=\"_ProductImage_\"] > img",
        "#sec-kv figure img.pd",
        ".maintitle img.pic_dissipation",
        ".maintitle img.pd",
        ".pd_box img.pd",
        "div.hero img",
        "section#spec figure > img.lazyLoad[data-src]:not([data-src*=\"-m\"])",
        "#kv .pic img[alt]:not([alt=\"\"],[alt*=\"_\"])",
        "section#sectionOverview span > img",
    ]
    soup = BeautifulSoup(content, "html.parser")
    motherboard_overview = []

    for selector in image_selectors:
        image_elements = soup.select(selector)
        if len(image_elements) == 0:
            print("Error: asus motherboard image not found (selector: %s)" % selector)
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
            motherboard_overview.append(MotherboardOverview(0, motherboard_item.id, MotherboardOverview.TYPE_IMAGE, src))



    if len(motherboard_overview) == 0:
        print("Error: asus motherboard image not found")
        exit()

    return motherboard_overview