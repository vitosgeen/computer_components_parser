from flask import Flask, jsonify

# routes for the motherboard controllers
class MotherboardRoutes:
    def __init__(self, app, motherboard_controller):
        self.app = app
        self.motherboard_controller = motherboard_controller
        self.init_routes()

    def init_routes(self):
        @self.app.route('/motherboards', methods=['GET'])
        def get_all_motherboards():
            motherboards = self.motherboard_controller.get_all_motherboards()
            return jsonify(motherboards)
            