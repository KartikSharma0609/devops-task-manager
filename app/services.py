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
