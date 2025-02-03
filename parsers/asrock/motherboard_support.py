import json
import random
from time import sleep
from bs4 import BeautifulSoup
from lxml import html
from selenium.webdriver.common.by import By

from models.manufacturer import Manufacturer
from models.motherboard_overview import MotherboardOverview
from models.motherboard_techspec import MotherboardTechSpec
from models.motherboard_support import MotherboardSupport
import utils
import utils.cache
import utils.download
import utils.swebdriver

# const prefix for cache key
CACHE_PREFIX = "support_motherboard_item_"

def start_parser_motherboard_support(mbir, mbor, mbtr, mbsr):
    # get all asrock motherboard items from db
    motherboard_items = mbir.getAllMotherboardsByManufacturer(Manufacturer().ASROCK)
    motherboard_support_result = []
    for motherboard_item in motherboard_items:
        key_motherboard_support = CACHE_PREFIX + str(motherboard_item.id)
        # check if cache exists
        json_cache = utils.cache.get_json_cache(key_motherboard_support)
        if json_cache is not None:
            print("cache exists: ", key_motherboard_support)
            continue
        
        # get motherboard_overview by mb_item_id and type link_support
        motherboard_overviews = mbor.getOverviewsByMbItemIdType(motherboard_item.id, MotherboardOverview.TYPE_LINK_SUPPORT)
        if motherboard_overviews is None:
            continue

        for motherboard_overview in motherboard_overviews:
            # start parse asrock motherboard techspec page
            motherboard_support = start_parser_motherboard_support_page(motherboard_overview)
            if motherboard_support is None:
                continue
            for motherboard_support_row in motherboard_support:
                motherboard_support_row.mb_item_id = motherboard_item.id
                motherboard_support_result.append(motherboard_support_row)

            mbsr.add_motherboards_support(motherboard_support)
            # set json cache
            utils.cache.set_json_cache(key_motherboard_support, motherboard_support)
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
    
    # parse content from support page
    print("start_parser_motherboard_support_page: is usual link", motherboard_overview.text)
    mb = []
    mb += parse_motherboard_support_page(motherboard_overview)
    return mb

