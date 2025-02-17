import json
import traceback
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
import utils.utils

# const prefix for cache key
CACHE_PREFIX = "support_motherboard_item_"

sleep_time_random = random.randint(7, 10)

def start_parser_motherboard_support(mbir, mbor, mbtr, mbsr):
    # get all msi motherboard items from db
    motherboard_items = mbir.getAllMotherboardsByManufacturer(Manufacturer().MSI)
    motherboard_support_result = []
    it_was = False
    for motherboard_item in motherboard_items:
        motherboard_support_result_rows = []
        # if motherboard_item.id != 869:
        #     continue
        # it's for speed up parsing and testing and debugging and development only.
        # remove this line in production
        print("start_parser_motherboard_support motherboard_item.link: ", motherboard_item.link, " motherboard_item.id: ", motherboard_item.id)
        # if motherboard_item.link == "https://www.msi.com/Motherboard/PRO-Z890-A-WIFI":
        #     it_was = True
        # if not it_was:
        #     continue
        # remove this line in production
        if "TPM-20" in motherboard_item.link:
            continue
        if "H610TI-S01" in motherboard_item.link:
            continue
        if "H510TI-S01" in motherboard_item.link:
            continue
        if "H510TI-S03" in motherboard_item.link:
            continue
        if "H510TI-S05" in motherboard_item.link:
            continue
        key_motherboard_support = CACHE_PREFIX + str(motherboard_item.id)
        # check if cache exists
        json_cache = utils.cache.get_json_cache(key_motherboard_support)
        json_cache_is_valid = utils.cache.check_cache_size_is_valid(key_motherboard_support)
        if json_cache_is_valid is False:
            print("cache is not valid: ", key_motherboard_support)
        if json_cache is not None and json_cache_is_valid:
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
                print("motherboard_support is None")
                continue
            if len(motherboard_support) == 0:
                print("motherboard_support is empty")
                continue
            for motherboard_support_row in motherboard_support:
                motherboard_support_row.mb_item_id = motherboard_item.id
                motherboard_support_result.append(motherboard_support_row)
                motherboard_support_result_rows.append(motherboard_support_row)

            mbsr.add_motherboards_support(motherboard_support)
            # set json cache
        if len(motherboard_support_result) > 0:
            utils.cache.set_json_cache(key_motherboard_support, motherboard_support_result_rows)
        else:
            print("motherboard_support_result is empty")
            exit(0)

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
    for i in range(1):
        try:
            mb = parse_motherboard_support_page_from_api(motherboard_overview)
            if len(mb) > 0:
                break
        except Exception as e:
            print("start_parser_motherboard_support_page: exception", e)
            # print traceback
            traceback.print_exception(type(e), e, e.__traceback__)
            sleep(random.randint(1, 3))
    return mb

