

import sys

from flask import Flask

import args
from databases import sqlite3
import databases.sqlite3
import parser
import databases
import repository
import repository.motherboard_item_repository
import models.manufacturer
import repository.motherboard_overview_repository
import repository.motherboard_support_repository
import repository.motherboard_techspec_repository
import api.routes.motherboard_routes
import api.services
import api.services.motherboard_service
import api.routes


def api_mode(db):
    pass
    # init repositories
    # motherboard item repository 
    # mbir = repository.motherboard_item_repository.MotherboardItemRepository(db)
    # # motherboard overview repository
    # mbor = repository.motherboard_overview_repository.MotherboardOverviewRepository(db)
    # # motherboard techspec repository
    # mbtr = repository.motherboard_techspec_repository.MotherboardTechSpecRepository(db)
    # # motherboard support repository
    # mbsr = repository.motherboard_support_repository.MotherboardSupportRepository(db)

    # # init services
    # motherboard_service = api.services.motherboard_service.MotherboardService(mbir, mbor, mbtr, mbsr)

    # app = Flask(__name__)

    # # init routes
    # router = api.routes.motherboard_routes.MotherboardRoutes(app, motherboard_service)

    # router.app.run(debug=True)

def cli_mode(db):
    # get manufature from args
    manufacture = args.get_arg()
    if manufacture is None:
        print('Error: manufacture (' + args.ARG_MANUFACTURE + ') is required')
        sys.exit(1)

    # validate manufacture
    is_valid = args.validate_manufacture(manufacture)
    if not is_valid:
        print('Error: manufacture (' + manufacture + ') is not valid')
        sys.exit(1)

    parser.parse_manufacture(manufacture, db)

if __name__ == '__main__':
    # init sqlite3 
    db = databases.sqlite3.SQLite3()
    db.install()
    
    if len(sys.argv) > 1:
        cli_mode(db)
    else:
        api_mode(db)

