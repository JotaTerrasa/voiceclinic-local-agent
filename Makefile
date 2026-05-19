PYTHON ?= python3

.PHONY: copy-env setup setup-voice setup-orchestration setup-livekit setup-all init-db reset-db api chat audiosocket test lint docker-up docker-down

copy-env:
	$(PYTHON) scripts/dev.py copy-env

setup:
	$(PYTHON) scripts/dev.py setup

setup-voice:
	$(PYTHON) scripts/dev.py setup-voice

setup-orchestration:
	$(PYTHON) scripts/dev.py setup-orchestration

setup-livekit:
	$(PYTHON) scripts/dev.py setup-livekit

setup-all:
	$(PYTHON) scripts/dev.py setup-all

init-db:
	$(PYTHON) scripts/dev.py init-db

reset-db:
	$(PYTHON) scripts/dev.py reset-db

api:
	$(PYTHON) scripts/dev.py api --host 127.0.0.1 --port 8000

chat:
	$(PYTHON) scripts/dev.py chat

audiosocket:
	$(PYTHON) scripts/dev.py audiosocket

test:
	$(PYTHON) scripts/dev.py test

lint:
	$(PYTHON) scripts/dev.py lint

docker-up:
	$(PYTHON) scripts/dev.py docker-up

docker-down:
	$(PYTHON) scripts/dev.py docker-down
