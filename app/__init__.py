from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_security.core import Security
from flask_security.datastore import SQLAlchemyUserDatastore
from flask_cors import CORS
from .models import db, User, Role
from .auth import auth_bp
from .surplus import surplus_bp
from .requests import requests_bp
from .config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    CORS(app, supports_credentials=True, origins=["*"])
    db.init_app(app)

    # Set up Flask-Security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    Security(app, user_datastore)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(surplus_bp, url_prefix="/api")
    app.register_blueprint(requests_bp, url_prefix="/api")

    return app
