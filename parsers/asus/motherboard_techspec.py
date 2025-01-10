import random
from bs4 import BeautifulSoup

from models.manufacturer import Manufacturer
from models.motherboard_overview import MotherboardOverview
from models.motherboard_techspec import MotherboardTechSpec
import utils
import utils.download

def start_parser_motherboard_techspec(mbir, mbor):
    # get all asus motherboard items from db
    motherboard_items = mbir.getAllMotherboardsByManufacturer(Manufacturer().ASUS)
    motherboard_techspecs_result = []
    for motherboard_item in motherboard_items:
        # get motherboard_overview techspec link from db by mb_item_id
        motherboard_overviews = mbor.getOverviewsByMbItemIdType(motherboard_item.id, MotherboardOverview.TYPE_LINK_TECHNICAL_SPEC)
        if motherboard_overviews is None:
            continue

        for motherboard_overview in motherboard_overviews:
            # start parse asus motherboard techspec page
            motherboard_techspecs = start_parser_motherboard_techspec_page(motherboard_overview)
            if motherboard_techspecs is None:
                continue
            for motherboard_techspec in motherboard_techspecs:
                # motherboard_techspec.mb_item_id = motherboard_item.id
                # motherboard_techspecs_result.append(motherboard_techspec)

                print(motherboard_techspec.to_dict())

    return motherboard_techspecs_result

def start_parser_motherboard_techspec_page(motherboard_overview):
    if motherboard_overview.type != MotherboardOverview.TYPE_LINK_TECHNICAL_SPEC:
        print("start_parser_motherboard_techspec_page: not a technical spec link")
        return
    
    print("start_parser_motherboard_techspec_page: ", motherboard_overview.text)

    motherboard_techspecs = []

    # random int for sleep time
    sleep_delay = random.randint(1, 5)

    # get content from overview page like motherboard_overview.text
    content = utils.download.download_file(motherboard_overview.text, sleep_time=sleep_delay)
    if content is None:
        return

    # parse content from overview page find type link_overview, link_technical_spec, link_support
    motherboard_techspecs += parse_motherboard_techspec_page(content, motherboard_overview)

    return motherboard_techspecs

def parse_motherboard_techspec_page(content, motherboard_overview):
    motherboard_techspecs = []
    
    motherboard_techspec = parse_motherboard_techspec_name(content, motherboard_overview)
    motherboard_techspecs.append(motherboard_techspec)

    motherboard_techspecs_rows = parse_motherboard_techspec_rows(content, motherboard_overview)
    motherboard_techspecs += motherboard_techspecs_rows
    
    print(motherboard_techspecs)
    return motherboard_techspecs

