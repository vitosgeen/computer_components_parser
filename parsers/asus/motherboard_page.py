from models.manufacturer import Manufacturer

def start_parser_motherboard_pages(mbir):
    # get all asus motherboard items from db
    motherboards = mbir.getAllMotherboardsByManufacturer(Manufacturer().ASUS)
    for motherboard in motherboards:
        pass