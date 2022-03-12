from dbconfig import DBConfig
from flask import Flask
from flask import jsonify
from flask import request
from flask_cors import CORS

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

def init_app():
    """Initialize the core application."""
    app = Flask(__name__, instance_relative_config=False)
    # app.config.from_object('config.Config')

    # Initialize Plugins
    db.init_app(app)
    r.init_app(app)

    with app.app_context():
        # Include our Routes
        # from . import routes

        # Register Blueprints
        app.register_blueprint(auth.auth_bp)
        app.register_blueprint(admin.admin_bp)

        return app