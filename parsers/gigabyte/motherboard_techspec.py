import random
import time
from bs4 import BeautifulSoup

from models.manufacturer import Manufacturer
from models.motherboard_overview import MotherboardOverview
from models.motherboard_techspec import MotherboardTechSpec
import utils
import utils.download

def start_parser_motherboard_techspec(mbir, mbor):
    # get all gigabyte motherboard items from db
    motherboard_items = mbir.getAllMotherboardsByManufacturer(Manufacturer().GIGABYTE)
    motherboard_techspecs_result = []
    it_was = False
    for motherboard_item in motherboard_items:
        print("start_parser_motherboard_page: ", motherboard_item.link, motherboard_item.id)
        # it's for speed up parsing and testing and debugging and development only.
        # remove this line in production
        # if motherboard_item.link == "https://www.gigabyte.com/Motherboard/B550I-AORUS-PRO-AX":
        #     it_was = True
        # if not it_was:
        #     continue
        # remove this line in production
        # start parse gigabyte motherboard page
        if "GC-TPM" in motherboard_item.link:
            continue
        if "-Bridge" in motherboard_item.link:
            continue
        if "MiniSAS" in motherboard_item.link:
            continue
        if "GP-TN90" in motherboard_item.link:
            continue
        if "GC-CI" in motherboard_item.link:
            continue
        
        # get motherboard_overview techspec link from db by mb_item_id
        motherboard_overviews = mbor.getOverviewsByMbItemIdType(motherboard_item.id, MotherboardOverview.TYPE_LINK_TECHNICAL_SPEC)
        if motherboard_overviews is None:
            print("Error: gigabyte motherboard techspec not found")
            continue
        motherboard_techspecs = []
        for motherboard_overview in motherboard_overviews:
            # start parse gigabyte motherboard techspec page
            motherboard_techspecs_rows = start_parser_motherboard_techspec_page(motherboard_overview)
            if motherboard_techspecs_rows is None:
                continue
            motherboard_techspecs += motherboard_techspecs_rows

        if motherboard_techspecs is None:
            print("Error: gigabyte motherboard techspec not found")
            exit(0)
        for motherboard_techspec in motherboard_techspecs:
            motherboard_techspec.mb_item_id = motherboard_item.id
            motherboard_techspecs_result.append(motherboard_techspec)

        

    return motherboard_techspecs_result

def start_parser_motherboard_techspec_page(motherboard_overview):
    if motherboard_overview.type != MotherboardOverview.TYPE_LINK_TECHNICAL_SPEC:
        print("start_parser_motherboard_techspec_page: not a technical spec link")
        return
    # if motherboard_overview.text doesn't have /spec/ in it, return
    if "/sp" not in motherboard_overview.text:
        print("start_parser_motherboard_techspec_page: not a technical spec link", motherboard_overview.text)
        return
    
    # get content from overview page like motherboard_overview.text
    content = utils.download.download_file_by_selenium_unvisible(motherboard_overview.text)
    if content is None:
        return

    # parse content from overview page find type link_overview, link_technical_spec, link_support
    return parse_motherboard_techspec_page(content, motherboard_overview)

def parse_motherboard_techspec_page(content, motherboard_overview):
    motherboard_techspecs = []
    
    motherboard_techspec = parse_motherboard_techspec_name(content, motherboard_overview)
    if motherboard_techspec is None:
        print("Error: gigabyte motherboard techspec name not found")
        exit(0)
    motherboard_techspecs.append(motherboard_techspec)
    
    motherboard_techspecs_rows = parse_motherboard_techspec_rows(content, motherboard_overview)
    # if motherboard_techspecs_rows length is 0, return
    if len(motherboard_techspecs_rows) == 0:
        print("Error: gigabyte motherboard techspec rows not found")
        print("motherboard_techspecs_rows: ", motherboard_techspecs_rows)
        exit(0)
    motherboard_techspecs += motherboard_techspecs_rows
    
    return motherboard_techspecs

