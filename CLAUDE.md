# CLAUDE.md - Strata Cloud Manager SDK

## Build & Test Commands
- **Install**: `poetry install`
- **Build**: `poetry build`
- **Lint**: `poetry run flake8`
- **Format**: `poetry run black scm tests`
- **Run all tests**: `poetry run pytest`
- **Run single test**: `poetry run pytest tests/path/to/test_file.py::TestClass::test_method`
- **Run specific test module**: `poetry run pytest tests/scm/config/objects/test_address.py`
- **Run API integration tests**: `poetry run pytest -m api`
- **Run with coverage**: `poetry run pytest --cov=scm tests/`

## Code Style Guidelines
- **Python Version**: 3.10+ required
- **Imports**: standard lib → external libs → local imports (grouped & alphabetized)
- **Naming**: snake_case for variables/functions, PascalCase for classes, UPPER_CASE for constants
- **Type Hints**: Required for all parameters, return values, and class attributes
- **Error Handling**: Use custom exceptions (APIError hierarchy), exception chaining with `raise ... from e`
- **Documentation**: Docstrings for all public methods with Args/Returns/Raises sections
- **Formatting**: Line length of 100 characters (E501 ignored), use Black formatter
- **Data Validation**: Use Pydantic models for request/response validation
- **Testing**: Unit tests required, mock external dependencies