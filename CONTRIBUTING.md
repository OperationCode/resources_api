# Contribution Guide

Firstly, thank you for considering making a contribution to our project! It's
people like you that make Operation Code such a great community.

We're an open source project and we love receiving contributions from our
community - you! There are many ways to contribute to our projects, from writing
tutorials or blog posts, improving documentation, submitting bug reports or
feature requests, or writing code which can be merged into any of our
repositories.

The team at Operation Code urges all contributors to join our Slack team.
Participating in discussions with the community on our Slack channel is the
best way to run new ideas by the team, and is the best place to get help. You
can get an invitation to our Slack channel by
[requesting to join Operation Code](https://operationcode.org/join). Once in our
Slack team, simply type: '/open #oc-python-projects' and then click enter. Feel
free to ask for help; everyone is a beginner at first :smile_cat:!

**This guide assumes that you have some at least some familiarity with
submitting a pull request on Github. If you don't, that's ok too. Simply
start by reading Github's own user documentation on how to fork a repository,
and make your own edits. That documentation is
[here](https://help.github.com/articles/about-pull-requests/) and
[here](https://help.github.com/articles/creating-a-pull-request/). 3rd party
tutorials on Git/Github can be found
[here](https://medium.freecodecamp.org/what-is-git-and-how-to-use-it-c341b049ae61)
and
[here](https://medium.freecodecamp.org/how-to-use-git-efficiently-54320a236369?source=linkShare-e41cd5edcdac-1535829065)**.

## Development Workflow

### Dependencies

The primary technologies used in this project are:

- [Python](https://www.python.org)
- [Flask](http://flask.pocoo.org)
- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/gettingstarted/)

To work on the codebase for this project, you will need to have those
dependencies installed.

#### Dependency Installation

1. **Docker**
   1. **Windows**: Docker on _Windows_ can be installed via
      [Docker Desktop](https://www.docker.com/products/docker-desktop).
   2. **Mac OS**: Docker on _Mac OS_ can be installed via
      [Docker Desktop](https://www.docker.com/products/docker-desktop) or via
      [Homebrew](https://brew.sh/) by doing (`brew install docker`).
   3. **Linux**: Depending on your Linux distribution (`cat /etc/os-release`),
      you can use your package manager on board typically to install Docker. Ex.
      `apt-get install docker` (if Ubuntu/Debian).
2. **Docker Compose**
   1. **Windows**: If installed via _Docker Desktop_, it will include
      _docker-compose_. Try to run _docker-compose version_ on commandline.
   2. **Mac OS**: Similar to above, if installed via _Docker Desktop_, it will
      include _docker-compose_. If using Homebrew please do
      `brew install docker-compose`.
   3. **Linux**: Please follow instructions at the _Linux_ tab
      [here](https://docs.docker.com/compose/install/). Linux has shell
      autocompletions available which are very helpful.

#### Dependency Resources

##### Cheatsheets

Cheatsheets are a nice way to get an high at-a-glance view of the
technology/tool. It's a very nice way to ramp up quickly with specific tooling.

- Python
  - [Learn X in Y Minutes](https://learnxinyminutes.com/docs/python3/)
  - [Devhints](https://devhints.io/python)
- Flask
  - [Pretty Printed](https://s3.us-east-2.amazonaws.com/prettyprinted/flask_cheatsheet.pdf)
  - [Flash Cheat Sheet](http://flask-cheat-sheet.herokuapp.com/)
- Docker
  - [Devhints](https://devhints.io/docker)
  - [Official Docker cheatsheet here](https://www.docker.com/sites/default/files/Docker_CheatSheet_08.09.2016_0.pdf)
- Docker Compose
  - [Devhints](https://devhints.io/docker-compose)

### Finding An Issue

<details>
	<summary>Click to Expand</summary>
<ul>
<li> After installing the listed dependencies, you can get to work coding on this project. A listing of this repo's issues can be found <a href="https://github.com/OperationCode/resources_api/issues">here</a>. Browse for an issue that you would like to work on. Don't be afraid to ask for help or clarification.</li>
<li> Once you have found an issue, leave a comment stating that you'd like to work on the issue. Once the issue is assigned to you, you may start working on it. </li>
</ul>
</details>

### Working On Your Issue

<details>
	<summary>Click to Expand</summary>

- After forking this repository to your own github account, and cloning it to
  your dev environment, you can now create a new branch on your machine. It's
  wise to name this branch after the issue you are trying to fix or the
  feature you are trying to add.

  ```bash
  git checkout -b creatingContributionGuide
  ```

- In the example above, I have created a new branch, named
  "creatingContributionGuide". This command also "checks out" the branch,
  meaning git now knows that is the branch you are working on. You can check
  what branch you are working on by using the `branch` command.

  ```bash
  git branch
  ```

- Following my example, `git branch`, would output "creatingContributionGuide"
  in my terminal.

- Once you have finished working on your issue, push your changes to your own
  github repo, and then submit a pull request.

- To return to your main `master` branch, type the following command in your
  terminal.

  ```bash
  git checkout master
  ```

  </details>

Before committing, please lint your code:

```sh
make lint
```
