from app.database import db
from app.models import Task


def test_delete_task(client, auth_headers):

    with client.application.app_context():

        task = Task(title="Delete Me", status="pending")

        db.session.add(task)
        db.session.commit()

        task_id = task.id

    response = client.delete(f"/tasks/{task_id}", headers=auth_headers)

    assert response.status_code == 200

    assert response.get_json() == {"message": "Task deleted successfully"}

    with client.application.app_context():

        deleted_task = db.session.get(Task, task_id)

        assert deleted_task is None


def test_delete_non_existing_task(client, auth_headers):

    response = client.delete("/tasks/9999", headers=auth_headers)

    assert response.status_code == 404

    assert response.get_json() == {"error": "Task not found"}
