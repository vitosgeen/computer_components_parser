
import sys

import models.motherboard_overview
import parsers
import parsers.asrock
import parsers.asrock.motherboard_list
import parsers.asus
import parsers.asus.motherboard_list
import parsers.asus.motherboard_page
import parsers.asus.motherboard_techspec
import parsers.biostar
import parsers.biostar.motherboard_list
import parsers.colorful
import parsers.colorful.motherboard_list
import parsers.evga
import parsers.evga.motherboard_list
import parsers.galax
import parsers.galax.motherboard_list
import parsers.gigabyte
import parsers.gigabyte.motherboard_list
import parsers.msi
import parsers.msi.motherboard_list
import repository
import repository.motherboard_item_repository
import models.manufacturer
import repository.motherboard_overview_repository
import repository.motherboard_techspec_repository


def start_parser(manufacture, db):
    # motherboard item repository 
    mbir = repository.motherboard_item_repository.MotherboardItemRepository(db)
    # motherboard overview repository
    mbor = repository.motherboard_overview_repository.MotherboardOverviewRepository(db)
    # motherboard techspec repository
    mbtr = repository.motherboard_techspec_repository.MotherboardTechSpecRepository(db)
    # start parser based on manufacture type with switch case
    if manufacture.lower() == models.manufacturer.Manufacturer().ASUS.lower():
        # motherboards = parsers.asus.motherboard_list.start_parser_moterboard_list()
        # add_motherboards(motherboards, mbir)
        # motherboards_overviews = parsers.asus.motherboard_page.start_parser_motherboard_pages(mbir)
        # add_motherboards_overviews(motherboards_overviews, mbor)
        motherboards_techspecs = parsers.asus.motherboard_techspec.start_parser_motherboard_techspec(mbir, mbor)

        # motherboards_overviews_techspec_links = get_motherboard_overviews_by_type(mbor, manufacture.lower(), models.motherboard_overview.MotherboardOverview.TYPE_LINK_TECHNICAL_SPEC)
        # motherboards_techspecs = parsers.asus.motherboard_techspec.start_parser_motherboard_techspec(mbir, mbor)
        # add_motherboards_techspecs(motherboards_techspecs, mbtr)



    elif manufacture.lower() == models.manufacturer.Manufacturer().MSI.lower():
        motherboards = parsers.msi.motherboard_list.start_parser_moterboard_list()
        add_motherboards(motherboards, mbir)

    elif manufacture.lower() == models.manufacturer.Manufacturer().GIGABYTE.lower():
        motherboards = parsers.gigabyte.motherboard_list.start_parser_moterboard_list()
        add_motherboards(motherboards, mbir)
    elif manufacture.lower() == models.manufacturer.Manufacturer().ASROCK.lower():
        motherboards = parsers.asrock.motherboard_list.start_parser_moterboard_list()
        add_motherboards(motherboards, mbir)
    elif manufacture.lower() == models.manufacturer.Manufacturer().BIOSTAR.lower():
        motherboards = parsers.biostar.motherboard_list.start_parser_moterboard_list()
        add_motherboards(motherboards, mbir)
    elif manufacture.lower() == models.manufacturer.Manufacturer().COLORFUL.lower():
        motherboards = parsers.colorful.motherboard_list.start_parser_moterboard_list()
        add_motherboards(motherboards, mbir)
    elif manufacture.lower() == models.manufacturer.Manufacturer().EVGA.lower():
        motherboards = parsers.evga.motherboard_list.start_parser_moterboard_list()
        add_motherboards(motherboards, mbir)
    elif manufacture.lower() == models.manufacturer.Manufacturer().GALAX.lower():
        motherboards = parsers.galax.motherboard_list.start_parser_moterboard_list()
        add_motherboards(motherboards, mbir)

    else:
        print('Error: manufacture (' + manufacture + ') is not implemented')
        sys.exit(1)


def add_motherboards(motherboards, mbir):
    for motherboard in motherboards:
        # check if motherboard exists in db by url
        motherboard_loaded = mbir.getByLink(motherboard.link)
        if motherboard_loaded is None:
            mbir.add(motherboard)

def add_motherboards_overviews(motherboards_overviews, mbor):
    for motherboard_overview in motherboards_overviews:
        # check if motherboard overview exists in db by mb_item_id and type
        motherboard_overview_loaded = mbor.getOverviewsByMbItemIdTypeText(motherboard_overview.mb_item_id, motherboard_overview.type, motherboard_overview.text)
        if motherboard_overview_loaded is None:
            mbor.add(motherboard_overview)

def add_motherboards_techspecs(motherboards_techspecs, mbtr):
    for motherboard_techspec in motherboards_techspecs:
        # check if motherboard techspec exists in db by mb_item_id and type
        motherboard_techspec_loaded = mbtr.getTechSpecsByMbItemIdTypeText(motherboard_techspec.mb_item_id, motherboard_techspec.type, motherboard_techspec.text)
        if motherboard_techspec_loaded is None:
            mbtr.add(motherboard_techspec)

def get_motherboard_overviews_by_type(mbor, manufacture, type):
    return mbor.getAllByType(type, manufacture)

def motherboards_list_by_manufacture(mbir, manufacture):
    return mbir.getAllMotherboardsByManufacturer(manufacture)