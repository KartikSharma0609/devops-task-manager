from flask_restx import Resource, Namespace
from sqlalchemy import text

from app.database import db

system_ns = Namespace("system", description="System endpoints")


@system_ns.route("/")
class Home(Resource):

    def get(self):
        return {"message": "DevOps Task Manager API is running"}


@system_ns.route("/db-test")
class DatabaseTest(Resource):

    def get(self):

        db.session.execute(db.text("SELECT 1"))

        return {"message": "Database connection successful!"}

@system_ns.route("/health")
class Health(Resource):

    def get(self):

        try:
            db.session.execute(text("SELECT 1"))

            return {
                "status": "healthy",
                "database": "connected"
            }

        except Exception:

            return {
                "status": "unhealthy",
                "database": "disconnected"
            }, 500
