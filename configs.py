import os
import sys
from dataclasses import dataclass


@dataclass
class PaginatorConfig:
    per_page: int = 20
    max_page_size: int = 100


def get_sys_exec_root_or_drive():
    path = sys.executable
    while os.path.split(path)[1]:
        path = os.path.split(path)[0]
    return path


postgres_user = os.environ.get('POSTGRES_USER')
if not postgres_user:
    raise KeyError("Application requires 'POSTGRES_USER' to run")

postgres_password = os.environ.get('POSTGRES_PASSWORD')
if not postgres_password:
    raise KeyError("Application requires 'POSTGRES_PASSWORD' to run")

postgres_db = os.environ.get('POSTGRES_DB')
if not postgres_db:
    raise KeyError("Application requires 'POSTGRES_DB' to run")

postgres_host = os.environ.get('POSTGRES_HOST')
if not postgres_host:
    raise KeyError("Application requires 'POSTGRES_HOST' to run")

application_id = os.environ.get('APPLICATION_ID')
api_key = os.environ.get('API_KEY')
if not all([application_id, api_key]):
    print("Application requires 'APPLICATION_ID' and 'API_KEY' for search functionality.")

index_name = os.environ.get("INDEX_NAME")


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:5432/{postgres_db}"
    APPLICATION_ID = application_id
    API_KEY = api_key
    INDEX_NAME = index_name

    # Can pass in changes to defaults, such as PaginatorConfig(per_page=40)
    RESOURCE_PAGINATOR = PaginatorConfig()
    LANGUAGE_PAGINATOR = PaginatorConfig()
    CATEGORY_PAGINATOR = PaginatorConfig()
