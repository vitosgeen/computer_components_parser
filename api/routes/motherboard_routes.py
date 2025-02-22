from flask import Flask, Response, jsonify, request

# routes for the motherboard controllers
class MotherboardRoutes:
    def __init__(self, app, motherboard_controller):
        self.app = app
        self.motherboard_controller = motherboard_controller
        self.init_routes()

    def init_routes(self):
        @self.app.route('/motherboards', methods=['GET'])
        def get_all_motherboards():
            # get query parameters
            limit = request.args.get('limit')
            offset = request.args.get('offset')
            if limit is None:
                limit = 1
            if offset is None:
                offset = 0
                
            return jsonify(self.motherboard_controller.get_all_motherboards(limit, offset))
            