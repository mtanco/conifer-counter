all: setup ## Install dependencies

setup: ## Install dependencies
	python3.6 -m venv venv
	./venv/bin/python -m pip install --upgrade pip
	./venv/bin/python -m pip install -r requirements.txt

run: ## Run the app with no reload
	./venv/bin/wave run --no-reload src/app.py

dev: ## Run the app with active reload
	./venv/bin/wave run src/app.py

.PHONY: format
format:
	./venv/bin/isort .
	./venv/bin/black --exclude venv .