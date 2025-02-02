import random
from time import sleep
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

from models.manufacturer import Manufacturer
from models.motherboard_overview import MotherboardOverview
import utils
import utils.download
import utils.swebdriver
import utils.utils

def start_parser_motherboard_pages(mbir):
    # get all asus motherboard items from db
    motherboard_items = mbir.getAllMotherboardsByManufacturer(Manufacturer().ASROCK)
    motherboard_overviews_result = []
    it_was = False
    for motherboard_item in motherboard_items:
        # it's for speed up parsing and testing and debugging and development only.
        # remove this line in production
        # if motherboard_item.link == "https://www.asrock.com/mb/Intel/Z590 OC Formula/index.asp":
        #     it_was = True
        # if not it_was:
        #     continue
        # remove this line in production
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
    # content = utils.download.download_file(motherboard_item.link, sleep_time=sleep_delay)
    
    # create swebdriver
    driver = utils.swebdriver.create_driver()
    driver.get(motherboard_item.link)
    # get content
    content = driver.page_source

    # wait for page to load
    sleep(5)
    if content is None:
        return
    
    # parse content from overview page find type link_overview, link_technical_spec, link_support
    motherboard_overviews += parse_motherboard_overview_links(driver, motherboard_item)
    if len(motherboard_overviews) == 0:
        print("motherboard_overviews is empty")
        exit()
    motherboard_overviews_model = parse_motherboard_model(driver, motherboard_item)
    if len(motherboard_overviews_model)==0:
        print("motherboard_overviews_model is empty")
        exit()
    motherboard_overviews += motherboard_overviews_model
    # motherboard_overviews_name = parse_motherboard_name(driver, motherboard_item)
    # if len(motherboard_overviews_name)==0:
    #     print("motherboard_overviews_name is empty")
    #     exit()
    # motherboard_overviews += motherboard_overviews_name    
    motherboard_overviews_desc = parse_motherboard_description(driver, motherboard_item)
    if len(motherboard_overviews_desc)==0:
        print("motherboard_overviews_desc is empty")
        exit()
    motherboard_overviews_image = parse_motherboard_image(driver, motherboard_item)
    if len(motherboard_overviews_image)==0:
        print("motherboard_overviews_image is empty")
        exit()
    motherboard_overviews += motherboard_overviews_desc

    
    return motherboard_overviews


def parse_motherboard_overview_links(driver, motherboard_item):
    motherboard_overviews = []
    
    selectors = [
        ".navbar ul.nav li a",
        "#SubItem li",
        ".aali_tm_header .menu ul a",
        "header nav.header_nav ul li a",
        "#menu-wrap .slimmenu li a",
        ".dizme_tm_header div.menu a",
        ".vlt-navbar .sf-menu li a",
    ]
    current_url = driver.current_url

    for selector in selectors:
        items = driver.find_elements(By.CSS_SELECTOR, selector)
        print("selector items: ", len(items))
        if len(items) == 0 or items is None:
            continue
        for item in items:
            type_item = ""
            link = ""
            item_text = item.get_attribute("textContent")
            if "overview" in item_text.lower():
                type_item = MotherboardOverview.TYPE_LINK_OVERVIEW
                if item.get_attribute("href") is not None and item.get_attribute("href") != "":
                    pass
                else:
                    # get current url of page
                    link = current_url + "#Overview"
                    print("overview link: ", link)
            elif "spec" in item_text.lower():
                type_item = MotherboardOverview.TYPE_LINK_TECHNICAL_SPEC
                # get origin url from link
                link = item.get_attribute("href")
                if link is None or link == "":
                    link = current_url + "#Specification"
                print("spec link: ", link)
            elif "support" in item_text.lower():
                type_item = MotherboardOverview.TYPE_LINK_SUPPORT
                # get origin url from link
                link = item.get_attribute("href")
                if link is None or link == "":
                    link = current_url + "#Support"
                print("support link: ", link)

            if type_item != "":
                motherboard_overviews.append(MotherboardOverview(0, motherboard_item.id, type_item, link))

        if len(motherboard_overviews) > 0:
            break
    
    return motherboard_overviews

