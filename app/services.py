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
