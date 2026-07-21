from flask import Flask

from flask_migrate import Migrate

from app.config import Config
from app.database import db


def create_app(config_class=Config):

    app = Flask(__name__)

    app.config.from_object(config_class)

    db.init_app(app)

    Migrate(app, db)

    from app.routes import main_routes

    app.register_blueprint(main_routes)

    return app
