.PHONY: setup lint format test clean install-hooks docs docs-serve docs-stop isort flake8 mypy quality quality-basic lint-format test-cov update-hooks pre-commit-all

# Default goal
.DEFAULT_GOAL := help

# Docker Compose service and shell prefix
DC_SERVICE=sdk
DC_RUN=docker compose run --rm $(DC_SERVICE)

# Install poetry dependencies (inside container)
setup:
	$(DC_RUN) poetry install
	$(DC_RUN) poetry run pre-commit install

# Run isort to sort imports
isort:
	$(DC_RUN) poetry run isort scm tests

# Run linting with ruff
lint:
	$(DC_RUN) poetry run ruff check scm tests

# Run linting with flake8
flake8:
	$(DC_RUN) poetry run flake8 scm tests

# Run type checking with mypy
mypy:
	$(DC_RUN) poetry run mypy --config-file mypy.ini scm tests

# Run formatting with ruff
format:
	$(DC_RUN) poetry run ruff check --select D --fix scm tests

# Check and auto-fix with ruff
fix:
	$(DC_RUN) poetry run ruff check --fix scm tests

# Run all code quality checks
quality: isort fix format lint flake8 mypy
	@echo "All code quality checks complete!"

# Run basic code quality checks (skip mypy)
quality-basic: isort fix lint flake8 format
	@echo "Basic code quality checks complete!"

# Run both linting and formatting
lint-format: lint format

# Run tests
test:
	$(DC_RUN) poetry run pytest

# Run tests with coverage
test-cov:
	$(DC_RUN) poetry run pytest -m "not api" --cov=scm --cov-report=xml --cov-report=term-missing tests/

# Clean caches (runs locally)
clean:
	@echo "Cleaning cache directories..."
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +

# Install pre-commit hooks
install-hooks:
	$(DC_RUN) poetry run pre-commit install

# Update all hooks to the latest version
update-hooks:
	$(DC_RUN) poetry run pre-commit autoupdate

# Run pre-commit on all files
pre-commit-all:
	$(DC_RUN) poetry run pre-commit run --all-files

# Build documentation
docs:
	$(DC_RUN) poetry run mkdocs build --strict --no-directory-urls

# Serve documentation locally
docs-serve:
	docker compose up -d docs
	@echo "Documentation server started. Access at http://localhost:8000/pan-scm-sdk/"
	@echo "To stop the server, run: make docs-stop"

# Stop documentation server
docs-stop:
	docker compose stop docs
	@echo "Documentation server stopped."

help:
	@echo "Available commands:"
	@echo "  setup           - Install dependencies and pre-commit hooks (in Docker)"
	@echo "  isort           - Sort imports with isort (in Docker)"
	@echo "  lint            - Run linting checks with ruff (in Docker)"
	@echo "  flake8          - Run linting checks with flake8 (in Docker)"
	@echo "  mypy            - Run type checking with mypy (in Docker)"
	@echo "  format          - Format code with ruff (in Docker)"
	@echo "  fix             - Auto-fix linting issues with ruff (in Docker)"
	@echo "  quality         - Run all code quality checks (in Docker)"
	@echo "  quality-basic   - Run basic code quality checks (in Docker)"
	@echo "  lint-format     - Run both linting and formatting (in Docker)"
	@echo "  test            - Run tests (in Docker)"
	@echo "  test-cov        - Run tests with coverage (in Docker)"
	@echo "  clean           - Clean cache directories (local)"
	@echo "  docs            - Build documentation site (in Docker)"
	@echo "  docs-serve      - Serve documentation locally on http://localhost:8000/pan-scm-sdk/ (using dedicated docs service)"
	@echo "  docs-stop       - Stop the documentation server"
	@echo "  install-hooks   - Install pre-commit hooks (in Docker)"
	@echo "  update-hooks    - Update pre-commit hooks to the latest versions (in Docker)"
	@echo "  pre-commit-all  - Run pre-commit on all files (in Docker)"
