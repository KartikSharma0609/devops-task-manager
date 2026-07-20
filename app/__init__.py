from flask import Flask

from app.config import Config
from app.database import db


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    from app import models

    from app.routes import main_routes

    app.register_blueprint(main_routes)

    return app
