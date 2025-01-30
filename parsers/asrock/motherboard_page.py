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
    motherboard_overviews += parse_motherboard_model(driver, motherboard_item)
    motherboard_overviews += parse_motherboard_name(driver, motherboard_item)
    motherboard_overviews += parse_motherboard_description(driver, motherboard_item)
    motherboard_overviews += parse_motherboard_image(driver, motherboard_item)
    
    return motherboard_overviews


def parse_motherboard_overview_links(driver, motherboard_item):
    motherboard_overviews = []
    
    selectors = [
        ".navbar ul.nav li a",
    ]

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
                    link = motherboard_item.link + "#Overview"
                    print("overview link: ", link)
            elif "spec" in item_text.lower():
                type_item = MotherboardOverview.TYPE_LINK_TECHNICAL_SPEC
                # get origin url from link
                link = item.get_attribute("href")
                print("spec link: ", link)
            elif "support" in item_text.lower():
                type_item = MotherboardOverview.TYPE_LINK_SUPPORT
                # get origin url from link
                link = item.get_attribute("href")
                print("support link: ", link)

            if type_item != "":
                motherboard_overviews.append(MotherboardOverview(0, motherboard_item.id, type_item, link))

    return motherboard_overviews

def parse_motherboard_model(driver, motherboard_item):
    motherboard_overview = []
    
    models_selectors = [
        "title",
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
    ]

    for selector in selectors:
        items = driver.find_elements(By.CSS_SELECTOR, selector)
        if len(items) == 0 or items is None:
            continue
        for item in items:
            type_item = MotherboardOverview.TYPE_DESCRIPTION
            text = item.get_attribute("textContent")
            # get previous element h3
            h3_element = item.find_element(By.XPATH, "preceding-sibling::h3")
            h3_text = h3_element.get_attribute("textContent")
            text = h3_text + " \n " + text
            motherboard_overview.append(MotherboardOverview(0, motherboard_item.id, type_item, text))

    return motherboard_overview

def parse_motherboard_image(driver, motherboard_item):
    motherboard_overview = []
    selectors = [
        ".carousel-inner .item img",
    ]

    for selector in selectors:
        items = driver.find_elements(By.CSS_SELECTOR, selector)
        if len(items) == 0 or items is None:
            continue
        for item in items:
            type_item = MotherboardOverview.TYPE_IMAGE
            link = item.get_attribute("src")
            print("image link: ", link)
            motherboard_overview.append(MotherboardOverview(0, motherboard_item.id, type_item, link))

    return motherboard_overview