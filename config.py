import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")

    DATABASE_URL = os.environ.get("DATABASE_URL")

 
    if not DATABASE_URL:
        DATABASE_URL = "sqlite:///volunteer.db"

    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
