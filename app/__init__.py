from pathlib import Path

from flask import Flask, jsonify, send_from_directory
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

    # The built React app is copied here by the Dockerfile. When it is absent
    # (tests, local API-only runs) "/" keeps returning the JSON status.
    frontend_dist = Path(app.root_path) / "frontend_dist"

    frontend_dist = Path(app.root_path) / "frontend_dist"

    if frontend_dist.exists():
        @app.route("/", methods=["GET"])
        def root_index():
            return send_from_directory(frontend_dist, "index.html")

        # Safely serve your Vanilla JS files from the root of frontend_dist
        @app.route("/<any('app.js', 'styles.css'):filename>", methods=["GET"])
        def frontend_assets(filename):
            return send_from_directory(frontend_dist, filename)

    else:

        @app.route("/", methods=["GET"])
        def root_index():
            return (
                jsonify(
                    {
                        "name": "DevOps Task Manager API",
                        "version": "1.0.0",
                        "status": "running",
                        "documentation": "/docs",
                        "health": "/system/health",
                    }
                ),
                200,
            )

    api.init_app(app)

    jwt = JWTManager()

    jwt.init_app(app)

    return app
