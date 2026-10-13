.PHONY: install run test lint docker
install:
	python -m venv .venv && .venv/bin/pip install -r requirements.txt -r requirements-dev.txt || .venv\\Scripts\\pip install -r requirements.txt -r requirements-dev.txt
run:
	uvicorn backend.main:app --reload --port 8000
test:
	pytest -q
lint:
	ruff check backend tests
docker:
	docker compose up --build
