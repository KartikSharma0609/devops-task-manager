from flask import Blueprint, jsonify, request
from app.database import db
from app.services import (
    fetch_tasks,
    create_new_task,
    update_existing_task,
    delete_existing_task
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


@main_routes.route("/tasks/<int:id>", methods=["DELETE"])
def delete_task(id):

    deleted = delete_existing_task(id)

    if not deleted:

        return jsonify({
            "error": "Task not found"
        }), 404

    return jsonify({
        "message": "Task deleted successfully"
    }), 200

@main_routes.route("/db-test")
def db_test():

    try:
        db.session.execute(db.text("SELECT 1"))

        return {
            "message": "Database connection successful!"
        }

    except Exception as e:

        return {
            "error": str(e)
        }, 500
