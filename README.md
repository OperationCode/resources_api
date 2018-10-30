# Operation Code Learning Resources API

## Vision

This project provides an API for storing and retrieving learning resources that might be helpful to members of [Operation Code](https://operationcode.org/). Ideally, this project will provide the backend for various interfaces for working with the data. The first, and most important front end will be https://operationcode.org/resources.

## Getting Started

If this is your first project using GitHub, Python, or pip follow these steps first:
1. Install [Git](https://git-scm.com/downloads).
- Choose your OS from the website and follow the prompts.  This installs Git and the Bash Terminal on your machine.
- Extra: [Git Documentation](https://git-scm.com/doc) for more information on Git.
2. Install and Setup Python.
- [Windows Users](https://docs.python.org/3/using/windows.html)
- [Mac Users](https://docs.python.org/3/using/mac.html)
3. Install [pip](https://pip.pypa.io/en/stable/installing/).
4. Sometimes these installs can be tricky.  If you get stuck ask for help in the Slack [#oc-python-projects](https://operation-code.slack.com/messages/C7NJLCCMB) channel! 
5. [Fork](https://help.github.com/articles/fork-a-repo/) this repository.
6. [Clone](https://help.github.com/articles/cloning-a-repository/) this repository in the Git Bash terminal.
- Navigate to where you would like to clone a fork of your repository. `cd \path\to\directory`
- Clone your fork of the project `git clone {project_url} resources`


Next, you'll need to configure a database. Once this project is deployed, we'll be using [PostgreSQL](https://www.postgresql.org/docs/). To set up a psql instance locally, follow the instructions for your OS:

### Windows Setup

1. Setup up paths and system variables:   
- Search --> Edit the [system environment variables](https://docs.microsoft.com/en-us/windows/desktop/shell/user-environment-variables) --> Environment Variables... --> Path --> Edit... --> New --> Enter `C:\ProgramData\chocolatey\bin` --> OK
- New --> `C:\Program Files\PostgreSQL\10\bin` --> OK
2. Set the System Variables.
- Click the bottom New... -->
- Connection Variable:
    - Variable Name: `SQLALCHEMY_DATABASE_URI`
    - Variable Value: `postgresql://aaron:password@127.0.0.1:5432/resources` (instead of aaron and password put what user name and password you want to use for postgresql) 
- FLASK_APP Variable:
    - Variable name: `FLASK_APP`
    - Variable Value: `run.py`
    - Optionally, enable debugging by setting the environment to development with the Variable Value: `development`
3. Close out of Environment Variables and System Properites.
4. Start your administrative shell. `ctrl + x` --> Windows Powershell (Admin).
- **Make sure you use the _admin powershell_ throughout all the steps.**
5. [Install Chocolatey](https://chocolatey.org/docs/installation#installing-chocolatey) if you do not already have it installed.
6. In your powershell (admin), run `choco install postgresql10`. Follow the prompts.
7. Upgrade postgresql: `choco upgrade postgresql`.
8. Start postgres: `psql -U postgres` you will see postgres-# in the terminal.
9. Create your user with `CREATE USER name WITH PASSWORD 'password';` The terminal will print CREATE ROLE.
10. Alter your role with permission to create a database with `ALTER USER name WITH CREATEDB CREATEROLE;` The terminal will print ALTER ROLE
11. Check everything is in order with `\du`. The terminal will print a table with Role name, Atrributes, and Member columns. If your user is listed you are good to go.
12. Create a database with: `CREATE DATABASE resources OWNER name;`.
13. Connect to the resources database: `\c resources`. If you see `resources =>` you are ready to move on to the next steps.
14. Navigate to the cloned repo directory `cd \path\to\resources`. (see step 6 under getting started)
15. Install virtualenv if you do not have it. `pip install virtualenv`.
16. [Create a virtual environment](https://docs.python.org/3/library/venv.html) called venv `python -m virtualenv venv`.
17. Set Execution Policy to unrestricted `Set-ExecutionPolicy Unrestricted -Force`
18. Activate the virtual environment `venv\Scripts\Activate.ps1`
19. Install the required dependencies `pip install pipenv`
20. Install --dev `pip install --dev`.
21. Create the tables in your database with `flask db-migrate create-tables`
22. Tell flask that your database is up to date with `flask db stamp head`
23. Populate your database with the resources `flask db-migrate init`
24. Start your development server with `flask run` and you're ready to go!
25. Check your work: Open your browser and go to `localhost:5000/api/v1/resources`. You should see a list of objects. 


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
8. Navigate to the cloned repo directory `cd \path\to\resources`. (see step 6 under getting started)
9. Install virtualenv if you do not have it. `pip install virtualenv`.
10. [Create a virtual environment](https://docs.python.org/3/library/venv.html) called venv `python -m virtualenv venv`.
11. Activate virtual environment `source venv/bin/activate`
12. Install the required dependencies `pip install pipenv`.
13. Install --dev `pip install --dev`.
14. Set the FLASK_APP environment variable `export FLASK_APP=run.py` or `ENV:FLASK_APP = "run.py"`
15. Optionally, enable debugging by setting the environment to development with `export FLASK_ENV=development`
16. Create the tables in your database with `flask db-migrate create-tables`
17. Tell flask that your database is up to date with `flask db stamp head`
18. Populate your database with the resources `flask db-migrate init`
19. Start your development server with `flask run` and you're ready to go!


## Development Notes

If you make changes to the models.py or other schemas, you need to run a migration and upgrade again:

1. Set the FLASK_APP environment variable 
- Mac OS: `export FLASK_APP=run.py` or `ENV:FLASK_APP = "run.py"`
- Windows: see step 1 & 2 under Windows Setup
2. Run the migration `flask db migrate`
3. Upgrade to the latest migration `flask db upgrade`

Before committing, please lint your code:

```sh
pip install --upgrade flake8
flake8 app
```
