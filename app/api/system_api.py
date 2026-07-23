from flask_restx import Resource, Namespace
from app.database import db

system_ns = Namespace(
    "system",
    description="System endpoints"
)

@system_ns.route("/")
class Home(Resource):

    def get(self):
        return {
            "message": "DevOps Task Manager API is running"
        }

@system_ns.route("/db-test")
class DatabaseTest(Resource):

    def get(self):

        db.session.execute(db.text("SELECT 1"))

        return {
            "message": "Database connection successful!"
        }


