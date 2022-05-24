# -*- coding: utf-8 -*-

import os

from .utils import INSTANCE_FOLDER_PATH


class BaseConfig(object):
    # Change these settings as per your needs

    PROJECT = "ame_manager_app"
    PROJECT_NAME = "ame_manager_app.local"
    PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    BASE_URL = "https://ame-manager.local"
    ADMIN_EMAILS = ["admin@ame-manager.local"]

    DEBUG = False
    TESTING = False

    SECRET_KEY = "rf942ut8hg43ztyr579890ysrt"


class DefaultConfig(BaseConfig):

    DEBUG = True

    # Flask-Sqlalchemy
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # SQLITE for production
    # SQLALCHEMY_DATABASE_URI = f"sqlite:///{INSTANCE_FOLDER_PATH}/db.sqlite"

    # MYSQL for production
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{os.getenv('MARIADB_USER')}:{os.getenv('MARIADB_KEY')}@{os.getenv('MARIADB_HOST')}/{os.getenv('MARIADB_DBNAME')}"

    # Flask-cache
    CACHE_TYPE = "simple"
    CACHE_DEFAULT_TIMEOUT = 60

    # Flask-mail
    MAIL_DEBUG = False
    MAIL_SERVER = ""  # something like 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True

    # Keep these in instance folder or in env variables
    MAIL_USERNAME = "admin@ame-manager.local"
    MAIL_PASSWORD = ""
    MAIL_DEFAULT_SENDER = MAIL_USERNAME
    
    # Borrowing
    MAX_DAYS_BORROW = 365
