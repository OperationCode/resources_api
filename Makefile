DOCKER := docker
DOCKER_COMPOSE := docker-compose
RESOURCES_CONTAINER := resources

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

.PHONY: test
test:
	${DOCKER_COMPOSE} run ${RESOURCES_CONTAINER} -m pytest --cov=app tests/

.PHONY: lint
lint:
	${DOCKER_COMPOSE} run ${RESOURCES_CONTAINER} -m flake8 src/app --statistics --count

.PHONY: build
build:
	${DOCKER_COMPOSE} build

.PHONY: setup
setup: build
	${DOCKER_COMPOSE} run ${RESOURCES_CONTAINER} -m flask db-migrate create-tables
	${DOCKER_COMPOSE} run ${RESOURCES_CONTAINER} -m flask db stamp head
	${DOCKER_COMPOSE} run ${RESOURCES_CONTAINER} -m flask db-migrate init

