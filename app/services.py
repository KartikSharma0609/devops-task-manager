from app.data import get_all_tasks, save_tasks


def fetch_tasks():

    return get_all_tasks()


def create_new_task(title):

    if not title.strip():

        return None


    tasks = get_all_tasks()


    if tasks:
        new_id = max(task["id"] for task in tasks) + 1
    else:
        new_id = 1

    new_task = {
        "id": new_id,
        "title": title.strip(),
        "status": "pending"
    }

    tasks.append(new_task)


    save_tasks(tasks)


    return new_task


def update_existing_task(task_id, updates):

    tasks = get_all_tasks()


    for task in tasks:

        if int(task["id"]) == int(task_id):

            if "title" in updates:

                if not updates["title"].strip():

                    return None

                task["title"] = updates["title"]


            if "status" in updates:

                if updates["status"] not in [
                    "pending",
                    "completed"
                ]:

                    return None


                task["status"] = updates["status"]


            save_tasks(tasks)

            return task


    return False


def delete_existing_task(task_id):

    tasks = get_all_tasks()

    for task in tasks:

        if task["id"] == task_id:

            tasks.remove(task)

            save_tasks(tasks)

            return True

    return False
