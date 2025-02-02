import random
from time import sleep
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

from models.manufacturer import Manufacturer
from models.motherboard_overview import MotherboardOverview
from models.motherboard_techspec import MotherboardTechSpec
import utils
import utils.download

def start_parser_motherboard_techspec(mbir, mbor):
    # get all asrock motherboard items from db
    motherboard_items = mbir.getAllMotherboardsByManufacturer(Manufacturer().ASROCK)
    motherboard_techspecs_result = []
    it_was = False
    count = 0
    for motherboard_item in motherboard_items:
        # it's for speed up parsing and testing and debugging and development only.
        # remove this line in production
        # print("Iteration number: " + str(count))
        # print("Motherboard link: " + motherboard_item.link)
        # count += 1
        # if motherboard_item.link == "https://www.asrock.com/mb/Intel/Z690 Taichi Razer Edition/index.asp":
        #     it_was = True
        # if not it_was:
        #     continue
        # remove this line in production
        # start parse asrock motherboard page
        # get motherboard_overview techspec link from db by mb_item_id
        motherboard_overviews = mbor.getOverviewsByMbItemIdType(motherboard_item.id, MotherboardOverview.TYPE_LINK_TECHNICAL_SPEC)
        if motherboard_overviews is None:
            continue

        for motherboard_overview in motherboard_overviews:
            # start parse asrock motherboard techspec page
            motherboard_techspecs = start_parser_motherboard_techspec_page(motherboard_overview)
            if motherboard_techspecs is None:
                continue
            for motherboard_techspec in motherboard_techspecs:
                motherboard_techspec.mb_item_id = motherboard_item.id
                motherboard_techspecs_result.append(motherboard_techspec)

    return motherboard_techspecs_result

def start_parser_motherboard_techspec_page(motherboard_overview):
    if motherboard_overview.type != MotherboardOverview.TYPE_LINK_TECHNICAL_SPEC:
        print("start_parser_motherboard_techspec_page: not a technical spec link")
        return
    # if motherboard_overview.text doesn't have /spec/ in it, return
    motherboard_overview_text = motherboard_overview.text.lower()
    if "spec" not in motherboard_overview_text:
        print("start_parser_motherboard_techspec_page: not a technical spec link", motherboard_overview.text)
        return
    
    print("start_parser_motherboard_techspec_page: ", motherboard_overview.text)

    motherboard_techspecs = []

    # random int for sleep time
    sleep_delay = random.randint(5, 10)

    # get content from overview page like motherboard_overview.text
    # content = utils.download.download_file(motherboard_overview.text, sleep_time=sleep_delay)
    # if content is None:
    #     return
    
    # create swebdriver
    driver = utils.swebdriver.create_driver_unvisible()
    driver.get(motherboard_overview.text)
    # get content
    content = driver.page_source

    # wait for page to load
    sleep(sleep_delay)
    if content is None:
        return

    # parse content from overview page find type link_overview, link_technical_spec, link_support
    motherboard_techspecs += parse_motherboard_techspec_page(driver, motherboard_overview)
    if len(motherboard_techspecs) == 0 and "#Spec" not in motherboard_overview.text:
        # try to add #Specification
        print("try to add #Specification")
        motherboard_overview.text = motherboard_overview.text + "#Specification"
        # create swebdriver
        driver = utils.swebdriver.create_driver_unvisible()
        driver.get(motherboard_overview.text)
        # get content
        content = driver.page_source

        # wait for page to load
        sleep(sleep_delay)
        if content is None:
            return
        motherboard_techspecs += parse_motherboard_techspec_page(driver, motherboard_overview)
        
    if len(motherboard_techspecs) == 0:
        print("Error: asrock motherboard techspec not found")
        exit(0)
        return
    return motherboard_techspecs

def parse_motherboard_techspec_page(driver, motherboard_overview):
    motherboard_techspecs = []

    motherboard_techspecs_rows = parse_motherboard_techspec_rows(driver, motherboard_overview)
    motherboard_techspecs += motherboard_techspecs_rows

    return motherboard_techspecs