def parse_motherboard_techspec_rows(content, motherboard_overview):
    soup = BeautifulSoup(content, 'html.parser')
    selectors = [
        '.sp-section .display-table-row',
        '.all-Products .owl-area .owl-item .specRow',
    ]
    motherboard_techspecs = []
    for index, selector in enumerate(selectors):
        items = soup.select(selector)
        if len(items) == 0:
            print("Error: gigabyte motherboard techspec rows not found (selector: %s)" % selector)
            # exit()
            continue
        if index == 0:
            return parse_motherboard_techspec_rows_1(items, motherboard_overview)
        elif index == 1:
            return parse_motherboard_techspec_rows_2(items, motherboard_overview)
        elif index == 2:
            return parse_motherboard_techspec_rows_3(items, motherboard_overview)
        
    return motherboard_techspecs

def parse_motherboard_techspec_rows_1(items, motherboard_overview):
    print("parse_motherboard_techspec_rows_2", motherboard_overview.text)
    motherboard_techspecs = []
    for item in items:
        mts = parse_motherboard_techspec_type_row_1(item, motherboard_overview)
        if mts is not None:
            motherboard_techspecs += mts
            continue

    # print("motherboard_techspecs: ", motherboard_techspecs)
    # exit(0)
    return motherboard_techspecs

def parse_motherboard_techspec_rows_2(items, motherboard_overview):
    print("parse_motherboard_techspec_rows_2")
    motherboard_techspecs = []
    for item in items:
        mts = parse_motherboard_techspec_type_row_2(item, motherboard_overview)
        if mts is not None:
            motherboard_techspecs += mts
            continue

    # print("motherboard_techspecs: ", motherboard_techspecs)
    # exit(0)
    return motherboard_techspecs

def parse_motherboard_techspec_rows_3(items, motherboard_overview):
    print("parse_motherboard_techspec_rows_3")
    motherboard_techspecs = []
    for item in items:
        mti = parse_motherboard_techspec_type_image_2(item, motherboard_overview)
        if mti is not None:
            motherboard_techspecs.append(mti)
            continue

        mts = parse_motherboard_techspec_type_row_3(item, motherboard_overview)
        if mts is not None:
            motherboard_techspecs += mts
            continue

    return motherboard_techspecs


