import pytest

from app import create_app
from app.config import TestingConfig
from app.database import db
from app.models.user import User
from flask_jwt_extended import create_access_token


@pytest.fixture
def auth_headers(app):
    """Generates valid JWT authorization headers for testing."""
    with app.app_context():
        # Create a token for a test identity (e.g. user ID 1 or username)
        access_token = create_access_token(identity="1")
        return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def app():

    app = create_app(TestingConfig)

    with app.app_context():

        db.create_all()

        test_user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            password_hash="fakehash",
        )
        db.session.add(test_user)
        db.session.commit()

        yield app

        db.session.remove()

        db.drop_all()


@pytest.fixture
def client(app):

    return app.test_client()
