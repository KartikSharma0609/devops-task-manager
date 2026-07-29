from app.models import Task
from app.database import db
from app.utils.logger import get_logger

logger = get_logger(__name__)

def fetch_tasks(user_id):
    try:
        tasks = Task.query.filter_by(user_id=user_id).all()

        return [task.to_dict() for task in tasks]

    except Exception:
        # 4. If anything goes wrong, undo the pending transaction
        db.session.rollback()
        
        # 5. Log the full error trace for debugging
        logger.exception("Failed to fetch task for user_id=%s", user_id)
        
        # 6. Rethrow the error so your API route can catch it and send a 500 response
        raise

def create_task(user_id, title, status="pending"):
    try:
        task = Task(title=title, status=status, user_id=user_id)

        db.session.add(task)

        db.session.commit()

        logger.info(
            "Task created successfully (id=%s)",
            task.id
        )

        return task.to_dict()

    except Exception:
        # 4. If anything goes wrong, undo the pending transaction
        db.session.rollback()
        
        # 5. Log the full error trace for debugging
        logger.exception("Failed to create task", user_id)
        
        # 6. Rethrow the error so your API route can catch it and send a 500 response
        raise

def update_task(user_id, task_id, title, status):
    try:
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()

        if task is None:
            return None

        task.title = title
        task.status = status

        db.session.commit()

        logger.info(
            "Task updated (id=%s)",
            task.id
        )

        return task.to_dict()

    except Exception:
        # 4. If anything goes wrong, undo the pending transaction
        db.session.rollback()
        
        # 5. Log the full error trace for debugging
        logger.exception("Failed to Update task", task_id)
        
        # 6. Rethrow the error so your API route can catch it and send a 500 response
        raise

def delete_task(user_id, task_id):
    try:
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()

        if task is None:
            return False

        db.session.delete(task)

        db.session.commit()

        logger.info(
            "Task deleted (id=%s)",
            task.id
        )

        return True
    except Exception:
        # 4. If anything goes wrong, undo the pending transaction
        db.session.rollback()
        
        # 5. Log the full error trace for debugging
        logger.exception("Failed to Delete task", task_id)
        
        # 6. Rethrow the error so your API route can catch it and send a 500 response
        raise