# def parse_motherboard_techspec_rows_1(items, motherboard_overview):
#     motherboard_techspecs = []
#     for item in items:
#         name = item.select_one('th span')
#         if name is None:
#             print("Error: gigabyte motherboard techspec name not found")
#             continue
#         name = name.text
#         if "chipset" in name.lower():
#             value = item.select_one('td')
#             if value is None:
#                 continue
#             value = value.text
#             motherboard_techspec = MotherboardTechSpec(
#                 id=None,
#                 mb_item_id=motherboard_overview.mb_item_id,
#                 type=MotherboardTechSpec.TYPE_CHIPSET,
#                 text=value,
#                 updated_at=None
#             )
#             motherboard_techspecs.append(motherboard_techspec)
#         if "model" in name.lower():
#             value = item.select_one('td').text
#             motherboard_techspec = MotherboardTechSpec(
#                 id=None,
#                 mb_item_id=motherboard_overview.mb_item_id,
#                 type=MotherboardTechSpec.TYPE_MODEL,
#                 text=value,
#                 updated_at=None
#             )
#             motherboard_techspecs.append(motherboard_techspec)
#         elif "cpu" in name.lower():
#             value_html = item.select_one('td')
#             # value_html to string
#             value_html = str(value_html)
#             value_html = value_html.replace("<br/>", "|||||")
#             # value_html to html again
#             value_html = BeautifulSoup(value_html, 'html.parser')
#             values = value_html.text.split("|||||")
#             for value in values:
#                 motherboard_techspec = MotherboardTechSpec(
#                     id=None,
#                     mb_item_id=motherboard_overview.mb_item_id,
#                     type=MotherboardTechSpec.TYPE_CPU,
#                     text=value,
#                     updated_at=None
#                 )
#                 motherboard_techspecs.append(motherboard_techspec)
#         elif "memory" in name.lower():
#             value_html = item.select_one('td')
#             # value_html to string
#             value_html = str(value_html)
#             value_html = value_html.replace("<br/>", "|||||")
#             # value_html to html again
#             value_html = BeautifulSoup(value_html, 'html.parser')
#             values = value_html.text.split("|||||")
#             for value in values:
#                 motherboard_techspec = MotherboardTechSpec(
#                     id=None,
#                     mb_item_id=motherboard_overview.mb_item_id,
#                     type=MotherboardTechSpec.TYPE_MEMORY,
#                     text=value,
#                     updated_at=None
#                 )
#                 motherboard_techspecs.append(motherboard_techspec)
#         elif "graphics" in name.lower():
#             value_html = item.select_one('td')
#             # value_html to string
#             value_html = str(value_html)
#             value_html = value_html.replace("<br/>", "|||||")
#             # value_html to html again
#             value_html = BeautifulSoup(value_html, 'html.parser')
#             values = value_html.text.split("|||||")
#             for value in values:
#                 motherboard_techspec = MotherboardTechSpec(
#                     id=None,
#                     mb_item_id=motherboard_overview.mb_item_id,
#                     type=MotherboardTechSpec.TYPE_GRAPHICS,
#                     text=value,
#                     updated_at=None
#                 )
#                 motherboard_techspecs.append(motherboard_techspec)
#         elif "slot" in name.lower():
#             value_html = item.select_one('td')
#             # value_html to string
#             value_html = str(value_html)
#             value_html = value_html.replace("<br/>", "|||||")
#             # value_html to html again
#             value_html = BeautifulSoup(value_html, 'html.parser')
#             values = value_html.text.split("|||||")
#             for value in values:
#                 motherboard_techspec = MotherboardTechSpec(
#                     id=None,
#                     mb_item_id=motherboard_overview.mb_item_id,
#                     type=MotherboardTechSpec.TYPE_EXPANSION_SLOTS,
#                     text=value,
#                     updated_at=None
#                 )
#                 motherboard_techspecs.append(motherboard_techspec)
#         elif "storage" in name.lower():
#             value_html = item.select_one('td')
#             # value_html to string
#             value_html = str(value_html)
#             value_html = value_html.replace("<br/>", "|||||")
#             # value_html to html again
#             value_html = BeautifulSoup(value_html, 'html.parser')
#             values = value_html.text.split("|||||")
#             for value in values:
#                 motherboard_techspec = MotherboardTechSpec(
#                     id=None,
#                     mb_item_id=motherboard_overview.mb_item_id,
#                     type=MotherboardTechSpec.TYPE_STORAGE,
#                     text=value,
#                     updated_at=None
#                 )
#                 motherboard_techspecs.append(motherboard_techspec)
#         elif "lan" in name.lower():
#             value_html = item.select_one('td')
#             # value_html to string
#             value_html = str(value_html)
#             value_html = value_html.replace("<br/>", "|||||")
#             # value_html to html again
#             value_html = BeautifulSoup(value_html, 'html.parser')
#             values = value_html.text.split("|||||")
#             for value in values:
#                 motherboard_techspec = MotherboardTechSpec(
#                     id=None,
#                     mb_item_id=motherboard_overview.mb_item_id,
#                     type=MotherboardTechSpec.TYPE_LAN,
#                     text=value,
#                     updated_at=None
#                 )
#                 motherboard_techspecs.append(motherboard_techspec)
#         elif "usb" in name.lower():
#             value_html = item.select_one('td')
#             # value_html to string
#             value_html = str(value_html)
#             value_html = value_html.replace("<br/>", "|||||")
#             # value_html to html again
#             value_html = BeautifulSoup(value_html, 'html.parser')
#             values = value_html.text.split("|||||")
#             for value in values:
#                 motherboard_techspec = MotherboardTechSpec(
#                     id=None,
#                     mb_item_id=motherboard_overview.mb_item_id,
#                     type=MotherboardTechSpec.TYPE_USB,
#                     text=value,
#                     updated_at=None
#                 )
#                 motherboard_techspecs.append(motherboard_techspec)
#         elif "audio" in name.lower():
#             value_html = item.select_one('td')
#             # value_html to string
#             value_html = str(value_html)
#             value_html = value_html.replace("<br/>", "|||||")
#             # value_html to html again
#             value_html = BeautifulSoup(value_html, 'html.parser')
#             values = value_html.text.split("|||||")
#             for value in values:
#                 motherboard_techspec = MotherboardTechSpec(
#                     id=None,
#                     mb_item_id=motherboard_overview.mb_item_id,
#                     type=MotherboardTechSpec.TYPE_AUDIO,
#                     text=value,
#                     updated_at=None
#                 )
#                 motherboard_techspecs.append(motherboard_techspec)
#         elif "back panel" in name.lower():
#             value_html = item.select_one('td')
#             # # value_html to string
#             # value_html = str(value_html)
#             # value_html = value_html.replace("<br/>", "|||||")
#             # # value_html to html again
#             # value_html = BeautifulSoup(value_html, 'html.parser')
#             # values = value_html.text.split("|||||")
#             values = value_html.select('li')
#             for value in values:
#                 if value is None:
#                     continue
#                 motherboard_techspec = MotherboardTechSpec(
#                     id=None,
#                     mb_item_id=motherboard_overview.mb_item_id,
#                     type=MotherboardTechSpec.TYPE_BACK_PANEL_PORTS,
#                     text=value.text,
#                     updated_at=None
#                 )
#                 motherboard_techspecs.append(motherboard_techspec)
#         elif "internal" in name.lower():
#             value_html = item.select_one('td')
#             # value_html to string
#             value_html = str(value_html)
#             value_html = value_html.replace("<br/>", "|||||")
#             # value_html to html again
#             value_html = BeautifulSoup(value_html, 'html.parser')
#             values = value_html.text.split("|||||")
#             for value in values:
#                 motherboard_techspec = MotherboardTechSpec(
#                     id=None,
#                     mb_item_id=motherboard_overview.mb_item_id,
#                     type=MotherboardTechSpec.TYPE_INTERNAL_I_O_PORTS,
#                     text=value,
#                     updated_at=None
#                 )
#                 motherboard_techspecs.append(motherboard_techspec)
#         elif "feature" in name.lower():
#             value_html = item.select_one('td')
#             # value_html to string
#             value_html = str(value_html)
#             value_html = value_html.replace("<br/>", "|||||")
#             # value_html to html again
#             value_html = BeautifulSoup(value_html, 'html.parser')
#             values = value_html.text.split("|||||")
#             for value in values:
#                 motherboard_techspec = MotherboardTechSpec(
#                     id=None,
#                     mb_item_id=motherboard_overview.mb_item_id,
#                     type=MotherboardTechSpec.TYPE_SPECIAL_FEATURES,
#                     text=value,
#                     updated_at=None
#                 )
#                 motherboard_techspecs.append(motherboard_techspec)
#         elif "pcb" in name.lower():
#             value = item.select_one('td')
#             if value is None:
#                 continue
#             value = value.text
#             motherboard_techspec = MotherboardTechSpec(
#                 id=None,
#                 mb_item_id=motherboard_overview.mb_item_id,
#                 type=MotherboardTechSpec.TYPE_FORM_FACTOR,
#                 text=value,
#                 updated_at=None
#             )
#             motherboard_techspecs.append(motherboard_techspec)
#         elif "bios" in name.lower():
#             value = item.select_one('div.rowTableItemViewBox')
#             if value is None:
#                 continue
#             value = value.text
#             motherboard_techspec = MotherboardTechSpec(
#                 id=None,
#                 mb_item_id=motherboard_overview.mb_item_id,
#                 type=MotherboardTechSpec.TYPE_BIOS,
#                 text=value,
#                 updated_at=None
#             )
#             motherboard_techspecs.append(motherboard_techspec)
#         elif "operating system" in name.lower():
#             value = item.select_one('td')
#             if value is None:
#                 continue
#             value = value.text
#             motherboard_techspec = MotherboardTechSpec(
#                 id=None,
#                 mb_item_id=motherboard_overview.mb_item_id,
#                 type=MotherboardTechSpec.TYPE_OPERATING_SYSTEM,
#                 text=value,
#                 updated_at=None
#             )
#             motherboard_techspecs.append(motherboard_techspec)
#         elif "raid" in name.lower():
#             value = item.select_one('td')
#             if value is None:
#                 continue
#             value = value.text
#             motherboard_techspec = MotherboardTechSpec(
#                 id=None,
#                 mb_item_id=motherboard_overview.mb_item_id,
#                 type=MotherboardTechSpec.TYPE_OTHER,
#                 text=value,
#                 updated_at=None
#             )
#             motherboard_techspecs.append(motherboard_techspec)
#         elif "onboard thunderbolt" in name.lower():
#             value_html = item.select_one('td')
#             # value_html to string
#             value_html = str(value_html)
#             value_html = value_html.replace("<br/>", "|||||")
#             # value_html to html again
#             value_html = BeautifulSoup(value_html, 'html.parser')
#             values = value_html.text.split("|||||")
#             for value in values:
#                 motherboard_techspec = MotherboardTechSpec(
#                     id=None,
#                     mb_item_id=motherboard_overview.mb_item_id,
#                     type=MotherboardTechSpec.TYPE_OTHER,
#                     text=value,
#                     updated_at=None
#                 )
#                 motherboard_techspecs.append(motherboard_techspec)

