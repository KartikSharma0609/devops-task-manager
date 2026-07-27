from flask import request
from app.models.user import User
from flask_restx import Namespace, Resource, fields, abort
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from app.services.auth_service import register_user, login_user

auth_ns = Namespace("auth", description="Authentication APIs")


register_input = auth_ns.model(
    "RegisterInput",
    {
        "username": fields.String(required=True),
        "email": fields.String(required=True),
        "password": fields.String(required=True),
    },
)


login_input = auth_ns.model(
    "LoginInput",
    {"email": fields.String(required=True), "password": fields.String(required=True)},
)


user_model = auth_ns.model(
    "User", {"id": fields.Integer, "username": fields.String, "email": fields.String}
)

login_response = auth_ns.model(
    "LoginResponse", {"access_token": fields.String, "user": fields.Nested(user_model)}
)


@auth_ns.route("/register")
class Register(Resource):

    @auth_ns.expect(register_input)
    @auth_ns.marshal_with(user_model, code=201)
    @auth_ns.response(400, "Invalid input")
    @auth_ns.response(409, "Email already exists")
    def post(self):

        data = request.get_json()

        username = data.get("username", "").strip()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        if not username or not email or not password:
            abort(400, message="All fields are required")

        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            abort(409, message="Username already exists")

        user = register_user(username, email, password)

        if user is None:
            abort(409, message="Email already exists")

        return user, 201


@auth_ns.route("/login")
class Login(Resource):

    @auth_ns.expect(login_input)
    @auth_ns.marshal_with(login_response)
    @auth_ns.response(401, "Invalid credentials")
    def post(self):

        data = request.get_json()

        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        user = login_user(email, password)

        if user is None:
            return {"message": "Invalid email or password"}, 401

        access_token = create_access_token(identity=str(user.id))

        return {
            "access_token": access_token,
            "user": {"id": user.id, "username": user.username, "email": user.email},
        }


@auth_ns.route("/me")
class UserProfile(Resource):
    
    @auth_ns.doc(security="Bearer") # Adds lock icon in Swagger UI
    @jwt_required()
    def get(self):
        """Get the current logged-in user's profile."""
        # get_jwt_identity() returns the string we passed to create_access_token()
        current_user_id = get_jwt_identity() 
        
        user = User.query.get(current_user_id)
        
        if not user:
            abort(404, message="User not found")
            
        return {
            "id": user.id, 
            "username": user.username, 
            "email": user.email
        }, 200
