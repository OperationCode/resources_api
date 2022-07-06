DOCKER := docker
DOCKER_COMPOSE := docker-compose
COMPOSE_FILE := docker-compose.yml
RESOURCES_CONTAINER := resources-api
RESOURCES_DB := resources-postgres
FLASK := flask
ARGS = $(filter-out $@,$(MAKECMDGOALS))

.PHONY: all

ifeq ($(OS),Windows_NT)
all: run_windows
else
all: run
endif

.PHONY:  shell
shell:
	${DOCKER_COMPOSE} -f ${COMPOSE_FILE} run ${RESOURCES_CONTAINER} ${FLASK} shell
	
.PHONY:  nuke
nuke:
	${DOCKER} system prune -a --volumes

.PHONY: minty-fresh
minty-fresh:
	${DOCKER_COMPOSE} -f ${COMPOSE_FILE} down --rmi all --volumes --remove-orphans

add remove:
	@if [ -z $(shell echo ${ARGS} | cut -d' ' -f1) ]; then echo "Please provide a proper package name"; exit 1; fi
	if [ ! "$$(${DOCKER} ps -q -f name=resources-api)" ]; then ${DOCKER_COMPOSE} -f ${COMPOSE_FILE} up --build -d; fi
	${DOCKER} exec ${RESOURCES_CONTAINER} /bin/bash -c "poetry $@ $(shell echo ${ARGS} | cut -d' ' -f1)"
%:
	@:

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
	if [ "$$(${DOCKER} ps -q -f name=resources-api)" ]; then ${DOCKER_COMPOSE} -f ${COMPOSE_FILE} down; fi
	${DOCKER_COMPOSE} -f ${COMPOSE_FILE} run -p 5000:5000 ${RESOURCES_CONTAINER}

.PHONY: run
run: build
	if [ "$$(${DOCKER} ps -q -f name=resources-api)" ]; then ${DOCKER_COMPOSE} -f ${COMPOSE_FILE} down; fi
	${DOCKER_COMPOSE} -f ${COMPOSE_FILE} run -p 5000:5000 ${RESOURCES_CONTAINER} ${FLASK} run -h 0.0.0.0

run_windows: build
	@cmd /c (IF NOT "$(shell ${DOCKER} ps -q -f name=resources-api)" == "" ${DOCKER_COMPOSE} -f ${COMPOSE_FILE} down)
	${DOCKER_COMPOSE} -f ${COMPOSE_FILE} run -p 5000:5000 ${RESOURCES_CONTAINER} ${FLASK} run -h 0.0.0.0


.PHONY: bg
bg:
	${DOCKER_COMPOSE} -f ${COMPOSE_FILE} up --build -d

.PHONY: routes
routes:
	${DOCKER_COMPOSE} -f ${COMPOSE_FILE} run ${RESOURCES_CONTAINER} ${FLASK} routes

.PHONY: test
test: build
	${DOCKER_COMPOSE} -f ${COMPOSE_FILE} run ${RESOURCES_CONTAINER} py.test --cov=app/ tests/

.PHONY: test-coverage
test-coverage:
	${DOCKER_COMPOSE} -f ${COMPOSE_FILE} run ${RESOURCES_CONTAINER} py.test --cov-report html --cov=app/ tests/

.PHONY: test-coverage-ci
test-coverage-ci:
	${DOCKER_COMPOSE} -f ${COMPOSE_FILE} run --name coverage_test_run ${RESOURCES_CONTAINER} \
	/bin/bash -c "py.test --cov=app/ tests/ && coverage xml"
	docker cp coverage_test_run:/src/coverage.xml coverage.xml

# Usage: make test-single tests/unit/test_api_key.py::test_get_api_key
.PHONY: test-single
test-single: build
	${DOCKER_COMPOSE} -f ${COMPOSE_FILE} run ${RESOURCES_CONTAINER} /bin/bash -c "py.test --cov=app/ $(shell echo ${ARGS})"

.PHONY: lint
lint:
	${DOCKER_COMPOSE} -f ${COMPOSE_FILE} run ${RESOURCES_CONTAINER} flake8 . --exclude migrations --statistics --count

.PHONY: bandit
bandit:
	${DOCKER_COMPOSE} -f ${COMPOSE_FILE} run ${RESOURCES_CONTAINER} bandit -r .

.PHONY: help
help: build
	${DOCKER_COMPOSE} -f ${COMPOSE_FILE} run ${RESOURCES_CONTAINER} ${FLASK} --help

.PHONY: build
build:
	${DOCKER_COMPOSE} -f ${COMPOSE_FILE} build --pull ${RESOURCES_CONTAINER}

.PHONY: setup
setup: bg
	${DOCKER_COMPOSE} -f ${COMPOSE_FILE} run ${RESOURCES_CONTAINER} ${FLASK}
	${DOCKER_COMPOSE} -f ${COMPOSE_FILE} run ${RESOURCES_CONTAINER} ${FLASK} db-migrate create-tables
	${DOCKER_COMPOSE} -f ${COMPOSE_FILE} run ${RESOURCES_CONTAINER} ${FLASK} db stamp head
	${DOCKER_COMPOSE} -f ${COMPOSE_FILE} run ${RESOURCES_CONTAINER} ${FLASK} db-migrate init

.PHONY: migrate
migrate: build
	${DOCKER_COMPOSE} -f ${COMPOSE_FILE} run ${RESOURCES_CONTAINER} ${FLASK} db migrate
	${DOCKER_COMPOSE} -f ${COMPOSE_FILE} run ${RESOURCES_CONTAINER} ${FLASK} db upgrade

.PHONY: reindex
reindex:
	${DOCKER_COMPOSE} -f ${COMPOSE_FILE} run ${RESOURCES_CONTAINER} ${FLASK} algolia reindex

.PHONY: bad-urls
bad-urls:
	${DOCKER_COMPOSE} -f ${COMPOSE_FILE} run ${RESOURCES_CONTAINER} ${FLASK} check-bad-urls
