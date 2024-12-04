from time import sleep
from bs4 import BeautifulSoup
from lxml import html
from selenium.webdriver.common.by import By

from models.motherboard_item import MotherboardItem
from models.manufacturer import Manufacturer
import utils
import utils.download
import utils.swebdriver

start_url = "https://www.asrock.com/mb/"

def start_parser_moterboard_list():
    motherboards_items = [] # MotherboardItem[]
    
    # create swebdriver
    driver = utils.swebdriver.create_driver()
    driver.get(start_url)

    # wait for page to load
    sleep(5)

    # get Category of motherboards #Reset + h6.Category + ul.Categories
    category_elements = driver.find_elements(By.CSS_SELECTOR, "h6.Category")
    for category_element in category_elements:
        is_break = False
        category_text = category_element.text
        # if Category contains "Category" 
        if "Category" in category_text:
            is_break = True
            # get all categories in next ul element
            category_li_items = category_element.find_element(By.XPATH, "following-sibling::ul").find_elements(By.TAG_NAME, "label")
            for category_li_item in category_li_items:
                print(category_li_item.text)
                if "Accessories" in category_li_item.text:
                    continue
                #get atributte "for" from label element to click on input element
                category_for = category_li_item.get_attribute("for")
                # click on category
                driver.execute_script('document.querySelector("label[for=' + category_for + ']").click()')
                # wait for page to load
                sleep(5)
                # get content
                content = driver.page_source
                # parse content
                motherboards_items += parse_content(content)
                # click on category to unselect
                driver.execute_script('document.querySelector("label[for=' + category_for + ']").click()')
                # wait for page to load
                sleep(5)

        if is_break:
            break
                
        
    
    # close driver
    utils.swebdriver.close_driver(driver)

    return motherboards_items

def parse_content(content):
    print("start parse content")
    # parse content to get items list of motherboards from gigabyte website with beautifulsoup
    soup = BeautifulSoup(content, "html.parser")
    items = soup.select("#ListProducts .ModelListBig")
    motherboards_items = []
    if len(items) == 0 or items is None:
        return motherboards_items
    for item in items:
        link = item.select_one("a").get("href")
        if link is not None and link != "" and not link.startswith("http") and link.startswith("/"):
            link = "https://www.asrock.com" + link
            
        orig_id = item.select_one(".CompBtn").get("id")
        name = item.select_one("h6").text
        price = ""
        description = item.text
        description = description.replace("Add to compare", "")
        category = ""
        manufacturer = Manufacturer().ASROCK
        
        # add to motherboards_items
        motherboards_items.append(MotherboardItem(0, orig_id, name, price, link, description, category, manufacturer))

    items = soup.select("#ListProducts .ModelList")
    if len(items) == 0 or items is None:
        return motherboards_items
    for item in items:
        link = item.select_one("a").get("href")
        if link is not None and link != "" and not link.startswith("http") and link.startswith("/"):
            link = "https://www.asrock.com" + link
            
        orig_id = item.select_one(".CompBtn").get("id")
        name = item.select_one("h6").text
        price = ""
        description = item.text
        description = description.replace("Add to compare", "")
        category = ""
        manufacturer = Manufacturer().ASROCK
        
        # add to motherboards_items
        motherboards_items.append(MotherboardItem(0, orig_id, name, price, link, description, category, manufacturer))
    
    return motherboards_items