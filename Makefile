DOCKER := docker
DOCKER_COMPOSE := docker-compose
RESOURCES_CONTAINER := resources
FLASK := flask

.PHONY: all
all: run

.PHONY:  nuke
nuke:
	${DOCKER} system prune -a --volumes

.PHONY: minty-fresh
minty-fresh:
	${DOCKER_COMPOSE} down --rmi all --volumes

.PHONY: rmi
rmi:
	${DOCKER} images -q | xargs docker rmi -f

.PHONY: rmdi
rmdi:
	${DOCKER} images -a --filter=dangling=true -q | xargs ${DOCKER} rmi

.PHONY: rm-exited-containers
rm-exited-containers:
	${DOCKER} ps -a -q -f status=exited | xargs ${DOCKER} rm -v

.PHONY: fresh-restart
fresh-restart: minty-fresh setup test run

.PHONY: run
run:
	${DOCKER_COMPOSE} up --build

.PHONY: bg
bg:
	${DOCKER_COMPOSE} up --build -d

.PHONY: routes
routes:
	${DOCKER_COMPOSE} run ${RESOURCES_CONTAINER} ${FLASK} routes

.PHONY: test
test:
	${DOCKER_COMPOSE} run ${RESOURCES_CONTAINER} pytest --cov=app tests/

.PHONY: lint
lint:
	${DOCKER_COMPOSE} run ${RESOURCES_CONTAINER} flake8 src/app --statistics --count

.PHONY: help
help: build
	${DOCKER_COMPOSE} run ${RESOURCES_CONTAINER} ${FLASK} --help

.PHONY: build
build:
	${DOCKER_COMPOSE} build --pull ${RESOURCES_CONTAINER}

.PHONY: setup
setup: build
	${DOCKER_COMPOSE} run ${RESOURCES_CONTAINER} ${FLASK} db-migrate create-tables
	${DOCKER_COMPOSE} run ${RESOURCES_CONTAINER} ${FLASK} db stamp head
	${DOCKER_COMPOSE} run ${RESOURCES_CONTAINER} ${FLASK} db-migrate init
