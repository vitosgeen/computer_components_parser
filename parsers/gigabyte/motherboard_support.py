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

sleep_time_random = random.randint(5, 10)

def start_parser_motherboard_support(mbir, mbor, mbtr, mbsr):
    # get all gigabyte motherboard items from db
    motherboard_items = mbir.getAllMotherboardsByManufacturer(Manufacturer().GIGABYTE)
    motherboard_support_result = []
    it_was = False
    for motherboard_item in motherboard_items:
        # it's for speed up parsing and testing and debugging and development only.
        # remove this line in production
        print("start_parser_motherboard_support motherboard_item.link: ", motherboard_item.link, " motherboard_item.id: ", motherboard_item.id)
        # if motherboard_item.link == "https://www.gigabyte.com/Motherboard/PRO-Z890-A-WIFI":
        #     it_was = True
        # if not it_was:
        #     continue
        # remove this line in production
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
            # start parse gigabyte motherboard techspec page
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

    # parse content from support page
    print("start_parser_motherboard_support_page: is usual link", motherboard_overview.text)
    mb = []
    # make 3 attempts to parse the page
    for i in range(3):
        try:
            mb = parse_motherboard_support_page(motherboard_overview)
            if len(mb) > 0:
                break
        except Exception as e:
            print("start_parser_motherboard_support_page: exception", e)
            sleep(random.randint(1, 3))
    return mb

def parse_motherboard_support_page(motherboard_overview):
    motherboard_supports = []
    
    link = motherboard_overview.text
    driver = utils.swebdriver.create_driver_unvisible()
    driver.get(link)
    # define response code from driver
    response_code = driver.execute_script("return document.readyState")
    if response_code != "complete":
        print("response_code: ", response_code)
        driver.quit()
        return motherboard_supports
    menu_tab_index = 0
    
    product_id = driver.find_element(By.CSS_SELECTOR, '#isPid').get_attribute("value")
    if product_id == "" or product_id is None:
        driver.quit()
        return motherboard_supports
    menu_elements = driver.find_elements(By.CSS_SELECTOR, '.model-content ul.info-nav li')
    for menu_element in menu_elements:
        menu_element_text = menu_element.get_attribute("textContent").lower().strip()
        if menu_element_text.lower() == "":
            continue
        print("menu_element text: ", menu_element.get_attribute("textContent"))
        if "cpu" in menu_element_text.lower():
            execute_script_str = "document.querySelectorAll('.model-content ul.info-nav li')[" + str(menu_tab_index) + "].click()"
            print("execute_script_str: ", execute_script_str)
            driver.execute_script(execute_script_str)
            sleep(sleep_time_random)
            menu_tab_index += 1
            url_cpu = 'https://www.gigabyte.com/Ajax/SupportFunction/GetCpuList'
            html_content = utils.download.download_file(url_cpu, type='post', data_post={"Value": product_id, "Type":"Product"})
            if html_content is None:
                print("content is None")
                continue
            selector_table_body = 'div.main table tr'
            selector_table_header = 'div.main table tr'
            table_header = get_motherboard_support_page_content_table_header_bs_soup(html_content, selector_table_header)
            table_body_rows = get_motherboard_support_page_content_table_rows_bs_soup(html_content, selector_table_body)
            data_rows = collect_data_rows_bs_soup(table_header, table_body_rows, 'th')
            motherboard_supports += make_motherboard_support_from_data_rows_pre(data_rows, menu_element_text, motherboard_overview)
        elif "memory" in menu_element_text.lower():
            execute_script_str = "document.querySelectorAll('.model-content ul.info-nav li')[" + str(menu_tab_index) + "].click()"
            print("execute_script_str: ", execute_script_str)
            driver.execute_script(execute_script_str)
            sleep(sleep_time_random)
            menu_tab_index += 1
            url_memory = 'https://www.gigabyte.com/Ajax/SupportFunction/GetMemorySupportTable'
            html_content = utils.download.download_file(url_memory, type='post', data_post={"id": product_id})
            if html_content is None:
                print("content is None")
                continue
            selector_table_body = 'table.memory-support-table tbody tr'
            selector_table_header = 'table.memory-support-table thead tr'
            table_header = get_motherboard_support_page_content_table_header_bs_soup(html_content, selector_table_header)
            table_body_rows = get_motherboard_support_page_content_table_rows_bs_soup(html_content, selector_table_body)
            data_rows = collect_data_rows_bs_soup(table_header, table_body_rows, 'td')
            print("data_rows: ", data_rows)
            exit(0)
            motherboard_supports += make_motherboard_support_from_data_rows_pre(data_rows, menu_element_text, motherboard_overview)
        elif "storage" in menu_element_text.lower():
            execute_script_str = "document.querySelectorAll('.model-content ul.info-nav li')[" + str(menu_tab_index) + "].click()"
            print("execute_script_str: ", execute_script_str)
            driver.execute_script(execute_script_str)
            sleep(sleep_time_random)
            menu_tab_index += 1
            url_memory = 'https://www.gigabyte.com/Ajax/SupportFunction/GetStorageSupportTable'
            html_content = utils.download.download_file(url_memory, type='post', data_post={"id": product_id})
            if html_content is None:
                print("content is None")
                continue
            selector_table_body = 'table.storage-support-table-body tbody tr'
            selector_table_header = 'table.storage-support-table-body thead tr'
            table_header = get_motherboard_support_page_content_table_header_bs_soup(html_content, selector_table_header)
            table_body_rows = driver.find_elements(By.CSS_SELECTOR, selector_table_body)
            data_rows = collect_data_rows(table_header, table_body_rows)
            motherboard_supports += make_motherboard_support_from_data_rows_pre(data_rows, menu_element_text, motherboard_overview)
        menu_tab_index += 1
        # retrieve the content of the tab and check if it contains "cpu" or "Memory"
        # if "compatibility" in menu_element_text.lower():
        #     execute_script_str = "document.querySelector('main#support .tabs button.tab:nth-child(" + str(menu_tab_index + 1) + ")').click()"
        #     print("execute_script_str: ", execute_script_str)
        #     driver.execute_script(execute_script_str)
        #     # menu_element.click()
        #     sleep(sleep_time_random)
            
        #     # get elements sub menu
        #     sub_menu_elements = driver.find_elements(By.CSS_SELECTOR, '#support .subTabs button')
        #     tab_index_sub_menu = 0
        #     sub_menu_element_texts = []
        #     for sub_menu_element in sub_menu_elements:
        #         if sub_menu_element.get_attribute("textContent").lower() == "":
        #             continue
        #         sub_menu_element_text = sub_menu_element.get_attribute("textContent").lower().strip()
        #         sub_menu_element_texts.append(sub_menu_element_text)
        #         # click on sub menu element
        #         execute_script_str = "document.querySelectorAll('#support .subTabs button')[" + str(tab_index_sub_menu) + "].click()"
        #         tab_index_sub_menu += 1
        #         print("execute_script_str: ", execute_script_str)
        #         driver.execute_script(execute_script_str)
        #         sleep(sleep_time_random)
                
        #         # check if driver has badges buttons "#support .badges button" and avoid errors
        #         badges_elements = driver.find_elements(By.CSS_SELECTOR, '#support .badges button')
        #         if badges_elements and len(badges_elements) > 0:
        #             data_rows = parse_motherboard_support_page_subpage_with_badges(driver, badges_elements)
        #             motherboard_supports += make_motherboard_support_from_data_rows_pre(data_rows, sub_menu_element_text, motherboard_overview)
        #         else:
        #             print("no badges elements")
        #             data_rows = parse_motherboard_support_page_subpage(driver)
        #             motherboard_supports += make_motherboard_support_from_data_rows_pre(data_rows, sub_menu_element_text, motherboard_overview)
        #         print("sub_menu_element_texts: ", sub_menu_element_texts)
        
    driver.quit()

    return motherboard_supports

