
# service to work with motherboards
import html
import re
from flask import json

import models


class MotherboardService:
    def __init__(self, motherboardItemRepository, motherboardOverviewRepository, motherboardTechSpecRepository, motherboardSupportRepository):
        self.motherboard_repository = motherboardItemRepository
        self.motherboard_overview_repository = motherboardOverviewRepository
        self.motherboard_techspec_repository = motherboardTechSpecRepository
        self.motherboard_support_repository = motherboardSupportRepository

    # get all motherboards
    def get_all_motherboards(self, limit=10, offset=0):
        result = {}
        result['data'] = {}
        motherboards = self.get_all_motherboards_item(limit, offset)
        motherboards_ids = self.get_ids_from_motherboards_item(motherboards)
        result['data']['motherboards_item'] = motherboards
        result['data']['motherboards_overview'] = self.get_all_motherboards_overview(motherboards_ids)
        result['data']['motherboards_techspec'] = self.get_all_motherboards_techspec_by_ids(motherboards_ids)
        result['data']['motherboards_support'] = self.get_all_motherboards_support_by_ids(motherboards_ids)

        return result

    def get_all_motherboards_item(self, limit=10, offset=0):
        motherboards = self.motherboard_repository.getAllMotherboardsList(limit, offset)
        for motherboard in motherboards:
            motherboard['title'] = self.clean_text(motherboard['title'])
            motherboard['description'] = self.clean_text(motherboard['description'])
        return motherboards
    
    def get_ids_from_motherboards_item(self, motherboards):
        ids = []
        for motherboard in motherboards:
            ids.append(motherboard['id'])
        return ids
    
    # get all motherboards overview
    def get_all_motherboards_overview(self, ids=None):
        if ids is not None:
            motherboards = self.motherboard_overview_repository.get_all_motherboards_overview_by_ids(ids)
        else:
            motherboards = self.motherboard_overview_repository.get_all_motherboards_overview()
        # motherboards to list and dict
        motherboards_list: list[models.MotherboardOverview] = []
        for motherboard in motherboards:
            motherboard_dict = motherboard.__dict__
            motherboards_list.append(motherboard_dict)
        return motherboards_list

    # get all motherboards techspec
    def get_all_motherboards_techspec(self):
        return self.motherboard_techspec_repository.get_all_motherboards_techspec()

    # get all motherboards techspec
    def get_all_motherboards_techspec_by_ids(self, ids):
        motherboards = self.motherboard_techspec_repository.get_all_motherboards_techspec_by_ids(ids)
        # motherboards to list and dict
        motherboards_list: list[models.MotherboardTechSpec] = []
        for motherboard in motherboards:
            motherboard_dict = motherboard.__dict__
            motherboard_dict['text'] = self.clean_text(motherboard_dict['text'])
            motherboards_list.append(motherboard_dict)
        return motherboards_list 

    # get all motherboards support
    def get_all_motherboards_support(self):
        return self.motherboard_support_repository.get_all_motherboards_support()
    
    # get all motherboards support
    def get_all_motherboards_support_by_ids(self, ids):
        motherboards = self.motherboard_support_repository.get_all_motherboards_support_by_ids(ids)
        # motherboards to list and dict
        motherboards_list: list[models.MotherboardSupport] = []
        for motherboard in motherboards:
            motherboard_dict = motherboard.__dict__
            motherboard_dict['data'] = json.loads(motherboard_dict['data'])
            motherboards_list.append(motherboard_dict)
        return motherboards_list

    # get all motherboards by manufacturer
    def get_all_motherboards_by_manufacturer(self, manufacturer):
        return self.motherboard_repository.get_all_motherboards_by_manufacturer(manufacturer)

    # get all motherboards overview by manufacturer
    def get_all_motherboards_overview_by_manufacturer(self, manufacturer):
        return self.motherboard_overview_repository.get_all_motherboards_overview_by_manufacturer(manufacturer)
    
    def clean_text(self, text):
        text = re.sub(r'<[^>]*?>', '', text)
        text = html.unescape(text)
        return text.replace('\n', '').replace('\r', '').replace('\t', '').strip()