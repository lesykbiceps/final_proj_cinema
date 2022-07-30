import os
from dotenv import load_dotenv

sqlite_uri = os.path.abspath("app/database/database.db")
project_root = os.getcwd()
load_dotenv()


class Config(object):
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']

    JWT_ACCESS_TOKEN_EXPIRES = 3000  # seconds
    JWT_REFRESH_TOKEN_EXPIRES = 800_000
    SQLALCHEMY_DATABASE_URI = (os.environ.get('SQLALCHEMY_DATABASE_URI')
                               or 'sqlite:///' + os.path.abspath("app/database/database.db"))