def parse_motherboard_techspec_rows(content, motherboard_overview):
    soup = BeautifulSoup(content, 'html.parser')
    selectors = [
        '#productTableBody > div > div'
    ]
    for selector in selectors:
        items = soup.select(selector)
        if len(items) == 0:
            print("Error: asus motherboard techspec rows not found (selector: %s)" % selector)
            exit()
            continue
        motherboard_techspecs = []
        for item in items:
            img = item.select_one('img')
            if img:
                motherboard_techspec = MotherboardTechSpec(
                    id=None,
                    mb_item_id=motherboard_overview.mb_item_id,
                    type=MotherboardTechSpec.TYPE_IMAGE,
                    text=img['src'],
                    updated_at=None
                )
                motherboard_techspecs.append(motherboard_techspec)
            
            name = item.select_one('div.rowTableTitle')
            if name is None:
                print("Error: asus motherboard techspec name not found")
                continue
            name = name.text
            if "model" in name.lower():
                value = item.select_one('div.pdName').text
                motherboard_techspec = MotherboardTechSpec(
                    id=None,
                    mb_item_id=motherboard_overview.mb_item_id,
                    type=MotherboardTechSpec.TYPE_MODEL,
                    text=value,
                    updated_at=None
                )
                motherboard_techspecs.append(motherboard_techspec)
            elif "cpu" in name.lower():
                value_html = item.select_one('div.rowTableItemViewBox')
                # value_html to string
                value_html = str(value_html)
                value_html = value_html.replace("<br/>", "|||||")
                # value_html to html again
                value_html = BeautifulSoup(value_html, 'html.parser')
                values = value_html.text.split("|||||")
                for value in values:
                    motherboard_techspec = MotherboardTechSpec(
                        id=None,
                        mb_item_id=motherboard_overview.mb_item_id,
                        type=MotherboardTechSpec.TYPE_CPU,
                        text=value,
                        updated_at=None
                    )
                    motherboard_techspecs.append(motherboard_techspec)
            elif "memory" in name.lower():
                value_html = item.select_one('div.rowTableItemViewBox')
                # value_html to string
                value_html = str(value_html)
                value_html = value_html.replace("<br/>", "|||||")
                # value_html to html again
                value_html = BeautifulSoup(value_html, 'html.parser')
                values = value_html.text.split("|||||")
                for value in values:
                    motherboard_techspec = MotherboardTechSpec(
                        id=None,
                        mb_item_id=motherboard_overview.mb_item_id,
                        type=MotherboardTechSpec.TYPE_MEMORY,
                        text=value,
                        updated_at=None
                    )
                    motherboard_techspecs.append(motherboard_techspec)
            elif "graphics" in name.lower():
                value_html = item.select_one('div.rowTableItemViewBox')
                # value_html to string
                value_html = str(value_html)
                value_html = value_html.replace("<br/>", "|||||")
                # value_html to html again
                value_html = BeautifulSoup(value_html, 'html.parser')
                values = value_html.text.split("|||||")
                for value in values:
                    motherboard_techspec = MotherboardTechSpec(
                        id=None,
                        mb_item_id=motherboard_overview.mb_item_id,
                        type=MotherboardTechSpec.TYPE_GRAPHICS,
                        text=value,
                        updated_at=None
                    )
                    motherboard_techspecs.append(motherboard_techspec)
            elif "expansion slots" in name.lower():
                value_html = item.select_one('div.rowTableItemViewBox')
                # value_html to string
                value_html = str(value_html)
                value_html = value_html.replace("<br/>", "|||||")
                # value_html to html again
                value_html = BeautifulSoup(value_html, 'html.parser')
                values = value_html.text.split("|||||")
                for value in values:
                    motherboard_techspec = MotherboardTechSpec(
                        id=None,
                        mb_item_id=motherboard_overview.mb_item_id,
                        type=MotherboardTechSpec.TYPE_EXPANSION_SLOTS,
                        text=value,
                        updated_at=None
                    )
                    motherboard_techspecs.append(motherboard_techspec)
            elif "storage" in name.lower():
                value_html = item.select_one('div.rowTableItemViewBox')
                # value_html to string
                value_html = str(value_html)
                value_html = value_html.replace("<br/>", "|||||")
                # value_html to html again
                value_html = BeautifulSoup(value_html, 'html.parser')
                values = value_html.text.split("|||||")
                for value in values:
                    motherboard_techspec = MotherboardTechSpec(
                        id=None,
                        mb_item_id=motherboard_overview.mb_item_id,
                        type=MotherboardTechSpec.TYPE_STORAGE,
                        text=value,
                        updated_at=None
                    )
                    motherboard_techspecs.append(motherboard_techspec)
            elif "ethernet" in name.lower():
                value_html = item.select_one('div.rowTableItemViewBox')
                # value_html to string
                value_html = str(value_html)
                value_html = value_html.replace("<br/>", "|||||")
                # value_html to html again
                value_html = BeautifulSoup(value_html, 'html.parser')
                values = value_html.text.split("|||||")
                for value in values:
                    motherboard_techspec = MotherboardTechSpec(
                        id=None,
                        mb_item_id=motherboard_overview.mb_item_id,
                        type=MotherboardTechSpec.TYPE_LAN,
                        text=value,
                        updated_at=None
                    )
                    motherboard_techspecs.append(motherboard_techspec)
            elif "usb" in name.lower():
                value_html = item.select_one('div.rowTableItemViewBox')
                # value_html to string
                value_html = str(value_html)
                value_html = value_html.replace("<br/>", "|||||")
                # value_html to html again
                value_html = BeautifulSoup(value_html, 'html.parser')
                values = value_html.text.split("|||||")
                for value in values:
                    motherboard_techspec = MotherboardTechSpec(
                        id=None,
                        mb_item_id=motherboard_overview.mb_item_id,
                        type=MotherboardTechSpec.TYPE_USB,
                        text=value,
                        updated_at=None
                    )
                    motherboard_techspecs.append(motherboard_techspec)
            elif "audio" in name.lower():
                value_html = item.select_one('div.rowTableItemViewBox')
                # value_html to string
                value_html = str(value_html)
                value_html = value_html.replace("<br/>", "|||||")
                # value_html to html again
                value_html = BeautifulSoup(value_html, 'html.parser')
                values = value_html.text.split("|||||")
                for value in values:
                    motherboard_techspec = MotherboardTechSpec(
                        id=None,
                        mb_item_id=motherboard_overview.mb_item_id,
                        type=MotherboardTechSpec.TYPE_AUDIO,
                        text=value,
                        updated_at=None
                    )
                    motherboard_techspecs.append(motherboard_techspec)
            elif "back panel" in name.lower():
                value_html = item.select_one('div.rowTableItemViewBox')
                # value_html to string
                value_html = str(value_html)
                value_html = value_html.replace("<br/>", "|||||")
                # value_html to html again
                value_html = BeautifulSoup(value_html, 'html.parser')
                values = value_html.text.split("|||||")
                for value in values:
                    motherboard_techspec = MotherboardTechSpec(
                        id=None,
                        mb_item_id=motherboard_overview.mb_item_id,
                        type=MotherboardTechSpec.TYPE_BACK_PANEL_PORTS,
                        text=value,
                        updated_at=None
                    )
                    motherboard_techspecs.append(motherboard_techspec)
            elif "internal i/o" in name.lower():
                value_html = item.select_one('div.rowTableItemViewBox')
                # value_html to string
                value_html = str(value_html)
                value_html = value_html.replace("<br/>", "|||||")
                # value_html to html again
                value_html = BeautifulSoup(value_html, 'html.parser')
                values = value_html.text.split("|||||")
                for value in values:
                    motherboard_techspec = MotherboardTechSpec(
                        id=None,
                        mb_item_id=motherboard_overview.mb_item_id,
                        type=MotherboardTechSpec.TYPE_INTERNAL_I_O_PORTS,
                        text=value,
                        updated_at=None
                    )
                    motherboard_techspecs.append(motherboard_techspec)
            elif "special features" in name.lower():
                value_html = item.select_one('div.rowTableItemViewBox')
                # value_html to string
                value_html = str(value_html)
                value_html = value_html.replace("<br/>", "|||||")
                # value_html to html again
                value_html = BeautifulSoup(value_html, 'html.parser')
                values = value_html.text.split("|||||")
                for value in values:
                    motherboard_techspec = MotherboardTechSpec(
                        id=None,
                        mb_item_id=motherboard_overview.mb_item_id,
                        type=MotherboardTechSpec.TYPE_SPECIAL_FEATURES,
                        text=value,
                        updated_at=None
                    )
                    motherboard_techspecs.append(motherboard_techspec)
            elif "form factor" in name.lower():
                value = item.select_one('div.rowTableItemViewBox')
                if value is None:
                    continue
                value = value.text
                motherboard_techspec = MotherboardTechSpec(
                    id=None,
                    mb_item_id=motherboard_overview.mb_item_id,
                    type=MotherboardTechSpec.TYPE_FORM_FACTOR,
                    text=value,
                    updated_at=None
                )
                motherboard_techspecs.append(motherboard_techspec)
            elif "bios" in name.lower():
                value = item.select_one('div.rowTableItemViewBox')
                if value is None:
                    continue
                value = value.text
                motherboard_techspec = MotherboardTechSpec(
                    id=None,
                    mb_item_id=motherboard_overview.mb_item_id,
                    type=MotherboardTechSpec.TYPE_BIOS,
                    text=value,
                    updated_at=None
                )
                motherboard_techspecs.append(motherboard_techspec)
            elif "manageability" in name.lower():
                value = item.select_one('div.rowTableItemViewBox')
                if value is None:
                    continue
                value = value.text
                motherboard_techspec = MotherboardTechSpec(
                    id=None,
                    mb_item_id=motherboard_overview.mb_item_id,
                    type=MotherboardTechSpec.TYPE_MANAGEABILITY,
                    text=value,
                    updated_at=None
                )
                motherboard_techspecs.append(motherboard_techspec)
            elif "accessories" in name.lower():
                value_html = item.select_one('div.rowTableItemViewBox')
                # value_html to string
                value_html = str(value_html)
                value_html = value_html.replace("<br/>", "|||||")
                # value_html to html again
                value_html = BeautifulSoup(value_html, 'html.parser')
                values = value_html.text.split("|||||")
                for value in values:
                    motherboard_techspec = MotherboardTechSpec(
                        id=None,
                        mb_item_id=motherboard_overview.mb_item_id,
                        type=MotherboardTechSpec.TYPE_ACCESSORIES,
                        text=value,
                        updated_at=None
                    )
                    motherboard_techspecs.append(motherboard_techspec)

    return motherboard_techspecs
    

def parse_motherboard_techspec_name(content, motherboard_overview):
    selectors = [
        'h1[tabindex]'
    ]
    soup = BeautifulSoup(content, 'html.parser')
    for selector in selectors:            
        name = soup.select_one(selector).text
        if name is None:
            print("Error: asus motherboard techspec name not found (selector: %s)" % selector)
            exit()
            continue
        motherboard_techspec = MotherboardTechSpec(
            id=None,
            mb_item_id=motherboard_overview.mb_item_id,
            type=MotherboardTechSpec.TYPE_NAME,
            text=name,
            updated_at=None
        )
    return motherboard_techspec