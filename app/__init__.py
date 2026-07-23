from flask import Flask
from app.api import api
from flask_migrate import Migrate
from app.config import Config
from app.database import db
from flask_jwt_extended import JWTManager



def create_app(config_class=Config):

    app = Flask(__name__)

    app.config.from_object(config_class)

    db.init_app(app)

    Migrate(app, db)

    api.init_app(app)

    jwt = JWTManager()

    jwt.init_app(app)

    return app
