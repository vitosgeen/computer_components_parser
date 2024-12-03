
import sys

import parsers
import parsers.asrock
import parsers.asrock.motherboard_list
import parsers.asus
import parsers.asus.motherboard_list
import parsers.gigabyte
import parsers.gigabyte.motherboard_list
import parsers.msi
import parsers.msi.motherboard_list
import repository
import repository.motherboard_item_repository
import models.manufacturer


def start_parser(manufacture, db):
    # motherboard item repository 
    mbir = repository.motherboard_item_repository.MotherboardItemRepository(db)
    # start parser based on manufacture type with switch case
    if manufacture.lower() == models.manufacturer.Manufacturer().ASUS.lower():
        motherboards = parsers.asus.motherboard_list.start_parser_moterboard_list()
        # add to db
        for motherboard in motherboards:
            # check if motherboard exists in db by url
            motherboard_loaded = mbir.getByLink(motherboard.link)
            if motherboard_loaded is None:
                mbir.add(motherboard)

    elif manufacture.lower() == models.manufacturer.Manufacturer().MSI.lower():
        motherboards = parsers.msi.motherboard_list.start_parser_moterboard_list()
        # add to db
        for motherboard in motherboards:
            # check if motherboard exists in db by url
            motherboard_loaded = mbir.getByLink(motherboard.link)
            if motherboard_loaded is None:
                mbir.add(motherboard)

    elif manufacture.lower() == models.manufacturer.Manufacturer().GIGABYTE.lower():
        motherboards = parsers.gigabyte.motherboard_list.start_parser_moterboard_list()
        # add to db
        for motherboard in motherboards:
            # check if motherboard exists in db by url
            motherboard_loaded = mbir.getByLink(motherboard.link)
            if motherboard_loaded is None:
                mbir.add(motherboard)
    elif manufacture.lower() == models.manufacturer.Manufacturer().ASROCK.lower():
        motherboards = parsers.asrock.motherboard_list.start_parser_moterboard_list()
        # add to db
        for motherboard in motherboards:
            # check if motherboard exists in db by url
            motherboard_loaded = mbir.getByLink(motherboard.link)
            if motherboard_loaded is None:
                mbir.add(motherboard)

    else:
        print('Error: manufacture (' + manufacture + ') is not implemented')
        sys.exit(1)