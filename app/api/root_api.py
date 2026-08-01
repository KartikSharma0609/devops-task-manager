from flask_restx import Namespace, Resource

root_ns = Namespace("", description="Root")


@root_ns.route("/")
class Root(Resource):

    def get(self):
        return {
            "name": "DevOps Task Manager API",
            "version": "1.0.0",
            "status": "running",
            "documentation": "/docs",
            "health": "/system/health"
        }, 200
