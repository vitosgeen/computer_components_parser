
# service to work with motherboards
class MotherboardService:
    def __init__(self, motherboardItemRepository, motherboardOverviewRepository, motherboardTechSpecRepository, motherboardSupportRepository):
        self.motherboard_repository = motherboardItemRepository
        self.motherboard_overview_repository = motherboardOverviewRepository
        self.motherboard_techspec_repository = motherboardTechSpecRepository
        self.motherboard_support_repository = motherboardSupportRepository

    # get all motherboards
    def get_all_motherboards(self):
        return self.motherboard_repository.get_all_motherboards()

    # get all motherboards overview
    def get_all_motherboards_overview(self):
        return self.motherboard_overview_repository.get_all_motherboards_overview()

    # get all motherboards techspec
    def get_all_motherboards_techspec(self):
        return self.motherboard_techspec_repository.get_all_motherboards_techspec()

    # get all motherboards support
    def get_all_motherboards_support(self):
        return self.motherboard_support_repository.get_all_motherboards_support()

    # get all motherboards by manufacturer
    def get_all_motherboards_by_manufacturer(self, manufacturer):
        return self.motherboard_repository.get_all_motherboards_by_manufacturer(manufacturer)

    # get all motherboards overview by manufacturer
    def get_all_motherboards_overview_by_manufacturer(self, manufacturer):
        return self.motherboard_overview_repository.get_all_motherboards_overview_by_manufacturer(manufacturer)