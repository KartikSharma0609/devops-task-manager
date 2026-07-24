from werkzeug.security import generate_password_hash, check_password_hash
from app.database import db
from app.models import User


def hash_password(password):
    return generate_password_hash(password)


def verify_password(password_hash, password):
    return check_password_hash(password_hash, password)


def register_user(username, email, password):

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return None

    user = User(username=username, email=email, password_hash=hash_password(password))

    db.session.add(user)
    db.session.commit()

    return user


def login_user(email, password):

    user = User.query.filter_by(email=email).first()

    if user is None:
        return None

    if not verify_password(user.password_hash, password):
        return None

    return user
