import os
from dotenv import load_dotenv

load_dotenv()


class Config:

    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 5000))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    if not JWT_SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY environment variable is required.")

    DATABASE_URL = os.getenv("DATABASE_URL")

    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = (
            f"postgresql://{DB_USER}:{DB_PASSWORD}"
            f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(Config):

    TESTING = True
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{Config.DB_USER}:{Config.DB_PASSWORD}"
        f"@{Config.DB_HOST}:{Config.DB_PORT}/"
        f"{os.getenv('TEST_DB_NAME')}"
    )