#     return motherboard_techspecs

def parse_motherboard_techspec_name(content, motherboard_overview):
    selectors = [
        'h1.pageTitle',
    ]
    soup = BeautifulSoup(content, 'html.parser')
    for selector in selectors:            
        name = soup.select_one(selector)
        if name is None:
            print("Error: gigabyte motherboard techspec name not found (selector: %s)" % selector)
            # exit()
            continue
        name = name.text
        motherboard_techspec = MotherboardTechSpec(
            id=None,
            mb_item_id=motherboard_overview.mb_item_id,
            type=MotherboardTechSpec.TYPE_NAME,
            text=name,
            updated_at=None
        )
        return motherboard_techspec
    
    return None

def parse_motherboard_techspec_type_image_2(item, motherboard_overview):
    img = item.select_one('#product img.io')
    if img:
        motherboard_techspec = MotherboardTechSpec(
            id=None,
            mb_item_id=motherboard_overview.mb_item_id,
            type=MotherboardTechSpec.TYPE_IMAGE,
            text=img['src'],
            updated_at=None
        )
        return motherboard_techspec
    return None

def parse_motherboard_techspec_type_name_2(item, motherboard_overview):
    names = item.select_one('[class^="ProductSpecSingle__specProductName__"]')
    if names is None:
        print("Error: gigabyte motherboard techspec name not found")
        return None
    for name in names:
        # if name is None or empty or doesn't have text, skip
        if name is None or name.text == "" or not name.text:
            continue
        name = name.text
        # if name is empty, skip or ""
        if name == "":
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