def parse_motherboard_support_page_subpage(driver):
    selector_table_header = '.info-content .main table tr'
    table_header = get_motherboard_support_page_content_table_header(driver, selector_table_header)
    
    selector_table_body = '.info-content .main table tr'
    selector_pagination = '.dataTables_paginate a'
    pagination_elements = driver.find_elements(By.CSS_SELECTOR, selector_pagination)
    pagination_elements_len = len(pagination_elements)

    data_rows = []
    if pagination_elements_len > 0:
        for key, pagination_element in enumerate(pagination_elements):
            if key == 0:
                continue
            if key == pagination_elements_len - 1:
                continue
            execute_script_str = "document.querySelectorAll('" + selector_pagination + "')[" + str(key) + "].click()"
            print("execute_script_str: ", execute_script_str)
            driver.execute_script(execute_script_str)
            sleep(sleep_time_random)
            table_body_rows = driver.find_elements(By.CSS_SELECTOR, selector_table_body)
            data_rows = collect_data_rows(table_header, table_body_rows)
    else:
        table_body_rows = driver.find_elements(By.CSS_SELECTOR, selector_table_body)
        data_rows = collect_data_rows(table_header, table_body_rows)
    return data_rows

def parse_motherboard_support_page_subpage_with_badges(driver, badges_elements):
    selector_table_header = '.info-content .main table tr'
    table_header = get_motherboard_support_page_content_table_header(driver, selector_table_header)

    data_rows = []
    badge_element_index = 0
    badge_element_selector = '.main > div:nth-child(1)'
    for badge_element in badges_elements:
        badge_element_text = badge_element.get_attribute("textContent").lower().strip()
        print("badge_element_text: ", badge_element_text)
        execute_script_str = "document.querySelectorAll('.main > div:nth-child(1)')[" + str(badge_element_index) + "].click()"
        print("execute_script_str: ", execute_script_str)
        driver.execute_script(execute_script_str)
        badge_element_index += 1
        sleep(sleep_time_random)
        selector_table_body = '.info-content .main table tr'
        selector_pagination = '.dataTables_paginate a'
        pagination_elements = driver.find_elements(By.CSS_SELECTOR, selector_pagination)
        pagination_elements_len = len(pagination_elements)

        if pagination_elements_len > 0:
            for key, pagination_element in enumerate(pagination_elements):
                if key == 0:
                    continue
                if key == pagination_elements_len - 1:
                    continue
                execute_script_str = "document.querySelectorAll('" + selector_pagination + "')[" + str(key) + "].click()"
                print("execute_script_str: ", execute_script_str)
                driver.execute_script(execute_script_str)
                sleep(sleep_time_random)
                table_body_rows = driver.find_elements(By.CSS_SELECTOR, selector_table_body)
                data_rows += collect_data_rows(table_header, table_body_rows)
        else:
            table_body_rows = driver.find_elements(By.CSS_SELECTOR, selector_table_body)
            data_rows += collect_data_rows(table_header, table_body_rows)
        for data_row in data_rows:
            data_row["notice"] = badge_element_text
    return data_rows
