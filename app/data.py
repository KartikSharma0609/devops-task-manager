import json


FILE_PATH = "tasks.json"


def get_all_tasks():

    with open(FILE_PATH, "r") as file:

        tasks = json.load(file)

    return tasks