def parse_motherboard_techspec_type_row_2(item, motherboard_overview):
    h2 = item.select_one('.specTitle')
    if h2 is None:
        return None
    h2 = h2.text

    general_selector = '.specDesc'
    if "processor" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_CPU, motherboard_overview.mb_item_id, item_elements)
    elif "chipset" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_CHIPSET, motherboard_overview.mb_item_id, item_elements)
    elif "memory" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_MEMORY, motherboard_overview.mb_item_id, item_elements)
    elif "graphics" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_GRAPHICS, motherboard_overview.mb_item_id, item_elements)
    elif "expansion slots" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_EXPANSION_SLOTS, motherboard_overview.mb_item_id, item_elements)
    elif "multi-gpu" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_OTHER, motherboard_overview.mb_item_id, item_elements)
    elif "storage" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_STORAGE, motherboard_overview.mb_item_id, item_elements)
    elif "sata" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_STORAGE, motherboard_overview.mb_item_id, item_elements)
    elif "ssd" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_STORAGE, motherboard_overview.mb_item_id, item_elements)
    elif "lan" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_LAN, motherboard_overview.mb_item_id, item_elements)
    elif "usb" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_USB, motherboard_overview.mb_item_id, item_elements)
    elif "audio" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_AUDIO, motherboard_overview.mb_item_id, item_elements)
    elif "back panel" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_BACK_PANEL_PORTS, motherboard_overview.mb_item_id, item_elements)
    elif "power connector" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_INTERNAL_I_O_PORTS, motherboard_overview.mb_item_id, item_elements)
    elif "fan connectors" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_INTERNAL_I_O_PORTS, motherboard_overview.mb_item_id, item_elements)
    elif "system connectors" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_INTERNAL_I_O_PORTS, motherboard_overview.mb_item_id, item_elements)
    elif "internal" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_INTERNAL_I_O_PORTS, motherboard_overview.mb_item_id, item_elements)
    elif "feature" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_SPECIAL_FEATURES, motherboard_overview.mb_item_id, item_elements)
    elif "bios" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_BIOS, motherboard_overview.mb_item_id, item_elements)
    elif "manageability" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_MANAGEABILITY, motherboard_overview.mb_item_id, item_elements)
    elif "accessories" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_ACCESSORIES, motherboard_overview.mb_item_id, item_elements)
    elif "jumpers" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_ACCESSORIES, motherboard_overview.mb_item_id, item_elements)
    elif "switches" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_ACCESSORIES, motherboard_overview.mb_item_id, item_elements)
    elif "operating system" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_OPERATING_SYSTEM, motherboard_overview.mb_item_id, item_elements)
    elif "form factor" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_FORM_FACTOR, motherboard_overview.mb_item_id, item_elements)
    elif "i/o controller" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_OTHER, motherboard_overview.mb_item_id, item_elements)
    elif "hardware monitor" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_OTHER, motherboard_overview.mb_item_id, item_elements)
    elif "raid" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_OTHER, motherboard_overview.mb_item_id, item_elements)
        

