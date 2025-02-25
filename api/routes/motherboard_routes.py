from flask import Flask, Response, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

# routes for the motherboard controllers
class MotherboardRoutes:
    def __init__(self, app, motherboard_controller, config):
        self.config = config
        self.app = app
        self.motherboard_controller = motherboard_controller
        self.init_routes()

    def init_routes(self):
        self.login_route()
        @self.app.route('/motherboards', methods=['GET'])
        @jwt_required()
        def get_all_motherboards():
            current_user = get_jwt_identity()
            # if unknown user
            if current_user != self.config.USER_LOGIN:
                return Response('Invalid user', 401)
            # get query parameters
            limit = request.args.get('limit')
            offset = request.args.get('offset')
            if limit is None:
                limit = 1
            if offset is None:
                offset = 0
                
            mb = self.motherboard_controller.get_all_motherboards(limit, offset)

            return jsonify(mb)
        
        
    def login_route(self):
        @self.app.route('/login', methods=['GET'])
        def loginForm():
            # get the login form from the templates/login.html file
            return self.render_template('login.html')
        @self.app.route('/login', methods=['POST'])
        def login():
            if not request.json:
                username = request.form.get('username', None)
                password = request.form.get('password', None)
            else:
                username = request.json.get('username', None)
                password = request.json.get('password', None)
            if username != self.config.USER_LOGIN or password != self.config.USER_PASSWORD:
                return Response('Invalid login', 401)
            access_token = create_access_token(identity=username)
            return jsonify(access_token=access_token)
            
    def render_template(self, template_name):
        with open('templates/' + template_name, 'r') as f:
            return f.read()