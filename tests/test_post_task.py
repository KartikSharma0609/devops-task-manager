from app.database import db
from app.models import Task


def test_create_task(client):

    response = client.post(
        "/tasks",
        json={
            "title": "Learn Terraform"
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["title"] == "Learn Terraform"

    assert data["status"] == "pending"

    with client.application.app_context():

        task = Task.query.first()

        assert task is not None

        assert task.title == "Learn Terraform"

        assert task.status == "pending"


def test_create_task_without_title(client):

    response = client.post(
        "/tasks",
        json={}
    )

    assert response.status_code == 400

    assert response.get_json() == {
        "error": "Request body is required"
    }

def test_create_task_with_empty_title(client):

    response = client.post(
        "/tasks",
        json={
            "title": ""
        }
    )

    assert response.status_code == 400

    assert response.get_json() == {
        "error": "Title is required"
    }


def test_create_task_with_blank_title(client):

    response = client.post(
        "/tasks",
        json={
            "title": "     "
        }
    )

    assert response.status_code == 400

    assert response.get_json() == {
        "error": "Title is required"
    }


def test_create_task_without_json(client):

    response = client.post("/tasks")

    assert response.status_code == 400
