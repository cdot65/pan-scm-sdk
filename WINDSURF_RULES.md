# WINDSURF RULES

## Project Overview

This project is the `pan-scm-sdk` Python SDK, providing programmatic access to Palo Alto Networks' Strata Cloud Manager (SCM) REST API. It is designed for use as a standalone SDK and as the core of the `cdot65.scm` Ansible Collection. All development follows strict architectural, coding, and workflow standards as outlined below.

---

## Directory & Package Structure

- Core SDK logic: `scm/`
  - `client.py`, `auth.py`, `exceptions.py`, `base_object.py`
  - `config/` for service/resource classes (by category)
  - `models/` for Pydantic models (by resource category)
- Tests: `tests/`, mirroring `scm/`
- Documentation: `docs/`
- Usage examples: `examples/`, mirroring `scm/` where applicable
- Dependency management: `pyproject.toml` (Poetry)

---

## Coding Standards

- **Linting/Formatting:** Use `ruff` (configured in `pyproject.toml`) for linting and formatting. Run with `poetry run ruff check --fix` and `poetry run ruff format`.
- **PEP 8:** Strictly enforced.
  - `snake_case` for functions, methods, variables
  - `PascalCase` for classes
  - `UPPER_CASE` for constants
- **Line Length:** 88 characters (ruff default)
- **Imports:** Use ruff's isort; prefer absolute imports within `scm`
- **Type Hints:** Python 3.10+ for all function/method parameters and return values
- **Typing:** Use `Optional`, `List`, `Dict`, `Any`, `Union`, `Literal`, `Type` from `typing`
- **Pydantic:** Use Pydantic V2+ for models/validation
- **BaseObject:** All resource service classes inherit from `BaseObject`
- **Standard Methods:** Implement `create`, `get`, `fetch`, `list`, `update`, `delete` for resources
- **Container Handling:** Validate container args; ensure exactly one is used when required
- **Pagination:** Auto-pagination in `list` methods using `max_limit`
- **Filtering:** Support both API-level and client-side filtering
- **Modularity:** Encapsulate logic per resource/service/model
- **Model Structure:** For each resource, define `CreateModel`, `UpdateModel`, `ResponseModel`, and a `BaseModel` for shared fields
- **Validation:** Use `Field` for basic, custom validators for complex rules
- **Serialization:** Use `.model_dump(exclude_unset=True)` for API payloads
- **Model Organization:** Place models in dedicated files within `scm/models/` by category

---

## SDK Service File Standards

All SDK service files (e.g., `scm/config/objects/address.py`) must follow these conventions:

- **File/Class Structure**
  - One main service class per file, named after the resource (PascalCase, singular).
  - Header docstring: Google-style, describing the file and resource.
  - Imports: Standard library first, then SDK modules (absolute), then models/exceptions.
  - Class-level constants: ENDPOINT, DEFAULT_MAX_LIMIT, ABSOLUTE_MAX_LIMIT.
  - Constructor: Accepts api_client, max_limit; sets up logger and validates limit.
  - max_limit property: With getter/setter, both documented.
  - Private _validate_max_limit method: Validates input, raises InvalidObjectError.
  - CRUD methods: At minimum, create, get, update, all returning a Pydantic ResponseModel.
  - Static _apply_filters method: For client-side filtering, with type hints and docstrings.

- **Naming & Typing**
  - snake_case for methods, PascalCase for classes/models, UPPER_CASE for constants.
  - Type hints for all parameters and return values (Python 3.10+).
  - Pydantic V2+ models for all resource data.

- **Docstrings & Comments**
  - Google-style docstrings for all public classes and methods.
  - Inline comments for clarity, especially for validation and API workflows.

- **Formatting & Linting**
  - Line length: 88 characters (ruff default).
  - Blank lines between class-level constants, methods, and logical blocks.
  - Ruff for linting/formatting, isort for imports.
  - Absolute imports for all SDK-internal modules.

- **Logic & Workflow**
  - Input validation: All user inputs (esp. limits, enums) are validated, with custom exceptions raised.
  - Model-driven: All data validated/serialized via Pydantic models.
  - API calls: Always via self.api_client, with endpoint and params explicit.
  - Error handling: Always uses SDK custom exceptions, detailed error codes/messages.

- **Special Behaviors**
  - Boolean field handling: Only include True values in payloads for SCM API (omit False).
  - Serialization: Always use .model_dump(exclude_unset=True) for API payloads.

- **Reference:** See `sdk_service_file_styling.md` for detailed examples and rationale.

---

## HTTP & Auth

- Use `requests` for HTTP, `requests_oauthlib` for OAuth2
- OAuth2 Client Credentials in `auth.py`
- Robust token refresh in `OAuth2Client` and `Scm` client
- Centralize API calls in `Scm` client (`_get`, `_post`, etc.)
- Support custom `token_url` and `base_url` on client init

---

## Error Handling

- Custom exception hierarchy rooted in `APIError` (`scm/exceptions.py`)
- Raise specific exceptions (e.g., `ObjectNotPresentError`, `NameNotUniqueError`)
- Use `ErrorHandler` to map HTTP status/API errors to exceptions
- Exceptions must include `message`, `error_code`, `http_status_code`, `details`
- Use `try...except` in examples and high-level SDK methods

---

## Testing

- Use `pytest` for all tests
- >80% code coverage (`coverage.py`, Codecov)
- Unit tests for:
  - Pydantic model validation
  - Auth logic (mock external calls)
  - Client methods (mock `requests`)
  - `BaseObject` & resource service methods
  - `ErrorHandler` logic
- Integration tests for key API interactions (mocking, VCR/cassettes, or test tenant)
- Use `pytest` fixtures for setup

---

## Documentation

- Google-style docstrings for all public classes, methods, and functions
- Generate API docs with MkDocs and `mkdocstrings`
- Maintain user docs: README, Installation, Getting Started, Troubleshooting, Release Notes
- Dedicated pages for each service/model
- Runnable examples in `examples/` and snippets in docs
- Deploy docs via GitHub Pages

---

## Dependency Management

- Use Poetry for all dependencies, locking, and packaging
- All project metadata, dependencies, and tool configs in `pyproject.toml`
- Pin direct dependencies; use `poetry.lock` for transitive
- Minimize external dependencies

---

## Release & Workflow

- Build and publish with Poetry (to PyPI)
- Use Git with Feature Branch workflow
- Require PRs for merging to `main`, with reviews
- Enforce pre-commit hooks (ruff format/check) before commit
- Use GitHub Actions for CI/CD: test, lint, coverage, docs, PyPI
- Semantic Versioning (SemVer)
- Maintain `CHANGELOG.md` or `release-notes.md`

---

## Makefile Functionality

The following developer workflows are provided by the Makefile (all commands are run with `poetry run` to ensure the Poetry virtualenv is used):

- **SDK Build & Install**
  - `make build`: Build the SDK package (if applicable)
  - `make install`: Install the SDK package locally
  - `make clean`: Remove build artifacts

- **Linting & Formatting**
  - `make lint`: Run `ruff` and `isort`
  - `make format`: Run `ruff format` and `isort` on all code

- **Testing**
  - `make test`: Run all tests (unit + integration)
  - `make unit-test`: Run unit tests
  - `make integration-test`: Run integration tests

- **Development Setup**
  - `make dev-setup`: Install Poetry dependencies and any test requirements

- **Example Run**
  - `make example`: Run sample usage scripts from `examples/`

**Note:** Always use `poetry run` for all build, lint, format, and test commands to ensure the virtual environment is active.

---

If you want this file named differently or want to include/exclude any section, let the maintainers know!
