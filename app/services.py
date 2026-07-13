from app.data import get_all_tasks, save_tasks


def fetch_tasks():

    return get_all_tasks()


def create_new_task(title):

    if not title.strip():

        return None


    tasks = get_all_tasks()


    new_task = {

        "id": len(tasks) + 1,

        "title": title,

        "status": "pending"

    }


    tasks.append(new_task)


    save_tasks(tasks)


    return new_task
