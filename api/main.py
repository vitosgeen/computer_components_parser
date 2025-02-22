import sys
import os
from flask import Flask

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# import databases
import databases.sqlite3
import repository
import repository.motherboard_item_repository
import models.manufacturer
import repository.motherboard_overview_repository
import repository.motherboard_support_repository
import repository.motherboard_techspec_repository
import routes.motherboard_routes
import services
import services.motherboard_service
import routes

if __name__ == '__main__':

    # init sqlite3
    db = databases.sqlite3.SQLite3()

    # init repositories
    # motherboard item repository 
    mbir = repository.motherboard_item_repository.MotherboardItemRepository(db)
    # motherboard overview repository
    mbor = repository.motherboard_overview_repository.MotherboardOverviewRepository(db)
    # motherboard techspec repository
    mbtr = repository.motherboard_techspec_repository.MotherboardTechSpecRepository(db)
    # motherboard support repository
    mbsr = repository.motherboard_support_repository.MotherboardSupportRepository(db)

    # init services
    motherboard_service = services.motherboard_service.MotherboardService(mbir, mbor, mbtr, mbsr)

    app = Flask(__name__)

    # init routes
    router = routes.motherboard_routes.MotherboardRoutes(app, motherboard_service)

    router.app.run(debug=True)