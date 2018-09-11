# Operation Code Learning Resources API

## Vision

This project provides an API for storing and retrieving learning resources that might be helpful to members of [Operation Code](https://operationcode.org/). Ideally, this project will provide the backend for various interfaces for working with the data. The first, and most important front end will be https://operationcode.org/resources.

## Getting Started

First, you'll need to configure a database. Once this project is deployed, we'll be using PostgreSQL. To set up a psql instance locally, follow the instructions for your OS:

### Windows setup

Coming Soon!

### Mac setup

1. [Install Homebrew](https://brew.sh/) if you do not already have it installed
2. In your terminal, run `brew install postgresql`
3. Start postgres: `pg_ctl -D /usr/local/var/postgres start`
4. Ensure postgres is running: `pg_ctl -V`
5. Create your user with `createuser -d -P aaron` (replace "aaron" with your own name). You will be prompted to enter a password for this user.
Note: if you try to use the same username as the user you are logged in as, you will encounter an error. Instead, create a new postgres username.
6. Create a database with `createdb resources -U aaron` ("resources" is the name of the database, feel free to replace it with whatever you like. make sure you replace "aaron" with whatever you chose as your username in the previous step).
7. Now you should have postgres listening on the default port with your username and password. Set the connection information in an environment variable with the following command, but replace the user, password, and database with whatever you used for your setup in the previous commands:
```
export SQLALCHEMY_DATABASE_URI=postgresql://aaron:password@127.0.0.1:5432/resources
```
8. Clone your fork of the project `git clone {project_url} resources`
9. Change directory into the project `cd resources`
10. Create a virtual environment called venv `python -m virtualenv venv`
11. Activate virtual environment `source venv/bin/activate`
12. Install the required dependencies `pip install -r requirements.txt`
13. Change into the db_setup directory `cd db_setup`
14. Set the FLASK_APP environment variable `export FLASK_APP=app.py` or `ENV:FLASK_APP = "app.py"`
15. Set the FLASK_APP environment variable `export FLASK_APP=app.py`
16. Comment out the call to `import_resources()` (TODO: we need to make it so we can run the migration without having to comment out this function call)
NOTE: The following will fail until we find a way to get alembic to play nicely
17. Run the migration `flask db migrate`
18. Upgrade to the latest migration `flask db upgrade`
19. Uncomment the call to `import_resources()` and then execute `flask run`


## Development Notes

If you make changes to the models.py or other schemas, you need to run a migration and upgrade again:

1. Set the FLASK_APP environment variable `export FLASK_APP=app.py` or `ENV:FLASK_APP = "app.py"`
2. Comment out the call to `import_resources()` or it will try to import them too (which we don't want)
3. Run the migration `flask db migrate`
4. Upgrade to the latest migration `flask db upgrade`
