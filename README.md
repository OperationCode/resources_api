# Operation Code Learning Resources API

## Vision

This project provides an API for storing and retrieving learning resources that might be helpful to members of [Operation Code](https://operationcode.org/). Ideally, this project will provide the backend for various interfaces for working with the data. The first, and most important front end will be https://operationcode.org/resources.

## Getting Started

Sometimes these installs can be tricky.  If you get stuck ask for help in the Slack [#oc-python-projects](https://operation-code.slack.com/messages/C7NJLCCMB) channel!

If this is your first project using GitHub, Python, or pip follow these steps first:
1. Install [Git](https://git-scm.com/downloads).
- Choose your OS from the website and follow the prompts.  This installs Git and the Bash Terminal on your machine.
- Extra: [Git Documentation](https://git-scm.com/doc) for more information on Git.
2. Install and Setup Python.
- [Windows Users](https://docs.python.org/3/using/windows.html)
- [Mac Users](https://docs.python.org/3/using/mac.html)
3. Install [pip](https://pip.pypa.io/en/stable/installing/).
4. [Fork](https://help.github.com/articles/fork-a-repo/) this repository.
5. [Clone](https://help.github.com/articles/cloning-a-repository/) this repository in the Git Bash terminal.
- Navigate to where you would like to clone a fork of your repository. `cd \path\to\directory`
- Clone your fork of the project `git clone {project_url} resources`


Next, you'll need to configure a database. Once this project is deployed, we'll be using [PostgreSQL](https://www.postgresql.org/docs/). To set up a psql instance locally, follow the instructions for your OS:

### Windows Setup

<details>
<summary>Click to Expand</summary>

1. Setup up paths and system variables:
- Search --> Edit the [system environment variables](https://docs.microsoft.com/en-us/windows/desktop/shell/user-environment-variables) --> Environment Variables... --> Path --> Edit... --> New --> Enter `C:\ProgramData\chocolatey\bin` --> OK
- New --> `C:\Program Files\PostgreSQL\10\bin` --> OK
2. Close out of Environment Variables and System Properites.
3. Start your administrative shell. `ctrl + x` --> Windows Powershell (Admin).
- **Make sure you use the _admin powershell_ throughout all the steps.**
4. [Install Chocolatey](https://chocolatey.org/docs/installation#installing-chocolatey) if you do not already have it installed.
5. In your powershell (admin), run `choco install postgresql10`. Follow the prompts.
6. Upgrade postgresql: `choco upgrade postgresql`.
7. Start postgres: `psql -U postgres` you will see postgres-# in the terminal.
8. Create your user with `CREATE USER name WITH PASSWORD 'password';` The terminal will print CREATE ROLE.
9. Alter your role with permission to create a database with `ALTER USER name WITH CREATEDB CREATEROLE;` The terminal will print ALTER ROLE
10. Check everything is in order with `\du`. The terminal will print a table with Role name, Atrributes, and Member columns. If your user is listed you are good to go.
11. Create a database with: `CREATE DATABASE resources OWNER name;`.
12. Connect to the resources database: `\c resources`. If you see `resources =>` you are ready to move on to the next steps.
13. Navigate to the cloned repo directory `cd \path\to\resources`. (see step 6 under getting started)
14. Install virtualenv if you do not have it. `pip install virtualenv`.
15. [Create a virtual environment](https://docs.python.org/3/library/venv.html) called venv `python -m virtualenv venv`.
16. Set Execution Policy to unrestricted `Set-ExecutionPolicy Unrestricted -Force`
17. Activate the virtual environment `venv\Scripts\Activate.ps1`
18. Install the required dependencies `pip install pipenv`
21. Install --dev `pip install --dev`.
20. Edit the `.env` file with the following string, but replace the user, password, and database with whatever you used for your setup in the previous commands:
```
SQLALCHEMY_DATABASE_URI=postgresql://aaron:password@127.0.0.1:5432/resources
```
21. Optionally, enable debugging by adding this line to the `.env` file: `FLASK_ENV=development`
22. Run `pipenv shell` to load all the environment variables from `.env`
23. Create the tables in your database with `flask db-migrate create-tables`
24. Tell flask that your database is up to date with `flask db stamp head`
25. Populate your database with the resources `flask db-migrate init`
26. Start your development server with `flask run` and you're ready to go!
27. Check your work: Open your browser and go to `localhost:5000/api/v1/resources`. You should see a list of objects.
</details>

### Mac setup

<details>
<summary>Click to Expand</summary>

1. [Install Homebrew](https://brew.sh/) if you do not already have it installed
2. In your terminal, run `brew install postgresql`
3. Start postgres: `pg_ctl -D /usr/local/var/postgres start`
4. Ensure postgres is running: `pg_ctl -V`
5. Create your user with `createuser -d -P aaron` (replace "aaron" with your own name). You will be prompted to enter a password for this user.
Note: if you try to use the same username as the user you are logged in as, you will encounter an error. Instead, create a new postgres username.
6. Create a database with `createdb resources -U aaron` ("resources" is the name of the database, feel free to replace it with whatever you like. make sure you replace "aaron" with whatever you chose as your username in the previous step).
7. Now you should have postgres listening on the default port with your username and password. Edit the `.env` file with the following string, but replace the user, password, and database with whatever you used for your setup in the previous commands:
```
SQLALCHEMY_DATABASE_URI=postgresql://aaron:password@127.0.0.1:5432/resources
```
8. Navigate to the cloned repo directory `cd \path\to\resources`. (see step 6 under getting started)
9. Install virtualenv if you do not have it. `pip install virtualenv`.
10. [Create a virtual environment](https://docs.python.org/3/library/venv.html) called venv `python -m virtualenv venv`.
11. Activate virtual environment `source venv/bin/activate`
12. Install the required dependencies `pip install pipenv`.
13. Install --dev `pipenv install --dev`.
14. Optionally, enable debugging by adding this line to the `.env` file: `FLASK_ENV=development`
15. Run `pipenv shell` to load all the environment variables from `.env`
16. Create the tables in your database with `flask db-migrate create-tables`
17. Tell flask that your database is up to date with `flask db stamp head`
18. Populate your database with the resources `flask db-migrate init`
19. Start your development server with `flask run` and you're ready to go!
20. Check your work: Open your browser and go to `localhost:5000/api/v1/resources`. You should see a list of objects.
</details>


### Linux Setup

<details>
<summary>Click to Expand</summary>

1. Install postgresql. On A Debian or Ubuntu based system(Linux Mint, elementaryOS, etc), this would look like

	```bash
	sudo apt install postgresql postgresql-contrib
	#postgresql-contrib is an optional package that adds some additional utilities to make using postgresql easier
	```
2. On an Ubuntu based system, Postgresql will automatically be enabled when installing it this way.
3. Ensure postgres is running: `psql -V`
4. Create your user with `sudo -u postgres createuser -d -P --interactive`. This will give you a prompt to create a new user. It will ask for the name of the role to add. This is your username. Then it will ask for your password. You must pick a username, that is different from an existing login name on your computer. For example, if you are logged into your computer as "aaron", pick a name other than "aaron". The prompt will than ask if you want to be a superuser. Just press "y", and enter.
5. Create a database with `sudo -u postgres createdb resources -U aaron` ("resources" is the name we are giving to the database. You can call it whatever you'd like. Make sure to replace "aaron", with whatever username you gave to your postgres user.)
6. Now you should be able to scroll up on this page, and start following along with the Mac setup instructions, starting at step #7.
</details>


## Development Notes

If you make changes to the models.py or other schemas, you need to run a migration and upgrade again:

1. Load the environmnent variables with `pipenv shell`
2. Run the migration `flask db migrate`
3. Upgrade to the latest migration `flask db upgrade`

Before committing, please lint your code:

```sh
pip install --upgrade flake8
flake8 app
```