def get_motherboard_support_page_content_table_rows_bs_soup(html_content, selector_table_body):
    soup = BeautifulSoup(html_content, 'html.parser')
    table_rows = soup.select(selector_table_body)
    return table_rows

def get_motherboard_support_page_content_table_header_bs_soup(html_content, selector_table_header):
    soup = BeautifulSoup(html_content, 'html.parser')
    table_rows = soup.select(selector_table_header)
    column_max_len = 0
    for table_row in table_rows:
        table_columns = table_row.select('th')
        if len(table_columns) > column_max_len:
            column_max_len = len(table_columns)

    if column_max_len == 0:
        return []
    
    has_colspan = False
    for table_row in table_rows:
        table_columns = table_row.select('th')
        if len(table_columns) == column_max_len:
            table_header = []
            for table_column in table_columns:
                if table_column.has_attr('colspan') and int(table_column['colspan']) > 1:
                    has_colspan = True
                # clean the text and trim it
                header_text = table_column.text.replace("\n", " ")
                header_text = header_text.strip()
                table_header.append(header_text)
            return table_header
        
    return []

def get_motherboard_support_page_content_table_header(driver, selector_table_header):
    table_rows = driver.find_elements(By.CSS_SELECTOR, selector_table_header)
    column_max_len = 0
    for table_row in table_rows:
        table_columns = table_row.find_elements(By.CSS_SELECTOR, 'th')
        print("table_columns: ", table_columns)
        if len(table_columns) > column_max_len:
            column_max_len = len(table_columns)

    if column_max_len == 0:
        return []
    
    for table_row in table_rows:
        table_columns = table_row.find_elements(By.CSS_SELECTOR, 'th')
        print("table_columns: ", table_columns)
        if len(table_columns) == column_max_len:
            table_header = []
            for table_column in table_columns:
                # clean the text and trim it
                header_text = table_column.text.replace("\n", " ")
                header_text = header_text.strip()
                table_header.append(header_text)
            return table_header
        
    return []

def collect_data_rows_bs_soup(table_header, table_body_rows, cell_selector='th'):
    table_header_len = len(table_header)
    data_rows = []
    for table_body_row in table_body_rows:
        data_cells = {}
        table_body_columns = table_body_row.select(cell_selector)
        if cell_selector == 'td':
            print("table_header_len: ", table_header_len, " len(table_body_columns): ", len(table_body_columns))
            exit(0)
        if table_header_len != len(table_body_columns):
            continue
        for i in range(len(table_body_columns)):
            data_cells[table_header[i]] = table_body_columns[i].text.replace("\n", " ").strip()
        if cell_selector == 'td':
            print("data_cells: ", data_cells)
            exit(0)
        data_rows.append(data_cells)
    return data_rows

def collect_data_rows(table_header, table_body_rows):
    table_header_len = len(table_header)
    data_rows = []
    for table_body_row in table_body_rows:
        data_cells = {}
        table_body_columns = table_body_row.find_elements(By.CSS_SELECTOR, 'th')
        if table_header_len != len(table_body_columns):
            continue
        for i in range(len(table_body_columns)):
            data_cells[table_header[i]] = table_body_columns[i].text

        data_rows.append(data_cells)
    return data_rows

def make_motherboard_support_from_data_rows_pre(data_rows, type_row, motherboard_overview):
    motherboard_supports = []
    if MotherboardSupport.TYPE_CPU in type_row:
        motherboard_supports += make_motherboard_support_from_data_rows(data_rows, MotherboardSupport.TYPE_CPU, motherboard_overview)
    elif MotherboardSupport.TYPE_MEMORY in type_row:
        motherboard_supports += make_motherboard_support_from_data_rows(data_rows, MotherboardSupport.TYPE_MEMORY, motherboard_overview)
    elif MotherboardSupport.TYPE_DEVICE in type_row:
        motherboard_supports += make_motherboard_support_from_data_rows(data_rows, MotherboardSupport.TYPE_DEVICE, motherboard_overview)
    elif MotherboardSupport.TYPE_VGA in type_row:
        motherboard_supports += make_motherboard_support_from_data_rows(data_rows, MotherboardSupport.TYPE_VGA, motherboard_overview)
    elif MotherboardSupport.TYPE_STORAGE in type_row:
        motherboard_supports += make_motherboard_support_from_data_rows(data_rows, MotherboardSupport.TYPE_STORAGE, motherboard_overview)

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
