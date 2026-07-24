from flask import request
from app.services import fetch_tasks, create_task, update_task, delete_task
from flask_restx import Namespace, Resource, fields, marshal
from flask_jwt_extended import jwt_required, get_jwt_identity

tasks_ns = Namespace("tasks", description="Task operations")


task_model = tasks_ns.model(
    "Task",
    {
        "id": fields.Integer,
        "title": fields.String,
        "status": fields.String,
    },
)

task_input = tasks_ns.model(
    "TaskInput",
    {
        "title": fields.String(required=True),
        "status": fields.String(required=True),
    },
)


def validate_task_data():

    data = request.get_json(silent=True)

    if not data:
        return None, {"error": "Request body is required"}, 400

    title = data.get("title", "").strip()
    status = data.get("status", "").strip()

    if not title:
        return None, {"error": "Title is required"}, 400

    if not status:
        return None, {"error": "Status is required"}, 400

    return {"title": title, "status": status}, None, None


@tasks_ns.route("")
class TaskList(Resource):

    @tasks_ns.marshal_list_with(task_model)
    @jwt_required()
    def get(self):
        user_id = int(get_jwt_identity())
        return fetch_tasks(user_id=user_id)

    @tasks_ns.expect(task_input)
    @jwt_required()
    def post(self):
        user_id = int(get_jwt_identity())
        data, error, status_code = validate_task_data()

        if error:
            return error, status_code

        new_task = create_task(user_id, data["title"], data["status"])
        return marshal(new_task, task_model), 201


@tasks_ns.route("/<int:task_id>")
class Task(Resource):

    @tasks_ns.expect(task_input)
    @jwt_required()
    def put(self, task_id):
        user_id = int(get_jwt_identity())
        data, error, status_code = validate_task_data()

        if error:
            return error, status_code

        task = update_task(user_id, task_id, data["title"], data["status"])

        if task is None:
            return {"error": "Task not found"}, 404

        return marshal(task, task_model), 200

    @jwt_required()
    def delete(self, task_id):
        user_id = int(get_jwt_identity())
        deleted = delete_task(user_id, task_id)

        if not deleted:
            return {"error": "Task not found"}, 404

        return {"message": "Task deleted successfully"}, 200
