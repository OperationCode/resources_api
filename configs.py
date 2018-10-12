
import sys, os

def get_sys_exec_root_or_drive():
    path = sys.executable
    while os.path.split(path)[1]:
        path = os.path.split(path)[0]
    return path

alternative_db = None

if os.environ.get('USE_SQLITE'):
    alternative_db = 'sqlite:///' + os.path.join(get_sys_exec_root_or_drive(), 'data.sqlite')
    print(alternative_db)

else:
    if not os.environ.get('SQLALCHEMY_DATABASE_URI'):
        raise KeyError("Application requires 'SQLALCHEMY_DATABASE_URL' to run in non DEVELOPMENT")


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or alternative_db
    SQL_LITE_DEFAULT = False or (alternative_db != None)
