# controller for the motherboard routes
class MotherboardController:
    def __init__(self, motherboard_service):
        self.motherboard_service = motherboard_service

    # get all motherboards
    def get_all_motherboards(self, limit=10, offset=0):
        motherboards = self.motherboard_service.get_all_motherboards(limit, offset)
        return motherboards

    # get all motherboards overview
    def get_all_motherboards_overview(self):
        return self.motherboard_service.get_all_motherboards_overview()

    # get all motherboards techspec
    def get_all_motherboards_techspec(self):
        return self.motherboard_service.get_all_motherboards_techspec()

    # get all motherboards support
    def get_all_motherboards_support(self):
        return self.motherboard_service.get_all_motherboards_support()

    # get all motherboards by manufacturer
    def get_all_motherboards_by_manufacturer(self, manufacturer):
        return self.motherboard_service.get_all_motherboards_by_manufacturer(manufacturer)