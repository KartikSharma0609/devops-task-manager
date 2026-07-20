from flask import Blueprint, request
from app.database import db
from app.services import (
    fetch_tasks,
    create_task,
    update_task
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

    return fetch_tasks()

@main_routes.route("/tasks", methods=["POST"])
def add_task():

    data = request.get_json(silent=True)

    if not data:

        return {
            "error": "Request body is required"
        }, 400

    title = data.get("title")

    if not title:

        return {
            "error": "Title is required"
        }, 400

    status = data.get("status", "pending")

    task = create_task(title, status)

    return task, 201

@main_routes.route("/tasks/<int:task_id>", methods=["PUT"])
def edit_task(task_id):

    data = request.get_json(silent=True)

    if not data:
        return {
            "error": "Request body is required"
        }, 400

    title = data.get("title")
    status = data.get("status")

    if not title:
        return {
            "error": "Title is required"
        }, 400

    if not status:
        return {
            "error": "Status is required"
        }, 400

    task = update_task(task_id, title, status)

    if task is None:
        return {
            "error": "Task not found"
        }, 404

    return task


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
