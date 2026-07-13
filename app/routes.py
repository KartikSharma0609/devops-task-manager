from flask import Blueprint, jsonify, request

from app.services import (
    fetch_tasks,
    create_new_task,
    update_existing_task
)

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

    data = request.get_json(silent=True)


    if data is None:

        return jsonify({
            "error": "Request body is required"
        }), 400


    if "title" not in data:

        return jsonify({
            "error": "Title is required"
        }), 400


    task = create_new_task(
    data["title"]
    )


    if task is None:

        return jsonify({
            "error": "Title cannot be empty"
        }),400


    return jsonify(task),201

@main_routes.route("/tasks/<int:id>", methods=["PUT"])
def update_task(id):

    data = request.get_json(silent=True)


    if data is None:

        return jsonify({
            "error":"Request body is required"
        }),400


    if not data:

        return jsonify({
            "error":"No update data provided"
        }),400


    task = update_existing_task(
        id,
        data
    )


    if task is False:

        return jsonify({
            "error":"Task not found"
        }),404


    if task is None:

        return jsonify({
            "error":"Invalid update data"
        }),400


    return jsonify(task)