def parse_motherboard_support_page_from_api(motherboard_overview):
    motherboard_supports = []
    
    link = motherboard_overview.text
    #modifying the link to add some parameters for avoiding caching 
    # if "#" not in link:
    #     if "?" in link:
    #         link = link + "&_=" + str(random.randint(1, 1000000000))
    #     else:
    #         link = link + "?_=" + str(random.randint(1, 1000000000))
    driver = utils.swebdriver.create_driver_unvisible()
    driver.get(link)
    # define response code from driver
    response_code = driver.execute_script("return document.readyState")
    if response_code != "complete":
        print("response_code: ", response_code)
        driver.quit()
        return motherboard_supports
    menu_tab_index = 0
    menu_elements = driver.find_elements(By.CSS_SELECTOR, 'main#support .tabs button.tab')
    if menu_elements is None or len(menu_elements) == 0:
        driver.quit()
        return motherboard_supports
    compatibility_isnt_found = False
    for menu_element in menu_elements:
        if menu_element is None:
            continue
        menu_element_text = menu_element.get_attribute("textContent").lower().strip()
        print("menu_element text: ", menu_element.get_attribute("textContent"))
        # retrieve the content of the tab and check if it contains "cpu" or "Memory"
        if "compatibility" in menu_element_text.lower():
            compatibility_isnt_found = True
            execute_script_str = "document.querySelector('main#support .tabs button.tab:nth-child(" + str(menu_tab_index + 1) + ")').click()"
            print("execute_script_str: ", execute_script_str)
            driver.execute_script(execute_script_str)
            # menu_element.click()
            sleep(sleep_time_random)
            
            # get elements sub menu
            sub_menu_elements = driver.find_elements(By.CSS_SELECTOR, '#support .subTabs button')
            tab_index_sub_menu = 0
            sub_menu_element_texts = []
            for sub_menu_element in sub_menu_elements:
                if sub_menu_element.get_attribute("textContent").lower() == "":
                    continue
                sub_menu_element_text = sub_menu_element.get_attribute("textContent").lower().strip()
                sub_menu_element_texts.append(sub_menu_element_text)
                print("sub_menu_element_text: ", sub_menu_element_text)
                
                product_from_url = utils.utils.get_part_before_last_from_url(motherboard_overview.text)
                print("product_from_url: ", product_from_url) 
                template_url = "https://www.msi.com/api/v1/product/support/panel?product={}&type={}&page={}&per_page={}"

                if MotherboardSupport.TYPE_CPU in sub_menu_element_text:
                    url = template_url.format(product_from_url, MotherboardSupport.TYPE_CPU, 1, 10)
                    data_json = parse_motherboard_support_page_from_api_subpage_json(url)
                    is_valid = parse_motherboard_support_page_from_api_subpage_json_validate(data_json)
                    if is_valid is False:
                        print("is_valid 0 is False")
                        continue
                    is_valid = parse_motherboard_support_page_from_api_subpage_json_validate_cpu(data_json)
                    if is_valid is False:
                        print("is_valid 1 is False")
                        continue
                    total = data_json["result"]["downloads"]["cpu"]["total"]
                    per_page = data_json["result"]["downloads"]["cpu"]["per_page"]
                    total = int(total)
                    per_page = int(per_page)
                    print("total: ", total, " per_page: ", per_page)
                    data_rows = []
                    total_pages = total // per_page
                    total_pages += 1
                    # get all pages
                    for page in range(1, total_pages):
                        url = template_url.format(product_from_url, MotherboardSupport.TYPE_CPU, page, per_page)
                        data_json = parse_motherboard_support_page_from_api_subpage_json(url)
                        is_valid = parse_motherboard_support_page_from_api_subpage_json_validate(data_json)
                        if is_valid is False:
                            print("range is_valid 0 is False")
                            continue
                        is_valid = parse_motherboard_support_page_from_api_subpage_json_validate_cpu(data_json)
                        if is_valid is False:
                            print("range is_valid 1 is False")
                            continue
                        data_rows += data_json["result"]["downloads"]["cpu"]["list"]
                        if len(data_rows) >= total:
                            break
                        
                    motherboard_supports += make_motherboard_support_from_data_rows_pre(data_rows, sub_menu_element_text, motherboard_overview)
                    pass
                elif MotherboardSupport.TYPE_MEMORY in sub_menu_element_text:
                    url = template_url.format(product_from_url, "mem", 1, 10)
                    print("url: ", url)
                    data_json = parse_motherboard_support_page_from_api_subpage_json(url)
                    print("url finished", url)
                    is_valid = parse_motherboard_support_page_from_api_subpage_json_validate(data_json)
                    if is_valid is False:
                        print("is_valid 0 is False")
                        continue
                    is_valid = parse_motherboard_support_page_from_api_subpage_json_validate_memory(data_json)
                    if is_valid is False:
                        print("is_valid 1 is False")
                        continue
                    type_title = data_json["result"]["downloads"]["type_title"]
                    max_total = 0
                    sum_total = 0
                    per_page = 10
                    for type_title_item in type_title:
                        if type_title_item in data_json["result"]["downloads"]:
                            total = data_json["result"]["downloads"][type_title_item]["total"]
                            per_page = data_json["result"]["downloads"][type_title_item]["per_page"]
                            total = int(total)
                            per_page = int(per_page)
                            sum_total += total
                            if total > max_total:
                                max_total = total

                    total_pages = max_total // per_page
                    total_pages += 1
                    data_rows = []
                    # get all pages
                    for page in range(1, total_pages):
                        url = template_url.format(product_from_url, "mem", page, per_page)
                        data_json = parse_motherboard_support_page_from_api_subpage_json(url)
                        is_valid = parse_motherboard_support_page_from_api_subpage_json_validate(data_json)
                        if is_valid is False:
                            print("range is_valid 0 is False")
                            continue
                        is_valid = parse_motherboard_support_page_from_api_subpage_json_validate_memory(data_json)
                        if is_valid is False:
                            print("range is_valid 1 is False")
                            continue
                        type_title = data_json["result"]["downloads"]["type_title"]
                        for type_title_item in type_title:
                            if type_title_item in data_json["result"]["downloads"]:
                                if len(data_json["result"]["downloads"][type_title_item]["list"]) > 0:
                                    data_rows_tmp = data_json["result"]["downloads"][type_title_item]["list"]
                                    for data_row in data_rows_tmp:
                                        data_row["notice"] = type_title_item
                                    data_rows += data_rows_tmp
                        if len(data_rows) >= sum_total:
                            break

                    motherboard_supports += make_motherboard_support_from_data_rows_pre(data_rows, sub_menu_element_text, motherboard_overview)
                    pass
                elif MotherboardSupport.TYPE_VGA in sub_menu_element_text:
                    url = template_url.format(product_from_url, MotherboardSupport.TYPE_VGA, 1, 10)
                    data_json = parse_motherboard_support_page_from_api_subpage_json(url)
                    is_valid = parse_motherboard_support_page_from_api_subpage_json_validate(data_json)
                    if is_valid is False:
                        print("is_valid 0 is False")
                        continue
                    is_valid = parse_motherboard_support_page_from_api_subpage_json_validate_vga(data_json)
                    if is_valid is False:
                        print("is_valid 1 is False")
                        continue
                    total = data_json["result"]["downloads"]["vga"]["total"]
                    per_page = data_json["result"]["downloads"]["vga"]["per_page"]
                    total = int(total)
                    per_page = int(per_page)
                    print("total: ", total, " per_page: ", per_page)
                    data_rows = []
                    total_pages = total // per_page
                    total_pages += 1
                    # get all pages
                    for page in range(1, total_pages):
                        url = template_url.format(product_from_url, MotherboardSupport.TYPE_VGA, page, per_page)
                        data_json = parse_motherboard_support_page_from_api_subpage_json(url)
                        is_valid = parse_motherboard_support_page_from_api_subpage_json_validate(data_json)
                        if is_valid is False:
                            print("range is_valid 0 is False")
                            continue
                        is_valid = parse_motherboard_support_page_from_api_subpage_json_validate_vga(data_json)
                        if is_valid is False:
                            print("range is_valid 1 is False")
                            continue
                        data_rows += data_json["result"]["downloads"]["vga"]["list"]
                        if len(data_rows) >= total:
                            break
                        
                    motherboard_supports += make_motherboard_support_from_data_rows_pre(data_rows, sub_menu_element_text, motherboard_overview)
                elif MotherboardSupport.TYPE_STORAGE in sub_menu_element_text:
                    url = template_url.format(product_from_url, 'hdd', 1, 10)
                    data_json = parse_motherboard_support_page_from_api_subpage_json(url)
                    is_valid = parse_motherboard_support_page_from_api_subpage_json_validate(data_json)
                    if is_valid is False:
                        print("is_valid 0 is False")
                        continue
                    is_valid = parse_motherboard_support_page_from_api_subpage_json_validate_hdd(data_json)
                    if is_valid is False:
                        print("is_valid 1 is False")
                        continue
                    total = data_json["result"]["downloads"]["hdd"]["total"]
                    per_page = data_json["result"]["downloads"]["hdd"]["per_page"]
                    total = int(total)
                    per_page = int(per_page)
                    print("total: ", total, " per_page: ", per_page)
                    data_rows = []
                    total_pages = total // per_page
                    total_pages += 1
                    # get all pages
                    for page in range(1, total_pages):
                        url = template_url.format(product_from_url, 'hdd', page, per_page)
                        data_json = parse_motherboard_support_page_from_api_subpage_json(url)
                        data_rows += data_json["result"]["downloads"]["hdd"]["list"]
                        if len(data_rows) >= total:
                            break
                        
                    motherboard_supports += make_motherboard_support_from_data_rows_pre(data_rows, sub_menu_element_text, motherboard_overview)
                elif MotherboardSupport.TYPE_DEVICE in sub_menu_element_text:
                    url = template_url.format(product_from_url, 'testReport', 1, 10)
                    data_json = parse_motherboard_support_page_from_api_subpage_json(url)
                    is_valid = parse_motherboard_support_page_from_api_subpage_json_validate(data_json)
                    if is_valid is False:
                        print("is_valid 0 is False")
                        continue
                    is_valid = parse_motherboard_support_page_from_api_subpage_json_validate_device(data_json)
                    if is_valid is False:
                        print("is_valid 1 is False")
                        continue
                    total = data_json["result"]["downloads"]["testReport"]["total"]
                    per_page = data_json["result"]["downloads"]["testReport"]["per_page"]
                    total = int(total)
                    per_page = int(per_page)
                    print("total: ", total, " per_page: ", per_page)
                    data_rows = []
                    total_pages = total // per_page
                    total_pages += 1
                    # get all pages
                    for page in range(1, total_pages):
                        url = template_url.format(product_from_url, 'testReport', page, per_page)
                        data_json = parse_motherboard_support_page_from_api_subpage_json(url)
                        is_valid = parse_motherboard_support_page_from_api_subpage_json_validate(data_json)
                        if is_valid is False:
                            print("is_valid 0 is False")
                            continue
                        is_valid = parse_motherboard_support_page_from_api_subpage_json_validate_device(data_json)
                        if is_valid is False:
                            print("is_valid 1 is False")
                            continue
                        data_rows += data_json["result"]["downloads"]["testReport"]["list"]
                        if len(data_rows) >= total:
                            break
                        
                    motherboard_supports += make_motherboard_support_from_data_rows_pre(data_rows, sub_menu_element_text, motherboard_overview)

        menu_tab_index+=1

    driver.quit()
    if compatibility_isnt_found is False:
        print("compatibility isn't found")
    return motherboard_supports

