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
# def start_parser_motherboard_support_multi_thread(mbir, mbor, mbtr, mbsr):
#     # get all msi motherboard items from db
#     motherboard_items = mbir.getAllMotherboardsByManufacturer(Manufacturer().MSI)
#     # devide the list into 4 parts like chunks
#     chunks = [motherboard_items[x:x+4] for x in range(0, len(motherboard_items), 4)]
#     motherboard_support_result = []
#     # iterate over the chunks with threads to speed up the process
#     for chunk in chunks:
#         motherboard_support_result += utils.threading.run_threaded(start_parser_motherboard_support_chunk, chunk, mbir, mbor, mbtr, mbsr)


# def start_parser_motherboard_support_chunk(mbir, mbor, mbtr, mbsr):

def start_parser_motherboard_support(mbir, mbor, mbtr, mbsr):
    # get all msi motherboard items from db
    motherboard_items = mbir.getAllMotherboardsByManufacturer(Manufacturer().MSI)
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
            # start parse msi motherboard techspec page
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
    if "rog." in motherboard_overview.text:
        print("start_parser_motherboard_support_page: is rog link", motherboard_overview.text)
        return parse_motherboard_support_page_rog(motherboard_overview)
    elif "tuf." in motherboard_overview.text:
        print("start_parser_motherboard_support_page: is tuf link", motherboard_overview.text)
        mb = []
        mb += parse_motherboard_support_page(motherboard_overview)
        if len(mb) == 0:
            mb += parse_motherboard_support_page_rog(motherboard_overview)
        return mb
    else:
        print("start_parser_motherboard_support_page: is usual link", motherboard_overview.text)
        mb = []
        mb += parse_motherboard_support_page(motherboard_overview)
        if len(mb) == 0:
            mb += parse_motherboard_support_page_rog(motherboard_overview)
        return mb

