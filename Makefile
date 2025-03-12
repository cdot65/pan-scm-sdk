.PHONY: setup lint format test clean install-hooks

# Default goal
.DEFAULT_GOAL := help

# Install poetry dependencies
setup:
	@echo "Installing dependencies..."
	poetry install
	@echo "Installing pre-commit hooks..."
	poetry run pre-commit install

# Run linting with ruff
lint:
	@echo "Running linting checks..."
	poetry run ruff check scm tests

# Run formatting with ruff
format:
	@echo "Running code formatter..."
	poetry run ruff format scm tests

# Check and auto-fix with ruff
fix:
	@echo "Auto-fixing linting issues..."
	poetry run ruff check --fix scm tests

# Run both linting and formatting
lint-format: lint format

# Run tests
test:
	@echo "Running tests..."
	poetry run pytest

# Run tests with coverage
test-cov:
	@echo "Running tests with coverage..."
	poetry run pytest --cov=scm tests/

# Clean caches
clean:
	@echo "Cleaning cache directories..."
	rm -rf .pytest_cache
	rm -rf .ruff_cache
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

help:
	@echo "Available commands:"
	@echo "  setup           - Install dependencies and pre-commit hooks"
	@echo "  lint            - Run linting checks with ruff"
	@echo "  format          - Format code with ruff"
	@echo "  fix             - Auto-fix linting issues with ruff"
	@echo "  lint-format     - Run both linting and formatting"
	@echo "  test            - Run tests"
	@echo "  test-cov        - Run tests with coverage"
	@echo "  clean           - Clean cache directories"
	@echo "  install-hooks   - Install pre-commit hooks"
	@echo "  update-hooks    - Update pre-commit hooks to the latest versions"
	@echo "  pre-commit-all  - Run pre-commit on all files"