def parse_motherboard_support_page_from_api_subpage_json_validate_device(data_json):
    if "testReport" not in data_json["result"]["downloads"]:
        print("testReport not in data_json or not in data_json")
        return False

    return True

def parse_motherboard_support_page_from_api_subpage_json_validate_hdd(data_json):
    if "hdd" not in data_json["result"]["downloads"]:
        print("hdd not in data_json or not in data_json")
        return False

    return True

def parse_motherboard_support_page_from_api_subpage_json_validate_vga(data_json):
    if "vga" not in data_json["result"]["downloads"]:
        print("vga not in data_json or not in data_json")
        return False
    
    return True

def parse_motherboard_support_page_from_api_subpage_json_validate_memory(data_json):
    if "type_title" not in data_json["result"]["downloads"]:
        print("type_title not in data_json or not in data_json")
        return False
    
    return True

def parse_motherboard_support_page_from_api_subpage_json_validate_cpu(data_json):
    # check exist data_json["result"]["downloads"]["cpu"]["list"]
    if "list" not in data_json["result"]["downloads"]["cpu"]:
        print("list not in data_json or not in data_json")
        return False
     # check exist data_json["result"]["downloads"]["cpu"]["total"]
    if "total" not in data_json["result"]["downloads"]["cpu"]:
        print("total not in data_json or not in data_json")
        return False
    
    return True