def parse_motherboard_support_page_rog(motherboard_overview):
    motherboard_supports = []
    
    link = motherboard_overview.text
    driver = utils.swebdriver.create_driver()
    driver.get(link)

    menu_elements = driver.find_elements(By.CSS_SELECTOR, '[class^="Tabs__tabs"] ul[role="tablist"] li')
    if len(menu_elements) == 0:
        tab_title_element = driver.find_element(By.CSS_SELECTOR, 'h2[class^="ProductSupportContent__tabTitle__"]')
        print("tab_title_element: ", tab_title_element.text.lower())
        
        selector_table_header = '[class^="ProductSupportRightArea__"] table thead tr th'
        table_header_elements = driver.find_elements(By.CSS_SELECTOR, selector_table_header)
        table_header = []
        for table_header_element in table_header_elements:
            # clean the text and trim it
            header_text = table_header_element.text.replace("\n", " ")
            header_text = header_text.strip()
            table_header.append(header_text)
        selector_table_body = '[class^="ProductSupportRightArea__"] table tbody tr'
        table_body_rows = driver.find_elements(By.CSS_SELECTOR, selector_table_body)
        data_rows = []
        for table_body_row in table_body_rows:
            data_cells = {}
            table_body_columns = table_body_row.find_elements(By.CSS_SELECTOR, 'td')
            for i in range(len(table_body_columns)):
                table_body_column_text = table_body_columns[i].text.replace(" GO", "")
                data_cells[table_header[i]] = table_body_column_text

            data_rows.append(data_cells)
            
        if MotherboardSupport.TYPE_MEMORY in tab_title_element.text.lower():
            selector_rows = '[class^="ProductSupportVersionFile__productSupportVersionFileBox"]'
            element_rows = driver.find_elements(By.CSS_SELECTOR, selector_rows)
            for i in range(len(element_rows)):
                element_row = element_rows[i]
                release_date = element_row.find_element(By.CSS_SELECTOR, '[class^="ProductSupportVersionFile__releaseDate"]').text
                file_title = element_row.find_element(By.CSS_SELECTOR, '[class^="ProductSupportVersionFile__boxContentTitle"]').text
                file_url = element_row.find_element(By.CSS_SELECTOR, '[class^="ProductSupportVersionFile__boxRight"] a').get_attribute("href")
                data_cells = {}
                data_cells["Release Date"] = release_date
                data_cells["File Title"] = file_title
                data_cells["File URL"] = file_url
                data_rows.append(data_cells)
    
        if MotherboardSupport.TYPE_CPU in tab_title_element.text.lower():
            motherboard_supports += make_motherboard_support_from_data_rows(data_rows, MotherboardSupport.TYPE_CPU, motherboard_overview)
        elif MotherboardSupport.TYPE_MEMORY in tab_title_element.text.lower():
            motherboard_supports += make_motherboard_support_from_data_rows(data_rows, MotherboardSupport.TYPE_MEMORY, motherboard_overview)
        elif MotherboardSupport.TYPE_DEVICE in tab_title_element.text.lower():
            motherboard_supports += make_motherboard_support_from_data_rows(data_rows, MotherboardSupport.TYPE_DEVICE, motherboard_overview)
        driver.quit()
        return motherboard_supports
    menu_element_count = 0;
    for menu_element in menu_elements:
        if menu_element.text == "" or menu_element.text is None or menu_element is None:
            continue
        print("menu_element: ", menu_element.text.lower())
        # retrieve the content of the tab and check if it contains "cpu" or "Memory"
        if "cpu" in menu_element.text.lower():
            tab_index = menu_element.get_attribute("tabindex")
            execute_script_str = "document.querySelectorAll('ul[role=\"tablist\"] li[tabindex]')[" + str(menu_element_count) + "].click()"
            menu_element_count += 1
            print("execute_script_str: ", execute_script_str)
            driver.execute_script(execute_script_str)
            sleep(10)
            # get elements sub menu
            sub_menu_elements = driver.find_elements(By.CSS_SELECTOR, 'ul.productSupportSubTab0 li')
            tab_index_sub_menu = 0
            sub_menu_element_texts = []
            for sub_menu_element in sub_menu_elements:
                sub_menu_element_texts.append(sub_menu_element.text.lower())

            for sub_menu_element in sub_menu_elements:
                sub_menu_element_text = sub_menu_element_texts[tab_index_sub_menu]
                print("sub_menu_element_text: ", sub_menu_element_text)
                execute_script_str = "document.querySelectorAll('ul.productSupportSubTab0 li')[" + str(tab_index_sub_menu) + "].click()"
                print("execute_script_str: ", execute_script_str)
                driver.execute_script(execute_script_str)
                sleep(10)
                tab_index_sub_menu += 1
                selector_table_header = '[class^="ProductSupportRightArea__"] table thead tr th'
                table_header_elements = driver.find_elements(By.CSS_SELECTOR, selector_table_header)
                table_header = []
                for table_header_element in table_header_elements:
                    # clean the text and trim it
                    header_text = table_header_element.text.replace("\n", " ")
                    header_text = header_text.strip()
                    table_header.append(header_text)

                # pagination [class^="Pagination__pageNumber__"]
                selector_pagination = '[class^="Pagination__pageNumber__"]'
                pagination_elements = driver.find_elements(By.CSS_SELECTOR, selector_pagination)
                if len(pagination_elements) > 0:
                    for key, pagination_element in enumerate(pagination_elements):
                        execute_script_str = "document.querySelectorAll('div[class^=\"Pagination__pageNumber__\"]')[" + str(key) + "].click()"
                        print("execute_script_str: ", execute_script_str)
                        driver.execute_script(execute_script_str)
                        sleep(10)
                        selector_table_body = '[class^="ProductSupportRightArea__"] table tbody tr'
                        table_body_rows = driver.find_elements(By.CSS_SELECTOR, selector_table_body)
                        data_rows = []
                        for table_body_row in table_body_rows:
                            data_cells = {}
                            table_body_columns = table_body_row.find_elements(By.CSS_SELECTOR, 'td')
                            for i in range(len(table_body_columns)):
                                data_cells[table_header[i]] = table_body_columns[i].text

                            data_rows.append(data_cells)
                        
                        if MotherboardSupport.TYPE_CPU in sub_menu_element_text:
                            motherboard_supports += make_motherboard_support_from_data_rows(data_rows, MotherboardSupport.TYPE_CPU, motherboard_overview)
                        elif MotherboardSupport.TYPE_MEMORY in sub_menu_element_text:
                            motherboard_supports += make_motherboard_support_from_data_rows(data_rows, MotherboardSupport.TYPE_MEMORY, motherboard_overview)
                        elif MotherboardSupport.TYPE_DEVICE in sub_menu_element_text:
                            motherboard_supports += make_motherboard_support_from_data_rows(data_rows, MotherboardSupport.TYPE_DEVICE, motherboard_overview)
                else:
                    selector_table_body = '[class^="ProductSupportRightArea__"] table tbody tr'
                    table_body_rows = driver.find_elements(By.CSS_SELECTOR, selector_table_body)
                    data_rows = []
                    for table_body_row in table_body_rows:
                        data_cells = {}
                        table_body_columns = table_body_row.find_elements(By.CSS_SELECTOR, 'td')
                        for i in range(len(table_body_columns)):
                            table_body_column_text = table_body_columns[i].text.replace(" GO", "")
                            data_cells[table_header[i]] = table_body_column_text

                        data_rows.append(data_cells)
                    if MotherboardSupport.TYPE_MEMORY in sub_menu_element_text:
                        selector_rows = '[class^="ProductSupportVersionFile__productSupportVersionFileBox"]'
                        element_rows = driver.find_elements(By.CSS_SELECTOR, selector_rows)
                        for i in range(len(element_rows)):
                            element_row = element_rows[i]
                            release_date = element_row.find_element(By.CSS_SELECTOR, '[class^="ProductSupportVersionFile__releaseDate"]').text
                            file_title = element_row.find_element(By.CSS_SELECTOR, '[class^="ProductSupportVersionFile__boxContentTitle"]').text
                            file_url = element_row.find_element(By.CSS_SELECTOR, '[class^="ProductSupportVersionFile__boxRight"] a').get_attribute("href")
                            data_cells = {}
                            data_cells["Release Date"] = release_date
                            data_cells["File Title"] = file_title
                            data_cells["File URL"] = file_url
                            data_rows.append(data_cells)

                    
                    if MotherboardSupport.TYPE_CPU in sub_menu_element_text:
                        motherboard_supports += make_motherboard_support_from_data_rows(data_rows, MotherboardSupport.TYPE_CPU, motherboard_overview)
                    elif MotherboardSupport.TYPE_MEMORY in sub_menu_element_text:
                        motherboard_supports += make_motherboard_support_from_data_rows(data_rows, MotherboardSupport.TYPE_MEMORY, motherboard_overview)
                    elif MotherboardSupport.TYPE_DEVICE in sub_menu_element_text:
                        motherboard_supports += make_motherboard_support_from_data_rows(data_rows, MotherboardSupport.TYPE_DEVICE, motherboard_overview)
        break
    
    driver.quit()
    return motherboard_supports


