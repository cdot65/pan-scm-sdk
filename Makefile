.PHONY: setup lint format test clean install-hooks docs docs-serve isort flake8 mypy quality quality-basic

# Default goal
.DEFAULT_GOAL := help

# Install poetry dependencies
setup:
	@echo "Installing dependencies..."
	poetry install
	@echo "Installing pre-commit hooks..."
	poetry run pre-commit install

# Run isort to sort imports
isort:
	@echo "Running isort to sort imports..."
	poetry run isort scm tests

# Run linting with ruff
lint:
	@echo "Running linting checks with ruff..."
	poetry run ruff check scm tests

# Run linting with flake8
flake8:
	@echo "Running linting checks with flake8..."
	poetry run flake8 scm tests

# Run type checking with mypy
mypy:
	@echo "Running type checking with mypy..."
	poetry run mypy --config-file mypy.ini scm tests

# Run formatting with ruff
format:
	@echo "Running code formatter with ruff..."
	poetry run ruff format scm tests

# Check and auto-fix with ruff
fix:
	@echo "Auto-fixing linting issues with ruff..."
	poetry run ruff check --fix scm tests

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
	@echo "Running tests..."
	poetry run pytest

# Run tests with coverage
test-cov:
	@echo "Running tests with coverage..."
	poetry run pytest -m "not api" --cov=scm --cov-report=xml --cov-report=term-missing tests/

# Clean caches
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
	@echo "Installing pre-commit hooks..."
	poetry run pre-commit install

# Update all hooks to the latest version
update-hooks:
	@echo "Updating pre-commit hooks..."
	poetry run pre-commit autoupdate

# Run pre-commit on all files
pre-commit-all:
	@echo "Running pre-commit on all files..."
	poetry run pre-commit run --all-files

# Build documentation
docs:
	@echo "Building documentation site..."
	poetry run mkdocs build --strict --no-directory-urls

# Serve documentation locally
docs-serve:
	@echo "Starting documentation server..."
	poetry run mkdocs serve

help:
	@echo "Available commands:"
	@echo "  setup           - Install dependencies and pre-commit hooks"
	@echo "  isort           - Sort imports with isort"
	@echo "  lint            - Run linting checks with ruff"
	@echo "  flake8          - Run linting checks with flake8"
	@echo "  mypy            - Run type checking with mypy"
	@echo "  format          - Format code with ruff"
	@echo "  fix             - Auto-fix linting issues with ruff"
	@echo "  quality         - Run all code quality checks (lint, flake8, mypy, format)"
	@echo "  quality-basic   - Run basic code quality checks (lint, flake8, format)"
	@echo "  lint-format     - Run both linting and formatting"
	@echo "  test            - Run tests"
	@echo "  test-cov        - Run tests with coverage"
	@echo "  clean           - Clean cache directories"
	@echo "  docs            - Build documentation site (with strict validation)"
	@echo "  docs-serve      - Serve documentation locally for development"
	@echo "  install-hooks   - Install pre-commit hooks"
	@echo "  update-hooks    - Update pre-commit hooks to the latest versions"
	@echo "  pre-commit-all  - Run pre-commit on all files"
