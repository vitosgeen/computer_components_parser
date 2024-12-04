from models.manufacturer import Manufacturer

def start_parser_motherboard_pages(mbir):
    # get all asus motherboard items from db
    motherboards = mbir.get_all_motherboards_by_manufacturer(Manufacturer().ASUS.lower())
    for motherboard in motherboards:
        print(motherboard.link)
        exit()
        # parse motherboard page
        # download content
        # parse content
        # update motherboard item
        # save to db