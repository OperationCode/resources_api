# Operation Code Learning Resources API

## Vision

This project provides an API for storing and retrieving learning resources that might be helpful to members of [Operation Code](https://operationcode.org/). Ideally, this project will provide the backend for various interfaces for working with the data. The first, and most important front end will be https://operationcode.org/resources.

## Getting Started

Sometimes these installs can be tricky.  If you get stuck ask for help in the Slack [#oc-python-projects](https://operation-code.slack.com/messages/C7NJLCCMB) channel!

1. Install [Git](https://git-scm.com/downloads).
- Choose your OS from the website and follow the prompts.  This installs Git and the Bash Terminal on your machine.
- Extra: [Git Documentation](https://git-scm.com/doc) for more information on Git.
2. Fork & Clone
- [Fork a repository](https://help.github.com/articles/fork-a-repo/)
- Create a local clone of your fork (Step 2 in the document above)
3. Install Docker [Mac and Windows](https://www.docker.com/products/docker-desktop) or [Linux](https://docs.docker.com/install/linux/docker-ce/ubuntu/) and ensure it is running
- Linux: install [docker compose](https://docs.docker.com/compose/install/#install-compose) as well.
4. [Install Make](http://gnuwin32.sourceforge.net/packages/make.htm) if you're on Windows. OSX already has it installed. Linux will tell you how to install it (i.e., `sudo apt-get install make`)
5. Run `make setup`
6. Run `make all` and then navigate to http://localhost:5000/api/v1/resources

If you see some JSON with a bunch of resources, it worked! If you encounter any errors, please open an issue or contact us on slack in #oc-python-projects.

## Authentication

 Routes that modify the database (e.g., `POST` and `PUT`) are authenticated routes. You need to include a header in your request with your API key. To generate an API key:

 1. Send a POST to http://localhost:5000/api/v1/apikey with the following JSON payload:
```json
{
	"email": "your@email.com",
	"password": "yoursupersecretpassword"
}
```
The email and password specified should be your login credentials for the Operation Code website. If you are not a member of Operation Code, please sign up at https://operationcode.org/join

 2. The response will have the following structure (but will contain your email and apikey):
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

Example curl request to an authenticated route:
```bash
curl -X POST \
  http://127.0.0.1:5000/api/v1/resources \
  -H 'Content-Type: application/json' \
  -H 'x-apikey: 0a14f702da134390ae43f3639686fe26' \
  -d '{
        "category": "Regular Expressions",
        "languages": ["Regex"],
        "name": "Regex101",
        "notes": "Regular Expression tester",
        "paid": false,
        "url": "https://regex101.com/"
}'
```

## Development Notes

If you make changes to the models.py or other schemas, you need to run a migration and upgrade again:

```sh
make migrate
```

Before committing, please lint your code:

```sh
make lint
```

## History

This project began when I ([Aaron Suarez](https://github.com/aaron-suarez)) started to learn software development. I did a little searching for learning resources and started a list of resources I wanted to come back to when I had some time. Shortly after this, I joined [Operation Code](https://operationcode.org/join) and encountered several more learning resources that members were sharing. Soon enough, my list had grown to about 40 links. At some point, someone asked "Hey, does anyone have any learning resources?" and I said "I have a list of about 40 links that I can DM to you if you like."

Immediately, I received several requests from others asking for this list. I started to share it around via DMs, and someone suggested that I put it up on GitHub. I also got a lot of feedback about how it would be nice if there was more metadata, like a way to categorize the resources, organize them by language, and maybe even have some notes or a description (assuming the title isn't obvious). Meanwhile, the list continued to grow rapidly.

Someone got the bright idea to put it on the OC website, so I started working on a PR to incorporate it into OC, which at the time used Rails and YAML files to serve up list-like content. However, a redesign of the site was in progress, so my PR was never merged. Eventually I got out of the military and began doing software development full time. I kept maintaining the list as a little side project and sharing it around, but it hasn't made it onto the OC website. However, the [resources.yml](https://github.com/OperationCode/resources_api/blob/master/resources.yml) file is accessible via Slack with a slash command, so if you type `/repeat resources` in a public channel, the bot will link you to that file.

Eventually, the idea to use the data for multiple purposes was proposed. One really cool idea was for a Slack bot to ping relevant channels with random resources on a regular basis so that people could find awesome resources that had been shared without having to find them by searching the slack history. So it was decided that a full featured API would be important in order to really serve the needs of the OC community. This repo contains the source for the aforementioned API.

It took a lot of time and collaborative effort to put together the data and to build the API, and the work is not done yet! Please help us out, and feel free to use the learning resources to gain the knowledge required to contribute.
