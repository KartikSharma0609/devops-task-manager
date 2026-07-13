import json
import os


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

FILE_PATH = os.path.join(
    BASE_DIR,
    "tasks.json"
)


def get_all_tasks():

    try:

        with open(FILE_PATH, "r") as file:
            tasks = json.load(file)

    except FileNotFoundError:

        tasks = []

    return tasks


def save_tasks(tasks):

    with open(FILE_PATH, "w") as file:

        json.dump(
            tasks,
            file,
            indent=4
        )
