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

# const prefix for cache key
CACHE_PREFIX = "support_motherboard_item_"

sleep_time_random = random.randint(5, 10)

def start_parser_motherboard_support(mbir, mbor, mbtr, mbsr):
    # get all biostar motherboard items from db
    motherboard_items = mbir.getAllMotherboardsByManufacturer(Manufacturer().BIOSTAR)
    motherboard_support_result = []
    it_was = False
    for motherboard_item in motherboard_items:
        # it's for speed up parsing and testing and debugging and development only.
        # remove this line in production
        print("start_parser_motherboard_support motherboard_item.link: ", motherboard_item.link, " motherboard_item.id: ", motherboard_item.id)
        # if motherboard_item.link == "https://www.biostar.com/Motherboard/PRO-Z890-A-WIFI":
        #     it_was = True
        # if not it_was:
        #     continue
        # remove this line in production
        if "S_ID=1039" in motherboard_item.link:
            continue
        if "S_ID=1017" in motherboard_item.link:
            continue
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

        motherboard_support_result_item = []
        for motherboard_overview in motherboard_overviews:
            # start parse biostar motherboard techspec page
            print("start_parser_motherboard_support: ", motherboard_overview.text)
            motherboard_support = start_parser_motherboard_support_page(motherboard_overview)
            if len(motherboard_support) == 0:
                print("start_parser_motherboard_support: no support data", motherboard_overview.text)
                exit(0)
            if motherboard_support is None:
                continue
            for motherboard_support_row in motherboard_support:
                motherboard_support_row.mb_item_id = motherboard_item.id
                motherboard_support_result.append(motherboard_support_row)
                motherboard_support_result_item.append(motherboard_support_row)

            # mbsr.add_motherboards_support(motherboard_support)
        # set json cache
        utils.cache.set_json_cache(key_motherboard_support, motherboard_support_result_item)

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
            traceback.print_exception(type(e), e, e.__traceback__)
            print("start_parser_motherboard_support_page: exception", e)
            exit(0)
            sleep(random.randint(1, 3))
    return mb

def parse_motherboard_support_page(motherboard_overview):
    motherboard_supports = []
    
    link = motherboard_overview.text
    
    content = utils.download.download_file_by_selenium_unvisible(link)
    if content is None:
        return
    
    # parse content by 
    if "mb_cpu" in link:
        motherboard_supports += parse_motherboard_support_page_content(content, MotherboardSupport.TYPE_CPU, motherboard_overview)
    if "mb_memory" in link:
        motherboard_supports += parse_motherboard_support_page_content(content, MotherboardSupport.TYPE_MEMORY, motherboard_overview)
    if "mb_storage" in link:
        motherboard_supports += parse_motherboard_support_page_content(content, MotherboardSupport.TYPE_STORAGE, motherboard_overview)
    if "mb_m2" in link:
        motherboard_supports += parse_motherboard_support_page_content(content, MotherboardSupport.TYPE_STORAGE, motherboard_overview)
    
    return motherboard_supports

def parse_motherboard_support_page_content(content, type, motherboard_overview):
    if type == MotherboardSupport.TYPE_CPU:
        selector_table_header = '.table-container table.table2excel thead tr'
        selector_table_body = '.table-container table.table2excel tbody tr'
        headers = get_motherboard_support_page_content_table_header(content, selector_table_header)
        if len(headers) == 0:
            return []
        table_body_rows = get_motherboard_support_page_content_table_body(content, selector_table_body)
        data_rows = collect_data_rows(headers, table_body_rows)
        return make_motherboard_support_from_data_rows_pre(data_rows, type, motherboard_overview)
    elif type == MotherboardSupport.TYPE_MEMORY:
        selector_table_header = '.table-container table.table2excel'
        selector_table_body = '.table-container table.table2excel tbody tr'
        headers = get_motherboard_support_page_content_table_header_memory(content, selector_table_header)
        if len(headers) == 0:
            return []
        table_body_rows = get_motherboard_support_page_content_table_body(content, selector_table_body)
        data_rows = collect_data_rows(headers, table_body_rows)
        return make_motherboard_support_from_data_rows_pre(data_rows, type, motherboard_overview)
    elif type == MotherboardSupport.TYPE_STORAGE:
        selector_table_header = '.table-container table.table2excel thead tr'
        selector_table_body = '.table-container table.table2excel tbody tr'
        headers = get_motherboard_support_page_content_table_header(content, selector_table_header)
        if len(headers) == 0:
            return []
        table_body_rows = get_motherboard_support_page_content_table_body(content, selector_table_body)
        data_rows = collect_data_rows(headers, table_body_rows)
        return make_motherboard_support_from_data_rows_pre(data_rows, type, motherboard_overview)
    
def get_motherboard_support_page_content_table_header_memory(content, selector_table_header):
    soup = BeautifulSoup(content, 'html.parser')
    table_header = soup.select(selector_table_header)
    if len(table_header) == 0:
        return []
    table_header = table_header[0].select('thead > tr > th')
    headers = []
    for header in table_header:
        if header is None:
            continue
        colspan = header.get('colspan')
        if colspan is not None:
            colspan = int(colspan)
        else:
            colspan = 1
            
        if colspan > 1:
            #  Find nested headers
            name_nested_header = header.select_one('table.inner-table tr:nth-of-type(1) th').text.replace("\n", " ").strip().lower()
            name_nested2_headers = header.select('table.inner-table tr:nth-of-type(2) td')
            for name_nested2_header in name_nested2_headers:
                header_text = name_nested_header + " " + name_nested2_header.text.replace("\n", " ").strip().lower()
                headers.append(header_text)
        else:
            header_text = header.text.replace("\n", " ").strip().lower()
            headers.append(header_text)

    return headers
            

def get_motherboard_support_page_content_table_header(content, selector_table_header):
    soup = BeautifulSoup(content, 'html.parser')
    table_header = soup.select(selector_table_header)
    if len(table_header) == 0:
        return []
    table_header = table_header[0].select('th')
    headers = []
    for header in table_header:
        if header is None:
            continue
        header_text = header.text.replace("\n", " ").strip().lower()
        headers.append(header_text)
    return headers

def get_motherboard_support_page_content_table_body(content, selector_table_body):
    soup = BeautifulSoup(content, 'html.parser')
    table_body = soup.select(selector_table_body)
    data_rows = []
    for table_body_row in table_body:
        data_cells = {}
        table_body_columns = table_body_row.select('td')
        for i in range(len(table_body_columns)):
            text_cell = table_body_columns[i].text.replace("\n", " ").strip()
            data_cells[i] = text_cell
        data_rows.append(data_cells)
    return data_rows

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
            print("table_header_len: ", table_header_len, " len(table_body_columns): ", len(table_body_columns))
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
        if table_header_len != len(table_body_row):
            continue
        for i in range(len(table_body_row)):
            if table_body_row[i] is None:
                continue
            data_cells[table_header[i]] = table_body_row[i]

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
