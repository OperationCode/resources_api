# Operation Code Learning Resources API

## Vision

This project provides an API for storing and retrieving learning resources that might be helpful to members of [Operation Code](https://operationcode.org/). Ideally, this project will provide the backend for various interfaces for working with the data. The first, and most important front end will be https://operationcode.org/resources.

## Getting Started

Sometimes these installs can be tricky.  If you get stuck ask for help in the Slack [#oc-python-projects](https://operation-code.slack.com/messages/C7NJLCCMB) channel!

1. Install [Git](https://git-scm.com/downloads).
- Choose your OS from the website and follow the prompts.  This installs Git and the Bash Terminal on your machine.
- Extra: [Git Documentation](https://git-scm.com/doc) for more information on Git.
2. Install Docker [Mac and Windows](https://www.docker.com/products/docker-desktop) or [Linux](https://docs.docker.com/install/linux/docker-ce/ubuntu/) and ensure it is running
- Linux: install [docker compose](https://docs.docker.com/compose/install/#install-compose) as well.
3. [Install Make](http://gnuwin32.sourceforge.net/packages/make.htm) if you're on Windows. OSX already has it installed. Linux will tell you how to install it (i.e., `sudo apt-get install make`)
4. Run `make setup`
5. Run `make all` and then navigate to http://localhost:8000/api/v1/resources

If you see some JSON with a bunch of resources, it worked! If you encounter any errors, please open an issue or contact us on slack in #oc-python-projects.

## Authentication

Routes that modify the database (e.g., `POST` and `PUT`) are authenticated routes. You need to include a header in your request with your API key. To generate an API key:

1. Send a POST to http://localhost:8000/api/v1/apikey with the following JSON payload:
```json
{
	"email": "your@email.com",
	"password": "yoursupersecretpassword"
}
```
The email and password specified should be your login credentials for the Operation Code website. If you are not a member of Operation Code, please sign up at https://operationcode.org/join

2. The response will be something similar to the following:
```json
{
    "apiVersion": "1.0",
    "data": {
        "apikey": "yourapikey",
        "email": "your@email.com"
    },
    "status": "ok"
}
```
3. When you create a request to an authenticated route, you must include a header `x-apikey: yourapikey`

## Development Notes

If you make changes to the models.py or other schemas, you need to run a migration and upgrade again:

```sh
make migrate
```

Before committing, please lint your code:

```sh
make lint
```
