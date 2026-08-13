VENV=backend/.venv
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip
CELERY=$(VENV)/bin/celery

.PHONY: venv install api worker beat up down build logs shell clean

venv:
	python3 -m venv $(VENV)

install: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r backend/requirements.txt

api:
	cd backend && ../$(PYTHON) run.py

worker:
	cd backend && ../$(CELERY) -A celery_worker.celery worker --loglevel=info

beat:
	cd backend && ../$(CELERY) -A celery_worker.celery beat --loglevel=info

build:
	docker compose build

up:
	docker compose up

up-d:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

logs-api:
	docker compose logs -f api

logs-worker:
	docker compose logs -f worker

shell:
	docker compose exec api /bin/bash

clean:
	docker compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; true
