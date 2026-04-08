PYTHON ?= python3

.PHONY: install dev lint test api compose-up compose-down cli-help ci staging-config staging-up staging-check staging-down

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e '.[dev]'

dev:
	uvicorn synapse.server:app --reload

lint:
	ruff check .

test:
	pytest

ci:
	ruff check .
	pytest
	cp .env.example .env
	cp deploy/.env.staging.example deploy/.env.staging
	docker compose config >/dev/null
	docker compose --env-file deploy/.env.staging -f deploy/docker-compose.staging.yml config >/dev/null

api:
	uvicorn synapse.server:app --host 0.0.0.0 --port 8000 --reload

compose-up:
	docker compose up -d postgres redis minio

compose-down:
	docker compose down

cli-help:
	synapse --help

staging-config:
	cp -n deploy/.env.staging.example deploy/.env.staging || true
	docker compose --env-file deploy/.env.staging -f deploy/docker-compose.staging.yml config

staging-up:
	./scripts/deploy_staging.sh

staging-check:
	./scripts/check_staging.sh

staging-down:
	docker compose --env-file deploy/.env.staging -f deploy/docker-compose.staging.yml down
