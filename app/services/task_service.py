from app.models import Task
from app.database import db


def fetch_tasks(user_id):

    tasks = Task.query.filter_by(user_id=user_id).all()

    return [task.to_dict() for task in tasks]


def create_task(user_id, title, status="pending"):

    task = Task(title=title, status=status, user_id=user_id)

    db.session.add(task)

    db.session.commit()

    return task.to_dict()


def update_task(user_id, task_id, title, status):

    task = Task.query.filter_by(id=task_id, user_id=user_id).first()

    if task is None:
        return None

    task.title = title
    task.status = status

    db.session.commit()

    return task.to_dict()


def delete_task(user_id, task_id):

    task = Task.query.filter_by(id=task_id, user_id=user_id).first()

    if task is None:
        return False

    db.session.delete(task)

    db.session.commit()

    return True
