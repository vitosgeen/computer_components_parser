

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