def parse_motherboard_techspec_rows(driver, motherboard_overview):
    selectors = [
        '.SpecForm li'
    ]
    motherboard_techspecs = []
    for selector in selectors:
        items = driver.find_elements(By.CSS_SELECTOR, selector)
        if items is None:
            continue
        if len(items) == 0:
            continue

        for item in items:
            if selector == '.SpecForm li':
                motherboard_techspecs_row = parse_motherboard_techspec_type_row_1(item, motherboard_overview)
                if len(motherboard_techspecs_row) > 0:
                    for mt in motherboard_techspecs_row:
                        print("motherboard_techspecs_row", mt.text)
                    motherboard_techspecs += motherboard_techspecs_row
        
    return motherboard_techspecs

# item element of <selenium.webdriver.remote.webelement.WebElement
def parse_motherboard_techspec_type_row_1(item, motherboard_overview):
    # find in item like select_one but for selenium - item.select_one('.SpecItem') - its not working
    labelSpec = item.find_element(By.CSS_SELECTOR, '.SpecItem')
    if labelSpec is None:
        return None
    labelSpec = labelSpec.text
    print("labelSpec: ", labelSpec)
    if "cpu" in labelSpec.lower():
        value_html = item.find_element(By.CSS_SELECTOR,'.SpecData')
        return parse_motherboard_techspec_type_row_1_value(MotherboardTechSpec.TYPE_CPU, motherboard_overview.mb_item_id, value_html)
    elif "chipset" in labelSpec.lower():
        value_html = item.find_element(By.CSS_SELECTOR,'.SpecData')
        return parse_motherboard_techspec_type_row_1_value(MotherboardTechSpec.TYPE_CHIPSET, motherboard_overview.mb_item_id, value_html)
    elif "memory" in labelSpec.lower():
        value_html = item.find_element(By.CSS_SELECTOR,'.SpecData')
        return parse_motherboard_techspec_type_row_1_value(MotherboardTechSpec.TYPE_MEMORY, motherboard_overview.mb_item_id, value_html)
    elif "graphic" in labelSpec.lower():
        value_html = item.find_element(By.CSS_SELECTOR,'.SpecData')
        return parse_motherboard_techspec_type_row_1_value(MotherboardTechSpec.TYPE_GRAPHICS, motherboard_overview.mb_item_id, value_html)
    elif "slots" in labelSpec.lower():
        value_html = item.find_element(By.CSS_SELECTOR,'.SpecData')
        return parse_motherboard_techspec_type_row_1_value(MotherboardTechSpec.TYPE_EXPANSION_SLOTS, motherboard_overview.mb_item_id, value_html)
    elif "storage" in labelSpec.lower():
        value_html = item.find_element(By.CSS_SELECTOR,'.SpecData')
        return parse_motherboard_techspec_type_row_1_value(MotherboardTechSpec.TYPE_STORAGE, motherboard_overview.mb_item_id, value_html)
    elif "lan" in labelSpec.lower():
        value_html = item.find_element(By.CSS_SELECTOR,'.SpecData')
        return parse_motherboard_techspec_type_row_1_value(MotherboardTechSpec.TYPE_LAN, motherboard_overview.mb_item_id, value_html)
    elif "usb" in labelSpec.lower():
        value_html = item.find_element(By.CSS_SELECTOR,'.SpecData')
        return parse_motherboard_techspec_type_row_1_value(MotherboardTechSpec.TYPE_USB, motherboard_overview.mb_item_id, value_html)
    elif "audio" in labelSpec.lower():
        value_html = item.find_element(By.CSS_SELECTOR,'.SpecData')
        return parse_motherboard_techspec_type_row_1_value(MotherboardTechSpec.TYPE_AUDIO, motherboard_overview.mb_item_id, value_html)
    elif "rear panel" in labelSpec.lower():
        value_html = item.find_element(By.CSS_SELECTOR,'.SpecData')
        return parse_motherboard_techspec_type_row_1_value(MotherboardTechSpec.TYPE_BACK_PANEL_PORTS, motherboard_overview.mb_item_id, value_html)
    elif "connector" in labelSpec.lower():
        value_html = item.find_element(By.CSS_SELECTOR,'.SpecData')
        return parse_motherboard_techspec_type_row_1_value(MotherboardTechSpec.TYPE_INTERNAL_I_O_PORTS, motherboard_overview.mb_item_id, value_html)
    elif "feature" in labelSpec.lower():
        value_html = item.find_element(By.CSS_SELECTOR,'.SpecData')
        return parse_motherboard_techspec_type_row_1_value(MotherboardTechSpec.TYPE_SPECIAL_FEATURES, motherboard_overview.mb_item_id, value_html)
    elif "bios" in labelSpec.lower():
        value = item.find_element(By.CSS_SELECTOR,'.SpecData')
        return parse_motherboard_techspec_type_row_1_value(MotherboardTechSpec.TYPE_BIOS, motherboard_overview.mb_item_id, value)
    elif "raid" in labelSpec.lower():
        value = item.find_element(By.CSS_SELECTOR,'.SpecData')
        return parse_motherboard_techspec_type_row_1_value(MotherboardTechSpec.TYPE_STORAGE, motherboard_overview.mb_item_id, value)
    elif "accessories" in labelSpec.lower():
        value_html = item.find_element(By.CSS_SELECTOR,'.SpecData')
        return parse_motherboard_techspec_type_row_1_value(MotherboardTechSpec.TYPE_ACCESSORIES, motherboard_overview.mb_item_id, value_html)
    elif "os" in labelSpec.lower():
        value = item.find_element(By.CSS_SELECTOR,'.SpecData')
        return parse_motherboard_techspec_type_row_1_value(MotherboardTechSpec.TYPE_OPERATING_SYSTEM, motherboard_overview.mb_item_id, value)
    elif "form factor" in labelSpec.lower():
        value = item.find_element(By.CSS_SELECTOR,'.SpecData')
        return parse_motherboard_techspec_type_row_1_value(MotherboardTechSpec.TYPE_FORM_FACTOR, motherboard_overview.mb_item_id, value)
    elif "software" in labelSpec.lower():
        value = item.find_element(By.CSS_SELECTOR,'.SpecData')
        return parse_motherboard_techspec_type_row_1_value(MotherboardTechSpec.TYPE_SOFTWARE, motherboard_overview.mb_item_id, value)
    elif "certifications" in labelSpec.lower():
        value = item.find_element(By.CSS_SELECTOR,'.SpecData')
        return parse_motherboard_techspec_type_row_1_value(MotherboardTechSpec.TYPE_OTHER, motherboard_overview.mb_item_id, value)
    elif "support cd" in labelSpec.lower():
        value = item.find_element(By.CSS_SELECTOR,'.SpecData')
        return parse_motherboard_techspec_type_row_1_value(MotherboardTechSpec.TYPE_OTHER, motherboard_overview.mb_item_id, value)
    elif "hardware monitor" in labelSpec.lower():
        value = item.find_element(By.CSS_SELECTOR,'.SpecData')
        return parse_motherboard_techspec_type_row_1_value(MotherboardTechSpec.TYPE_OTHER, motherboard_overview.mb_item_id, value)
    elif "gaming armor" in labelSpec.lower():
        value = item.find_element(By.CSS_SELECTOR,'.SpecData')
        return parse_motherboard_techspec_type_row_1_value(MotherboardTechSpec.TYPE_OTHER, motherboard_overview.mb_item_id, value)
    return []

