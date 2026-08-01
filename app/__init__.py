from flask import Flask, jsonify
from app.api import api
from flask_migrate import Migrate
from app.config import Config
from app.database import db
from flask_jwt_extended import JWTManager
from app.utils.logging_config import configure_logging


def create_app(config_class=Config):

    configure_logging()

    app = Flask(__name__)

    app.config.from_object(config_class)

    if not app.config.get("JWT_SECRET_KEY"):
        raise RuntimeError("JWT_SECRET_KEY environment variable is required.")

    db.init_app(app)

    Migrate(app, db)

    @app.route("/", methods=["GET"])
    def root_index():
        return jsonify({
            "name": "DevOps Task Manager API",
            "version": "1.0.0",
            "status": "running",
            "documentation": "/docs",
            "health": "/system/health"
        }), 200

    api.init_app(app)

    jwt = JWTManager()

    jwt.init_app(app)

    return app
