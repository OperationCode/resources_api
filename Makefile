DOCKER := docker
DOCKER_COMPOSE := docker-compose
RESOURCES_CONTAINER := resources-api
RESOURCES_DB := resources-postgres
FLASK := flask

.PHONY: all
all: run

.PHONY:  nuke
nuke:
	${DOCKER} system prune -a --volumes

.PHONY: minty-fresh
minty-fresh:
	${DOCKER_COMPOSE} down --rmi all --volumes --remove-orphans

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
fresh-restart: minty-fresh test setup run

.PHONY: run-with-metrics
run-with-metrics: build
	if [ "$$(${DOCKER} ps -q -f name=resources-api)" ]; then ${DOCKER_COMPOSE} down; fi
	${DOCKER_COMPOSE} run -p 5000:5000 ${RESOURCES_CONTAINER}

.PHONY: run
run: build
	if [ "$$(${DOCKER} ps -q -f name=resources-api)" ]; then ${DOCKER_COMPOSE} down; fi
	${DOCKER_COMPOSE} run -p 5000:5000 ${RESOURCES_CONTAINER} ${FLASK} run -h 0.0.0.0

.PHONY: bg
bg:
	${DOCKER_COMPOSE} up --build -d

.PHONY: routes
routes:
	${DOCKER_COMPOSE} run ${RESOURCES_CONTAINER} ${FLASK} routes

.PHONY: test
test: build
	${DOCKER_COMPOSE} run ${RESOURCES_CONTAINER} py.test --cov=app/ tests/

.PHONY: test-coverage
test-coverage:
	${DOCKER_COMPOSE} run ${RESOURCES_CONTAINER} py.test --cov-report html --cov=app/ tests/

.PHONY: lint
lint:
	${DOCKER_COMPOSE} run ${RESOURCES_CONTAINER} flake8 . --exclude migrations,tests --statistics --count

.PHONY: bandit
bandit:
	${DOCKER_COMPOSE} run ${RESOURCES_CONTAINER} bandit -r .

.PHONY: help
help: build
	${DOCKER_COMPOSE} run ${RESOURCES_CONTAINER} ${FLASK} --help

.PHONY: build
build:
	${DOCKER_COMPOSE} build --pull ${RESOURCES_CONTAINER}

.PHONY: setup
setup: bg
	${DOCKER_COMPOSE} run ${RESOURCES_CONTAINER} ${FLASK}
	${DOCKER_COMPOSE} run ${RESOURCES_CONTAINER} ${FLASK} db-migrate create-tables
	${DOCKER_COMPOSE} run ${RESOURCES_CONTAINER} ${FLASK} db stamp head
	${DOCKER_COMPOSE} run ${RESOURCES_CONTAINER} ${FLASK} db-migrate init

.PHONY: migrate
migrate: build
	${DOCKER_COMPOSE} run ${RESOURCES_CONTAINER} ${FLASK} db migrate
	${DOCKER_COMPOSE} run ${RESOURCES_CONTAINER} ${FLASK} db upgrade

.PHONY: reindex
reindex: 
	${DOCKER_COMPOSE} run ${RESOURCES_CONTAINER} ${FLASK} algolia reindex