def parse_motherboard_techspec_type_row_1_value(type, mb_item_id, value_html):
    value_html = value_html.get_attribute('outerHTML')
    motherboard_techspecs = []
    if value_html is None:
        return None
    value_html = str(value_html)
    value_html = value_html.replace("<br/>", "|||||")
    value_html = value_html.replace("<br>", "|||||")
    value_html = BeautifulSoup(value_html, 'html.parser')
    values = value_html.text.split("|||||")
    for value in values:
        motherboard_techspec = MotherboardTechSpec(
            id=None,
            mb_item_id=mb_item_id,
            type=type,
            text=value,
            updated_at=None
        )
        motherboard_techspecs.append(motherboard_techspec)
    return motherboard_techspecs

def parse_motherboard_techspec_name(driver, motherboard_overview):
    selectors = [
        '.hero_mdinfo .hero_name',
    ]
    for selector in selectors:
        name = driver.find_element(By.CSS_SELECTOR, selector)
        if name is None:
            continue
        name = name.text
        if name is None or name == "":
            continue
        motherboard_techspec = MotherboardTechSpec(
            id=None,
            mb_item_id=motherboard_overview.mb_item_id,
            type=MotherboardTechSpec.TYPE_MODEL,
            text=name,
            updated_at=None
        )
        return motherboard_techspec
    return None
