from flask import Blueprint, jsonify
from app.services import fetch_tasks


main_routes = Blueprint(
    "main_routes",
    __name__
)


@main_routes.route("/")
def home():

    return {
        "message": "DevOps Task Manager API is running"
    }



@main_routes.route("/tasks", methods=["GET"])
def get_tasks():

    tasks = fetch_tasks()

    return jsonify(tasks)