def parse_motherboard_support_page_from_api_subpage_json_validate(data_json):
    # check exist data_json["result"]["title"]
    if data_json is None or "result" not in data_json or "title" not in data_json["result"]:
        print("data_json is None or not in data_json or not in data_json")
        return False
    # check exist data_json["result"]["downloads"]["cpu"]["list"]
    if "downloads" not in data_json["result"]:
        print("downloads not in data_json")
        return False
    
    return True

def parse_motherboard_support_page_from_api_subpage_json(url):
    data_json = {}
    try:
        content = utils.download.download_file_by_selenium_unvisible(url)
        if content is None:
            return data_json
        data_json = utils.download.parse_json_from_content(content)
        if data_json is None:
            return data_json
    except Exception as e:
        print("parse_motherboard_support_page_from_api_subpage_json: exception", e)
        return data_json
    return data_json


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
    menu_elements = driver.find_elements(By.CSS_SELECTOR, 'main#support .tabs button.tab')
    for menu_element in menu_elements:
        menu_element_text = menu_element.get_attribute("textContent").lower().strip()
        print("menu_element text: ", menu_element.get_attribute("textContent"))
        # retrieve the content of the tab and check if it contains "cpu" or "Memory"
        if "compatibility" in menu_element_text.lower():
            execute_script_str = "document.querySelector('main#support .tabs button.tab:nth-child(" + str(menu_tab_index + 1) + ")').click()"
            print("execute_script_str: ", execute_script_str)
            driver.execute_script(execute_script_str)
            # menu_element.click()
            sleep(sleep_time_random)
            
            # get elements sub menu
            sub_menu_elements = driver.find_elements(By.CSS_SELECTOR, '#support .subTabs button')
            tab_index_sub_menu = 0
            sub_menu_element_texts = []
            for sub_menu_element in sub_menu_elements:
                if sub_menu_element.get_attribute("textContent").lower() == "":
                    continue
                sub_menu_element_text = sub_menu_element.get_attribute("textContent").lower().strip()
                sub_menu_element_texts.append(sub_menu_element_text)
                # click on sub menu element
                execute_script_str = "document.querySelectorAll('#support .subTabs button')[" + str(tab_index_sub_menu) + "].click()"
                tab_index_sub_menu += 1
                print("execute_script_str: ", execute_script_str)
                driver.execute_script(execute_script_str)
                sleep(sleep_time_random)
                
                # check if driver has badges buttons "#support .badges button" and avoid errors
                badges_elements = driver.find_elements(By.CSS_SELECTOR, '#support .badges button')
                if badges_elements and len(badges_elements) > 0:
                    data_rows = parse_motherboard_support_page_subpage_with_badges(driver, badges_elements)
                    motherboard_supports += make_motherboard_support_from_data_rows_pre(data_rows, sub_menu_element_text, motherboard_overview)
                else:
                    print("no badges elements")
                    data_rows = parse_motherboard_support_page_subpage(driver)
                    motherboard_supports += make_motherboard_support_from_data_rows_pre(data_rows, sub_menu_element_text, motherboard_overview)
                print("sub_menu_element_texts: ", sub_menu_element_texts)

        menu_tab_index += 1
    driver.quit()

    return motherboard_supports

