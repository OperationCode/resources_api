# resources_api
API for resources.yaml


To run database setup:

1. Make db connector string (configs.py)
2. git clone project_url resources 
3. cd resources
4. python -m virtualenv venv
5. activate virtual environment
6. pip install -r requirements.txt
7. cd db_setup 
8. `export FLASK_APP=app.py` or `ENV:FLASK_APP = "run.py"`
9. flask run

