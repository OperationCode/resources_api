import os
import sys
from dataclasses import dataclass


@dataclass
class PaginatorConfig:
    per_page: int = 20
    max_page_size: int = 200


def get_sys_exec_root_or_drive():
    path = sys.executable
    while os.path.split(path)[1]:
        path = os.path.split(path)[0]
    return path


pg_user = os.environ.get('POSTGRES_USER')
if not pg_user:
    raise KeyError("Application requires 'POSTGRES_USER' to run")

pg_pw = os.environ.get('POSTGRES_PASSWORD')
if not pg_pw:
    raise KeyError("Application requires 'POSTGRES_PASSWORD' to run")

pg_db = os.environ.get('POSTGRES_DB')
if not pg_db:
    raise KeyError("Application requires 'POSTGRES_DB' to run")

pg_host = os.environ.get('POSTGRES_HOST')
if not pg_host:
    raise KeyError("Application requires 'POSTGRES_HOST' to run")

algolia_app_id = os.environ.get('ALGOLIA_APP_ID')
algolia_api_key = os.environ.get('ALGOLIA_API_KEY')
if not all([algolia_app_id, algolia_api_key]):
    print("Application requires 'ALGOLIA_APP_ID' and 'ALGOLIA_API_KEY' for search")

secret_key = os.environ.get('SECRET_KEY', None)
security_password_hash = 'pbkdf2_sha512'
security_password_salt = os.environ.get('SECURITY_PASSWORD_SALT', None)

if not all([secret_key, security_password_salt]):
    print('Application requires "SECRET_KEY" and "SECURITY_HASH"')

index_name = os.environ.get("INDEX_NAME")


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_DATABASE_URI = f"postgresql://{pg_user}:{pg_pw}@{pg_host}:5432/{pg_db}"

    ALGOLIA_APP_ID = algolia_app_id
    ALGOLIA_API_KEY = algolia_api_key
    INDEX_NAME = index_name

    SECRET_KEY = secret_key
    SECURITY_URL_PREFIX = "/admin"
    SECURITY_PASSWORD_HASH = security_password_hash
    SECURITY_PASSWORD_SALT = security_password_salt
    SECURITY_LOGIN_URL = "/login/"
    SECURITY_LOGOUT_URL = "/logout/"
    SECURITY_POST_LOGIN_VIEW = "/admin/"
    SECURITY_POST_LOGOUT_VIEW = "/admin/"
    SECURITY_REGISTERABLE = False
    SECURITY_SEND_REGISTER_EMAIL = False
    # Can pass in changes to defaults, such as PaginatorConfig(per_page=40)
    RESOURCE_PAGINATOR = PaginatorConfig()
    LANGUAGE_PAGINATOR = PaginatorConfig()
    CATEGORY_PAGINATOR = PaginatorConfig()
