from flask_restx import Api
from flask_restx import fields

api = Api(
    title="DevOps Task Manager API",
    version="1.0",
    description="A REST API built with Flask, PostgreSQL, Docker and SQLAlchemy.",
    doc="/docs"
)

from app.api.task_api import tasks_ns
from app.api.system_api import system_ns
from app.api.auth_api import auth_ns


api.add_namespace(system_ns)
api.add_namespace(tasks_ns)
api.add_namespace(auth_ns)