def parse_motherboard_support_page_subpage(driver):
    selector_table_header = '#support .compatibility table thead th'
    table_header = get_motherboard_support_page_content_table_header(driver, selector_table_header)
    
    selector_table_body = '#support .compatibility table tbody tr'
    selector_pagination = '#support .pagination__link button'
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
            # 3 attempts to click on pagination element
            attempts_error = 0
            for i in range(3):
                try:
                    driver.execute_script(execute_script_str)
                    sleep(sleep_time_random)
                    break
                except Exception as e:
                    print("exception message in click on pagination element")
                    sleep(random.randint(1, 3))
                    attempts_error += 1
            print("attempts_error: ", attempts_error)
            if attempts_error == 3:
                print("error: 3 attempts to click on pagination element")
                break
            table_body_rows = driver.find_elements(By.CSS_SELECTOR, selector_table_body)
            data_rows = collect_data_rows(table_header, table_body_rows)
            if len(table_body_rows) < 10:
                break
    else:
        table_body_rows = driver.find_elements(By.CSS_SELECTOR, selector_table_body)
        data_rows = collect_data_rows(table_header, table_body_rows)
    return data_rows

def parse_motherboard_support_page_subpage_with_badges(driver, badges_elements):
    selector_table_header = '#support .compatibility table thead th'
    table_header = get_motherboard_support_page_content_table_header(driver, selector_table_header)

    data_rows = []
    badge_element_index = 0
    badge_element_selector = '#support .badges button'
    for badge_element in badges_elements:
        if badge_element is None:
            continue
        badge_element_text = badge_element.get_attribute("textContent").lower().strip()
        print("badge_element_text: ", badge_element_text)
        execute_script_str = "document.querySelectorAll('#support .badges button')[" + str(badge_element_index) + "].click()"
        print("execute_script_str: ", execute_script_str)
        driver.execute_script(execute_script_str)
        badge_element_index += 1
        sleep(sleep_time_random)
        selector_table_body = '#support .compatibility table tbody tr'
        selector_pagination = '#support .pagination__link button'
        pagination_elements = driver.find_elements(By.CSS_SELECTOR, selector_pagination)
        pagination_elements_len = len(pagination_elements)

        if pagination_elements_len > 0:
            for key, pagination_element in enumerate(pagination_elements):
                if key == 0:
                    continue
                if key == pagination_elements_len - 1:
                    continue
                execute_script_str = "document.querySelectorAll('" + selector_pagination + "')[" + str(key) + "].click()"
                print("execute_script_str: ", execute_script_str, " key: ", key, " pagination_elements_len: ", pagination_elements_len)
                # make screenshot
                # driver.save_screenshot("screenshot_" + str(key) + ".png")
                # # save driver's page source
                # with open("page_source_" + str(key) + ".html", "w") as file:
                #     file.write(driver.page_source)
                # 3 attempts to click on pagination element
                attempts_error = 0
                for i in range(3):
                    try:
                        driver.execute_script(execute_script_str)
                        sleep(sleep_time_random)
                        break
                    except Exception as e:
                        print("exception message in click on pagination element")
                        sleep(random.randint(1, 3))
                        attempts_error += 1
                print("attempts_error: ", attempts_error)
                if attempts_error == 3:
                    print("error: 3 attempts to click on pagination element")
                    break
                table_body_rows = driver.find_elements(By.CSS_SELECTOR, selector_table_body)
                data_rows += collect_data_rows(table_header, table_body_rows)
                if len(table_body_rows) < 10:
                    break
        else:
            table_body_rows = driver.find_elements(By.CSS_SELECTOR, selector_table_body)
            data_rows += collect_data_rows(table_header, table_body_rows)
        for data_row in data_rows:
            data_row["notice"] = badge_element_text

    return data_rows

def get_motherboard_support_page_content_table_header(driver, selector_table_header):
    table_header_elements = driver.find_elements(By.CSS_SELECTOR, selector_table_header)
    table_header = []
    for table_header_element in table_header_elements:
        # clean the text and trim it
        header_text = table_header_element.text.replace("\n", " ")
        header_text = header_text.strip()
        table_header.append(header_text)
    return table_header

def collect_data_rows(table_header, table_body_rows):
    data_rows = []
    for table_body_row in table_body_rows:
        data_cells = {}
        table_body_columns = table_body_row.find_elements(By.CSS_SELECTOR, 'td')
        if table_body_columns is None or len(table_body_columns) == 0:
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