def parse_motherboard_model(driver, motherboard_item):
    motherboard_overview = []
    
    models_selectors = [
        "title",
        "#briefModel"
    ]
    for selector in models_selectors:
        items = driver.find_elements(By.CSS_SELECTOR, selector)
        if len(items) == 0 or items is None:
            continue
        for item in items:
            type_item = MotherboardOverview.TYPE_MODEL
            text = item.get_attribute("textContent")
            print("model text: ", text)
            motherboard_overview.append(MotherboardOverview(0, motherboard_item.id, type_item, text))

    return motherboard_overview

def parse_motherboard_name(driver, motherboard_item):
    motherboard_overview = []

    return motherboard_overview

def parse_motherboard_description(driver, motherboard_item):
    motherboard_overview = []
    selectors = [
        "h3 + p",
        ".hero_mddesc",
        "#sOverview .Context",
        ".Banner h3 + div.Context600",
        "#briefDesc li",
        "#home-top p",
        " #about .item h1, #about .item h5,#about .item p, .services-discr",
        ".dizme_tm_section div.dizme_tm_main_title",
        ".vlt-post-content",
    ]

    for selector in selectors:
        items = driver.find_elements(By.CSS_SELECTOR, selector)
        if len(items) == 0 or items is None:
            continue
        for item in items:
            if selector == "h3 + p" or selector == ".Banner h3 + div.Context600":
                type_item = MotherboardOverview.TYPE_DESCRIPTION
                text = item.get_attribute("textContent")
                # get previous element h3
                h3_element = item.find_element(By.XPATH, "preceding-sibling::h3")
                h3_text = h3_element.get_attribute("textContent")
                text = h3_text + " \n " + text
                text = text.strip()
                # remove read more text not 
                text = text.replace("Read more", "")
                print("description text: ", text)
                motherboard_overview.append(MotherboardOverview(0, motherboard_item.id, type_item, text))
            else:
                type_item = MotherboardOverview.TYPE_DESCRIPTION
                text = item.text
                if text is None or text == "":
                    text = item.get_attribute("textContent")
                    # trim text
                    text = text.strip()

                
                # remove read more text not 
                text = text.replace("Read more", "")
                print("description text: ", text)
                motherboard_overview.append(MotherboardOverview(0, motherboard_item.id, type_item, text))

    return motherboard_overview

def parse_motherboard_image(driver, motherboard_item):
    motherboard_overview = []
    selectors = [
        ".carousel-inner .item img",
        ".accslide img.desktop",
        "#sGallery .Gallery a img",
        ".avatar img",
        ".slick-track img",
        "#briefGallery a[data-image]",
        "#portfolio img",
        "#portfolio div.main[data-img-url]",
        "vlt-post-media img",
        ".vlt-section__projects-background img",
    ]

    for selector in selectors:
        items = driver.find_elements(By.CSS_SELECTOR, selector)
        if len(items) == 0 or items is None:
            continue
        for item in items:
            if selector == "#portfolio div.main[data-img-url]":
                type_item = MotherboardOverview.TYPE_IMAGE
                link = item.get_attribute("data-img-url")
                # ternary operator like: link contains http ? link : https://www.asrock.com + link
                link = link if "http" in link else utils.utils.get_url_without_last_part(motherboard_item.link) + "/" + link
                print("image link: ", link)
                motherboard_overview.append(MotherboardOverview(0, motherboard_item.id, type_item, link))
                continue
            if selector == "#briefGallery a[data-image]":
                type_item = MotherboardOverview.TYPE_IMAGE
                link = item.get_attribute("data-image")
                # ternary operator like: link contains http ? link : https://www.asrock.com + link
                link = link if "http" in link else utils.utils.get_origin(motherboard_item.link) + link
                print("image link: ", link)
                motherboard_overview.append(MotherboardOverview(0, motherboard_item.id, type_item, link))
                continue
            type_item = MotherboardOverview.TYPE_IMAGE
            link = item.get_attribute("src")
            print("image link: ", link)
            motherboard_overview.append(MotherboardOverview(0, motherboard_item.id, type_item, link))

    return motherboard_overview