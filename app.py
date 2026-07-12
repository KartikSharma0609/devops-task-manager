from flask import Flask, jsonify, request

app = Flask(__name__)


tasks = [
    {
        "id": 1,
        "title": "Learn AWS",
        "status": "completed"
    },
    {
        "id": 2,
        "title": "Learn Docker",
        "status": "pending"
    }
]


@app.route("/")
def home():
    return jsonify({
        "message": "DevOps Task Manager API is running"
    })


# GET all tasks
@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify(tasks)


# CREATE task
@app.route("/tasks", methods=["POST"])
def create_task():

    data = request.get_json()

    new_task = {
        "id": len(tasks) + 1,
        "title": data["title"],
        "status": "pending"
    }

    tasks.append(new_task)

    return jsonify(new_task), 201



# UPDATE task
@app.route("/tasks/<int:id>", methods=["PUT"])
def update_task(id):

    for task in tasks:

        if task["id"] == id:

            data = request.get_json()

            task["title"] = data["title"]
            task["status"] = data["status"]

            return jsonify(task)

    return jsonify({
        "error": "Task not found"
    }), 404



# DELETE task
@app.route("/tasks/<int:id>", methods=["DELETE"])
def delete_task(id):

    for task in tasks:

        if task["id"] == id:

            tasks.remove(task)

            return jsonify({
                "message": "Task deleted"
            })

    return jsonify({
        "error": "Task not found"
    }), 404



if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
