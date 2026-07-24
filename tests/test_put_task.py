from app.database import db
from app.models import Task


def test_update_task(client, auth_headers):

    with client.application.app_context():

        task = Task(title="Learn Docker", status="pending", user_id=1)

        db.session.add(task)
        db.session.commit()

        task_id = task.id

    response = client.put(
        f"/tasks/{task_id}",
        json={"title": "Learn Docker Deeply", "status": "completed"}, 
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["title"] == "Learn Docker Deeply"
    assert data["status"] == "completed"

    with client.application.app_context():

        updated_task = db.session.get(Task, task_id)

        assert updated_task.title == "Learn Docker Deeply"
        assert updated_task.status == "completed"


def test_update_non_existing_task(client, auth_headers):

    response = client.put(
        "/tasks/9999", json={"title": "Anything", "status": "pending"}, headers=auth_headers
    )

    assert response.status_code == 404

    assert response.get_json() == {"error": "Task not found"}


def test_update_with_empty_title(client, auth_headers):

    with client.application.app_context():

        task = Task(title="Docker", status="pending", user_id=1)

        db.session.add(task)
        db.session.commit()

        task_id = task.id

    response = client.put(f"/tasks/{task_id}", json={"title": ""}, headers=auth_headers)

    assert response.status_code == 400
