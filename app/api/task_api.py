from flask import request
from app.services import fetch_tasks, create_task, update_task, delete_task
from flask_restx import Namespace, Resource, fields, marshal
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.logger import get_logger

logger = get_logger(__name__)



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
        logger.info("Fetching all tasks")
        user_id = int(get_jwt_identity())
        return fetch_tasks(user_id=user_id)

    @tasks_ns.expect(task_input)
    @jwt_required()
    def post(self):
        try:
            user_id = int(get_jwt_identity())
            data, error, status_code = validate_task_data()

            if error:
                return error, status_code

            new_task = create_task(user_id, data["title"], data["status"])
            return marshal(new_task, task_model), 201

        except Exception:
            # 5. Catch ANY unexpected crash (like a database failure)
            logger.exception("Unexpected error while creating task")
            return {"message": "Internal server error"}, 500


@tasks_ns.route("/<int:task_id>")
class Task(Resource):

    @tasks_ns.expect(task_input)
    @jwt_required()
    def put(self, task_id):
        try:
            user_id = int(get_jwt_identity())
            data, error, status_code = validate_task_data()

            if error:
                return error, status_code

            task = update_task(user_id, task_id, data["title"], data["status"])

            if task is None:
                logger.warning("Task %s not found", task_id)
                return {"error": "Task not found"}, 404

            return marshal(task, task_model), 200

        except Exception:
            # Pro-tip: include the task_id in the exception log for easier debugging
            logger.exception("Unexpected error while updating task %s", task_id)
            return {"message": "Internal server error"}, 500

    @jwt_required()
    def delete(self, task_id):
        try:
            user_id = int(get_jwt_identity())
            deleted = delete_task(user_id, task_id)

            if not deleted:
                return {"error": "Task not found"}, 404

            return {"message": "Task deleted successfully"}, 200

        except Exception:
            # Pro-tip: include the task_id in the exception log for easier debugging
            logger.exception("Unexpected error while deleting task %s", task_id)
            return {"message": "Internal server error"}, 500