def parse_motherboard_support_page(motherboard_overview):
    motherboard_supports = []
    
    link = motherboard_overview.text
    driver = utils.swebdriver.create_driver()
    driver.get(link)

    menu_elements = driver.find_elements(By.CSS_SELECTOR, '#sSupport input.Buttons')
    for menu_element in menu_elements:
        menu_element_text = menu_element.get_attribute("value")
        print("menu_element: ", menu_element_text.lower())

        # retrieve the content of the tab and check if it contains "cpu" or "Memory"
        if "cpu" in menu_element_text.lower():
            menu_element.click()
            sleep(10)

            selector_table_header = 'div#CPU.Support table thead tr th'
            table_header_elements = driver.find_elements(By.CSS_SELECTOR, selector_table_header)
            table_header = []
            for table_header_element in table_header_elements:
                # clean the text and trim it
                header_text = table_header_element.text.replace("\n", " ")
                header_text = header_text.strip()
                table_header.append(header_text)

            selector_table_body = 'div#CPU.Support table tbody tr'
            table_body_rows = driver.find_elements(By.CSS_SELECTOR, selector_table_body)
            data_rows = []
            for table_body_row in table_body_rows:
                data_cells = {}
                table_body_columns = table_body_row.find_elements(By.CSS_SELECTOR, 'td')
                for i in range(len(table_body_columns)):
                    data_cells[table_header[i]] = table_body_columns[i].text

                data_rows.append(data_cells)
        elif "memory" in menu_element_text.lower():
            menu_element.click()
            sleep(10)
            # if page has #SelectMemory dropdown, select the each option and get the data
            selector_select_memory = 'select#SelectMemory option'
            select_memory_elements = driver.find_elements(By.CSS_SELECTOR, selector_select_memory)
            # order the select_memory_elements reverse
            select_memory_elements.reverse()
            for select_memory_element in select_memory_elements:
                if select_memory_element.get_attribute("value") is None:
                    continue
                select_memory_element.click()
                sleep(10)
                processor_memory_selector = 'div#Memory h3'
                processor_memory_element = driver.find_element(By.CSS_SELECTOR, processor_memory_selector)
                processor_memory_text = processor_memory_element.text
                print("processor_memory_text: ", processor_memory_text)

                selector_table_header = 'div#Memory table thead tr th'
                table_header_elements = driver.find_elements(By.CSS_SELECTOR, selector_table_header)
                table_header = []
                for table_header_element in table_header_elements:
                    # table_header_element has label , so need value of label
                    thead_element_html = table_header_element.get_attribute("outerHTML")
                    label_element = None
                    if "label" in thead_element_html:
                        label_element = table_header_element.find_element(By.CSS_SELECTOR, 'label')
                    if label_element is not None:
                        header_text = label_element.text.replace("\n", " ")
                    else:
                        header_text = table_header_element.text.replace("\n", " ")

                    # clean the text and trim it
                    header_text = header_text.strip()
                    table_header.append(header_text)
                    
                selector_table_body = 'div#Memory.Support table tbody tr'
                table_body_rows = driver.find_elements(By.CSS_SELECTOR, selector_table_body)
                data_rows = []
                for table_body_row in table_body_rows:
                    data_cells = {}
                    table_body_columns = table_body_row.find_elements(By.CSS_SELECTOR, 'td')
                    if len(table_body_columns) == 0:
                        continue
                    for i in range(len(table_body_columns)):
                        data_cells[table_header[i]] = table_body_columns[i].text

                    data_cells["notice"] = processor_memory_text
                    data_rows.append(data_cells)
                        
        elif "storage" in menu_element_text.lower():
            menu_element.click()
            sleep(10)

            selector_table_header = 'div#Storage.Support table thead tr th'
            table_header_elements = driver.find_elements(By.CSS_SELECTOR, selector_table_header)
            table_header = []
            for table_header_element in table_header_elements:
                # clean the text and trim it
                header_text = table_header_element.text.replace("\n", " ")
                header_text = header_text.strip()
                table_header.append(header_text)

            selector_table_body = 'div#Storage.Support table tbody tr'
            table_body_rows = driver.find_elements(By.CSS_SELECTOR, selector_table_body)
            data_rows = []
            for table_body_row in table_body_rows:
                data_cells = {}
                table_body_columns = table_body_row.find_elements(By.CSS_SELECTOR, 'td')
                for i in range(len(table_body_columns)):
                    data_cells[table_header[i]] = table_body_columns[i].text

                data_rows.append(data_cells)
                        
        if MotherboardSupport.TYPE_CPU in menu_element_text.lower():
            motherboard_supports += make_motherboard_support_from_data_rows(data_rows, MotherboardSupport.TYPE_CPU, motherboard_overview)
        elif MotherboardSupport.TYPE_MEMORY in menu_element_text.lower():
            motherboard_supports += make_motherboard_support_from_data_rows(data_rows, MotherboardSupport.TYPE_MEMORY, motherboard_overview)
        elif "storage" in menu_element_text.lower():
            motherboard_supports += make_motherboard_support_from_data_rows(data_rows, MotherboardSupport.TYPE_DEVICE, motherboard_overview)
            
    driver.quit()
    return motherboard_supports

def make_motherboard_support_from_data_rows(data_rows, type, motherboard_overview):
    motherboard_supports = []
    for data_row in data_rows:
        print("data_row: ", data_row)
        motherboard_support = MotherboardSupport(
            id=None,
            mb_item_id=motherboard_overview.mb_item_id,
            type=type,
            data=json.dumps(data_row)
        )
        motherboard_supports.append(motherboard_support)
    return motherboard_supports
