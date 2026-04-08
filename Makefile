PYTHON ?= python3

.PHONY: install dev lint test api compose-up compose-down cli-help

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e '.[dev]'

dev:
	uvicorn synapse.server:app --reload

lint:
	ruff check .

test:
	pytest

api:
	uvicorn synapse.server:app --host 0.0.0.0 --port 8000 --reload

compose-up:
	docker compose up -d postgres redis minio

compose-down:
	docker compose down

cli-help:
	synapse --help
