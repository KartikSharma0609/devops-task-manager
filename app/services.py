from app.models import Task
from app.database import db

def fetch_tasks():

    tasks = Task.query.all()

    return [task.to_dict() for task in tasks]

def create_task(title, status="pending"):

    task = Task(
        title=title,
        status=status
    )

    db.session.add(task)

    db.session.commit()

    return task.to_dict()

def update_task(task_id, title, status):

    task = Task.query.get(task_id)

    if task is None:
        return None

    task.title = title
    task.status = status

    db.session.commit()

    return task.to_dict()
