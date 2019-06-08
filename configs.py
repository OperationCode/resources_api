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


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = f"postgresql://{pg_user}:{pg_pw}@{pg_host}:5432/{pg_db}"

    # Can pass in changes to defaults, such as PaginatorConfig(per_page=40)
    RESOURCE_PAGINATOR = PaginatorConfig()
    LANGUAGE_PAGINATOR = PaginatorConfig()
    CATEGORY_PAGINATOR = PaginatorConfig()
