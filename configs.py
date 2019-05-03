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

search_user = os.environ.get('SEARCH_USER')
search_key = os.environ.get('SEARCH_KEY')
if not all([search_user, search_key]):
    print("Application requires 'SEARCH_USER' and 'SEARCH_KEY' for search functionality.")

search_resource_index = os.environ.get("SEARCH_RESOURCE_INDEX")


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:5432/{postgres_db}"
    SEARCH_USER = search_user
    SEARCH_KEY = search_key
    SEARCH_RESOURCE_INDEX = search_resource_index

    # Can pass in changes to defaults, such as PaginatorConfig(per_page=40)
    RESOURCE_PAGINATOR = PaginatorConfig()
    LANGUAGE_PAGINATOR = PaginatorConfig()
    CATEGORY_PAGINATOR = PaginatorConfig()
