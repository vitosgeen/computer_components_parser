import sys
import os
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import Config
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

    config = Config()

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


    # Secret key for JWT
    app.config["JWT_SECRET_KEY"] = config.JWT_SECRET
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 60 * 60 * 24 * 7  # 1 week
    jwt = JWTManager(app)

    # init routes
    router = routes.motherboard_routes.MotherboardRoutes(app, motherboard_service, config)

    router.app.run(debug=True)