# Operation Code Learning Resources API

## Vision

This project provides an API for storing and retrieving learning resources that might be helpful to members of [Operation Code](https://operationcode.org/). Ideally, this project will provide the backend for various interfaces for working with the data. The first, and most important front end will be https://operationcode.org/resources.

## Getting Started

First, you'll need to configure a database. Once this project is deployed, we'll be using PostgreSQL. To set up a psql instance locally, follow the instructions for your OS:

### Windows setup

## Chocolatey and Postgres: (Needs Testing)
1. [Install Chocolatey](https://chocolatey.org/docs/installation#installing-chocolatey) if you do not already have it installed.
2. Add `C:\ProgramData\chocolatey\bin` to your paths (type path in search, click Edit environment varaibles for you account).
3. In your powershell (admin), run `choco install postgresql10` (powershell (admin) can be found by pressing `win + x`). 
- Make sure you use the admin powershell throughout all the steps.
4. Upgrade postgresql: `choco upgrade postgresql`.
5. Add `C:\Program Files\PostgreSQL\10\bin` to your [paths](https://helpdeskgeek.com/windows-10/add-windows-path-environment-variable/).
6. Restart your admin terminal to update the path. 
7. Start postgres: `psql -U postgres` you will see postgres-# in the terminal.
8. Create your user with `CREATE USER name;` The terminal will print CREATE ROLE.
9. Alter your role with permission to create a database with `ALTER USER name WITH CREATEDB CREATEROLE;` The terminal will print ALTER ROLE
10. Check everything is in order with `\du`. The terminal will print a table with Role name, Atrributes, and Member of columns. If your user is listed you are good to go.
11. Quit with `\q` or `ctr + c`.
12. Start psql with new username with `psql`. You should see `name=>`.
13. Create a database with: `CREATE DATABASE resources OWNER name;`.
14. Connect to the resources database: `\c resources`. If you see resources => you are ready to move on to the next steps.
## Set Up and Activate your Environment:
15. Set the connection information in a [user environment variable](https://docs.microsoft.com/en-us/windows/desktop/shell/user-environment-variables):
- Search --> Edit the System Environment Variables --> Environment Variables... (at bottom) --> System Variables: New... --> 
    - Variable Name: `SQLALCHEMY_DATABASE_URI`
    - Variable Value: `postgresql://aaron:password@127.0.0.1:5432/resources` (use your chosen username, password and database name)
16. In powershell navigate to where you would like to clone a fork of your repository. `cd \path\to\directory`
16. Clone your fork of the project `git clone {project_url} resources`
17. Change directory into the project `cd resources-api`
18. [Create a virtual environment](https://docs.python.org/3/library/venv.html) called venv `python -m virtualenv venv`.
19. Set Execution Policy to unrestricted `Set-ExecutionPolicy Unrestricted -Force`
20. Activate virtual environment venv\Scripts\Activate.ps1
21. Install the required dependencies `pip install -r requirements.txt`
22. Set the FLASK_APP environment variable (see step 15) 
- Variable name: `FLASK_APP`
- Variable Value: `run.py`
- Optionally, enable debugging by setting the environment to development with the Variable Value: `development`
24. Restart powershell.
23. Create the tables in your database with `flask db_migrate create_tables`
24. Tell flask that your database is up to date with `flask db stamp head`
25. Populate your database with the resources `flask db_migrate init`
26. Start your development server with `flask run` and you're ready to go!

27. Check your work: `Ctrl + c` then `psql resources`. The terminal pointer will say `resources=>`. Then `\dt` to view the schema.


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
13. Set the FLASK_APP environment variable `export FLASK_APP=run.py` or `ENV:FLASK_APP = "run.py"`
14. Optionally, enable debugging by setting the environment to development with `export FLASK_ENV=development`
15. Create the tables in your database with `flask db_migrate create_tables`
16. Tell flask that your database is up to date with `flask db stamp head`
17. Populate your database with the resources `flask db_migrate init`
18. Start your development server with `flask run` and you're ready to go!


## Development Notes

If you make changes to the models.py or other schemas, you need to run a migration and upgrade again:

1. Set the FLASK_APP environment variable `export FLASK_APP=run.py` or `ENV:FLASK_APP = "run.py"`
- Windows users follow Step 22 in the Windows setup.
2. Run the migration `flask db migrate`
3. Upgrade to the latest migration `flask db upgrade`

Before committing, please lint your code:

```sh
pip install --upgrade flake8
flake8 app
```
