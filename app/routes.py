from flask import Blueprint, jsonify, request

from app.services import fetch_tasks, create_new_task


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



@main_routes.route("/tasks", methods=["POST"])
def add_task():

    data = request.get_json()


    task = create_new_task(
        data["title"]
    )


    return jsonify(task), 201
