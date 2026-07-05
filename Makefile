.PHONY: install dev test lint run

install:
	pip install -e ".[dev]"

test:
	pytest -q

lint:
	ruff check src tests

run:
	uvicorn medreception.main:app --reload --app-dir src