def parse_motherboard_techspec_type_row_2_value(type, mb_item_id, item_elements):
    motherboard_techspecs = []
    for item_element in item_elements:
        value_html = str(item_element)
        value_html = value_html.replace("<br/>", "|||||")
        value_html = value_html.replace("\n", "|||||")
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


def parse_motherboard_techspec_type_row_3(item, motherboard_overview):
    h2 = item.select_one('.TechSpec__title')
    if h2 is None:
        return None
    h2 = h2.text

    if "cpu" in h2.lower():
        value_html = item.select_one('.TechSpec__content')
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_CPU, motherboard_overview.mb_item_id, value_html)
    elif "chipset" in h2.lower():
        value_html = item.select_one('.TechSpec__content')
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_CHIPSET, motherboard_overview.mb_item_id, value_html)
    elif "memory" in h2.lower():
        value_html = item.select_one('.TechSpec__content')
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_MEMORY, motherboard_overview.mb_item_id, value_html)
    elif "graphics" in h2.lower():
        value_html = item.select_one('.TechSpec__content')
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_GRAPHICS, motherboard_overview.mb_item_id, value_html)
    elif "expansion slots" in h2.lower():
        value_html = item.select_one('.TechSpec__content')
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_EXPANSION_SLOTS, motherboard_overview.mb_item_id, value_html)
    elif "storage" in h2.lower():
        value_html = item.select_one('.TechSpec__content')
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_STORAGE, motherboard_overview.mb_item_id, value_html)
    elif "ethernet" in h2.lower():
        value_html = item.select_one('.TechSpec__content')
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_LAN, motherboard_overview.mb_item_id, value_html)
    elif "usb" in h2.lower():
        value_html = item.select_one('.TechSpec__content')
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_USB, motherboard_overview.mb_item_id, value_html)
    elif "audio" in h2.lower():
        value_html = item.select_one('.TechSpec__content')
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_AUDIO, motherboard_overview.mb_item_id, value_html)
    elif "back panel" in h2.lower():
        value_html = item.select_one('.TechSpec__content')
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_BACK_PANEL_PORTS, motherboard_overview.mb_item_id, value_html)
    elif "internal i/o" in h2.lower():
        value_html = item.select_one('.TechSpec__content')
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_INTERNAL_I_O_PORTS, motherboard_overview.mb_item_id, value_html)
    elif "special features" in h2.lower():
        value_html = item.select_one('.TechSpec__content')
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_SPECIAL_FEATURES, motherboard_overview.mb_item_id, value_html)
    elif "bios" in h2.lower():
        value = item.select_one('.TechSpec__content')
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_BIOS, motherboard_overview.mb_item_id, value)
    elif "manageability" in h2.lower():
        value = item.select_one('.TechSpec__content')
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_MANAGEABILITY, motherboard_overview.mb_item_id, value)
    elif "accessories" in h2.lower():
        value_html = item.select_one('.TechSpec__content')
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_ACCESSORIES, motherboard_overview.mb_item_id, value_html)
    elif "operating system" in h2.lower():
        value = item.select_one('.TechSpec__content')
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_OPERATING_SYSTEM, motherboard_overview.mb_item_id, value)
    elif "form factor" in h2.lower():
        value = item.select_one('.TechSpec__content')
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_FORM_FACTOR, motherboard_overview.mb_item_id, value)



