PYTHON ?= python3.12

.PHONY: setup setup-voice init-db reset-db api chat audiosocket test lint docker-up docker-down

setup:
	$(PYTHON) -m venv .venv
	.venv/bin/pip install -U pip
	.venv/bin/pip install -e ".[dev]"

setup-voice:
	.venv/bin/pip install -e ".[dev,voice]"

init-db:
	.venv/bin/voiceclinic init-db

reset-db:
	.venv/bin/voiceclinic reset-db

api:
	.venv/bin/voiceclinic api --host 127.0.0.1 --port 8000

chat:
	.venv/bin/voiceclinic chat

audiosocket:
	.venv/bin/voiceclinic audiosocket

test:
	.venv/bin/pytest

lint:
	.venv/bin/ruff check src tests

docker-up:
	docker compose up --build

docker-down:
	docker compose down