def parse_motherboard_support_page(motherboard_overview):
    motherboard_supports = []
    
    link = motherboard_overview.text
    driver = utils.swebdriver.create_driver()
    driver.get(link)

    menu_elements = driver.find_elements(By.CSS_SELECTOR, '[class^="Tabs__tabs"] ul[role="tablist"] li')
    for menu_element in menu_elements:
        print("menu_element: ", menu_element.text.lower())
        # retrieve the content of the tab and check if it contains "cpu" or "Memory"
        if "cpu" in menu_element.text.lower():
            tab_index = menu_element.get_attribute("tabindex")
            execute_script_str = "document.querySelector('ul[role=\"tablist\"] li[tabindex=\"" + tab_index + "\"]').click()"
            print("execute_script_str: ", execute_script_str)
            driver.execute_script(execute_script_str)
            sleep(10)
            # get elements sub menu
            sub_menu_elements = driver.find_elements(By.CSS_SELECTOR, 'ul.productSupportSubTab0 li')
            tab_index_sub_menu = 0
            sub_menu_element_texts = []
            for sub_menu_element in sub_menu_elements:
                sub_menu_element_texts.append(sub_menu_element.text.lower())

            for sub_menu_element in sub_menu_elements:
                sub_menu_element_text = sub_menu_element_texts[tab_index_sub_menu]
                print("sub_menu_element_text: ", sub_menu_element_text)
                execute_script_str = "document.querySelectorAll('ul.productSupportSubTab0 li')[" + str(tab_index_sub_menu) + "].click()"
                print("execute_script_str: ", execute_script_str)
                driver.execute_script(execute_script_str)
                sleep(10)
                tab_index_sub_menu += 1
                selector_table_header = '[class^="ProductSupportRightArea__"] table thead tr th'
                table_header_elements = driver.find_elements(By.CSS_SELECTOR, selector_table_header)
                table_header = []
                for table_header_element in table_header_elements:
                    # clean the text and trim it
                    header_text = table_header_element.text.replace("\n", " ")
                    header_text = header_text.strip()
                    table_header.append(header_text)

                # pagination [class^="Pagination__pageNumber__"]
                selector_pagination = '[class^="Pagination__pageNumber__"]'
                pagination_elements = driver.find_elements(By.CSS_SELECTOR, selector_pagination)
                if len(pagination_elements) > 0:
                    for key, pagination_element in enumerate(pagination_elements):
                        execute_script_str = "document.querySelectorAll('div[class^=\"Pagination__pageNumber__\"]')[" + str(key) + "].click()"
                        print("execute_script_str: ", execute_script_str)
                        driver.execute_script(execute_script_str)
                        sleep(10)
                        selector_table_body = '[class^="ProductSupportRightArea__"] table tbody tr'
                        table_body_rows = driver.find_elements(By.CSS_SELECTOR, selector_table_body)
                        data_rows = []
                        for table_body_row in table_body_rows:
                            data_cells = {}
                            table_body_columns = table_body_row.find_elements(By.CSS_SELECTOR, 'td')
                            for i in range(len(table_body_columns)):
                                data_cells[table_header[i]] = table_body_columns[i].text

                            data_rows.append(data_cells)
                        
                        if MotherboardSupport.TYPE_CPU in sub_menu_element_text:
                            motherboard_supports += make_motherboard_support_from_data_rows(data_rows, MotherboardSupport.TYPE_CPU, motherboard_overview)
                        elif MotherboardSupport.TYPE_MEMORY in sub_menu_element_text:
                            motherboard_supports += make_motherboard_support_from_data_rows(data_rows, MotherboardSupport.TYPE_MEMORY, motherboard_overview)
                        elif MotherboardSupport.TYPE_DEVICE in sub_menu_element_text:
                            motherboard_supports += make_motherboard_support_from_data_rows(data_rows, MotherboardSupport.TYPE_DEVICE, motherboard_overview)
                else:
                    selector_table_body = '[class^="ProductSupportRightArea__"] table tbody tr'
                    table_body_rows = driver.find_elements(By.CSS_SELECTOR, selector_table_body)
                    data_rows = []
                    for table_body_row in table_body_rows:
                        data_cells = {}
                        table_body_columns = table_body_row.find_elements(By.CSS_SELECTOR, 'td')
                        for i in range(len(table_body_columns)):
                            data_cells[table_header[i]] = table_body_columns[i].text

                        data_rows.append(data_cells)
                    
                    if MotherboardSupport.TYPE_CPU in sub_menu_element_text:
                        motherboard_supports += make_motherboard_support_from_data_rows(data_rows, MotherboardSupport.TYPE_CPU, motherboard_overview)
                    elif MotherboardSupport.TYPE_MEMORY in sub_menu_element_text:
                        motherboard_supports += make_motherboard_support_from_data_rows(data_rows, MotherboardSupport.TYPE_MEMORY, motherboard_overview)
                    elif MotherboardSupport.TYPE_DEVICE in sub_menu_element_text:
                        motherboard_supports += make_motherboard_support_from_data_rows(data_rows, MotherboardSupport.TYPE_DEVICE, motherboard_overview)

        break
    driver.quit()
    return motherboard_supports

def make_motherboard_support_from_data_rows(data_rows, type, motherboard_overview):
    motherboard_supports = []
    for data_row in data_rows:
        motherboard_support = MotherboardSupport(
            id=None,
            mb_item_id=motherboard_overview.mb_item_id,
            type=type,
            data=json.dumps(data_row)
        )
        motherboard_supports.append(motherboard_support)
    return motherboard_supports