def parse_motherboard_techspec_type_row_1(item, motherboard_overview):
    h2 = item.select_one('.display-table-cell.item .specText')
    if h2 is None:
        return None
    h2 = h2.text

    general_selector = '.display-table-cell .specDesc'
    if "processor" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_CPU, motherboard_overview.mb_item_id, item_elements)
    elif "chipset" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_CHIPSET, motherboard_overview.mb_item_id, item_elements)
    elif "memory" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_MEMORY, motherboard_overview.mb_item_id, item_elements)
    elif "graphics" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_GRAPHICS, motherboard_overview.mb_item_id, item_elements)
    elif "expansion slots" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_EXPANSION_SLOTS, motherboard_overview.mb_item_id, item_elements)
    elif "multi-gpu" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_OTHER, motherboard_overview.mb_item_id, item_elements)
    elif "storage" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_STORAGE, motherboard_overview.mb_item_id, item_elements)
    elif "sata" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_STORAGE, motherboard_overview.mb_item_id, item_elements)
    elif "ssd" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_STORAGE, motherboard_overview.mb_item_id, item_elements)
    elif "lan" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_LAN, motherboard_overview.mb_item_id, item_elements)
    elif "usb" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_USB, motherboard_overview.mb_item_id, item_elements)
    elif "audio" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_AUDIO, motherboard_overview.mb_item_id, item_elements)
    elif "back panel" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_BACK_PANEL_PORTS, motherboard_overview.mb_item_id, item_elements)
    elif "power connector" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_INTERNAL_I_O_PORTS, motherboard_overview.mb_item_id, item_elements)
    elif "fan connectors" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_INTERNAL_I_O_PORTS, motherboard_overview.mb_item_id, item_elements)
    elif "system connectors" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_INTERNAL_I_O_PORTS, motherboard_overview.mb_item_id, item_elements)
    elif "internal" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_INTERNAL_I_O_PORTS, motherboard_overview.mb_item_id, item_elements)
    elif "feature" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_SPECIAL_FEATURES, motherboard_overview.mb_item_id, item_elements)
    elif "bios" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_BIOS, motherboard_overview.mb_item_id, item_elements)
    elif "manageability" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_MANAGEABILITY, motherboard_overview.mb_item_id, item_elements)
    elif "accessories" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_ACCESSORIES, motherboard_overview.mb_item_id, item_elements)
    elif "jumpers" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_ACCESSORIES, motherboard_overview.mb_item_id, item_elements)
    elif "switches" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_ACCESSORIES, motherboard_overview.mb_item_id, item_elements)
    elif "operating system" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_OPERATING_SYSTEM, motherboard_overview.mb_item_id, item_elements)
    elif "form factor" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_FORM_FACTOR, motherboard_overview.mb_item_id, item_elements)
    elif "i/o controller" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_OTHER, motherboard_overview.mb_item_id, item_elements)
    elif "hardware monitor" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_OTHER, motherboard_overview.mb_item_id, item_elements)
    elif "raid" in h2.lower():
        item_elements = item.select(general_selector)
        return parse_motherboard_techspec_type_row_2_value(MotherboardTechSpec.TYPE_OTHER, motherboard_overview.mb_item_id, item_elements)
        