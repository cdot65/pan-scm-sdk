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

All SDK service files (e.g., `scm/config/objects/address.py`) must strictly adhere to the following standards, which are harmonized from `CLAUDE.md`, `SDK_SERVICE_TEMPLATE.py`, `SDK_STYLING_GUIDE.md`, and `CLAUDE_MODELS.md`. These rules supersede any previous conventions and are enforced for all new and existing SDK service code.

- **File & Module Structure**
  - One main service class per file, named after the resource (PascalCase, singular).
  - **Module docstring**: Google-style, describing the service and resource.
  - **File header comment**: Include the source file path as the first line after the docstring.
  - **Imports**: Standard library first, then SDK modules (absolute imports only), then models/exceptions.
  - **Class-level constants**: `ENDPOINT`, `DEFAULT_MAX_LIMIT`, `ABSOLUTE_MAX_LIMIT` (with comments on API limits).
  - **Constructor**: Accepts `api_client`, `max_limit`; sets up logger, validates limit, and follows the template pattern.
  - **max_limit property**: With getter/setter, both documented with Google-style docstrings.
  - **Private `_validate_max_limit` method**: Validates input, raises `InvalidObjectError` with detailed error code, status, and details.
  - **CRUD methods**: At minimum, `create`, `get`, `update`, all returning a Pydantic `ResponseModel`, and following the exact signature and docstring patterns from the template and guides.
  - **Static `_apply_filters` method**: For client-side filtering, with full type hints and docstrings.
  - **Standard helper methods**: e.g., `_build_container_params`, as per template.

- **Naming & Typing**
  - `snake_case` for all methods, properties, variables.
  - `PascalCase` for all classes and Pydantic models.
  - `UPPER_CASE` for constants.
  - Type hints for all parameters and return values (Python 3.10+ syntax required).
  - All resource data must use Pydantic V2+ models (`CreateModel`, `UpdateModel`, `ResponseModel`).

- **Docstrings & Comments**
  - Google-style docstrings are required for all public classes and methods, including Args, Returns, and Raises sections.
  - Inline comments must be used for clarity, especially around validation, API workflows, and any SCM API-specific behaviors (such as boolean handling).
  - All method docstrings must be specific about types and expected values.

- **Formatting & Linting**
  - Line length: 88 characters (ruff default; see `pyproject.toml`).
  - Blank lines between class-level constants, methods, and logical blocks.
  - Use `ruff` and `isort` for linting and formatting (see Makefile and style guide).
  - Only absolute imports for SDK-internal modules.
  - Double quotes for strings (unless otherwise required by project-wide style guide).

- **Logic & Workflow**
  - All user input (especially limits, enums, containers) must be validated, with custom exceptions (`InvalidObjectError`, `MissingQueryParameterError`, etc.) raised as appropriate.
  - All data must be validated and serialized via Pydantic models, using `.model_dump(exclude_unset=True)` for payloads.
  - All API calls must be made via `self.api_client`, with endpoint and params explicit and clear.
  - All error handling must use SDK custom exceptions, with detailed error codes, HTTP status, and context in the `details` dictionary.
  - Pagination logic must use `max_limit`, `offset`, and process all pages as per the canonical pattern in the template.

- **Special Behaviors & SCM API Requirements**
  - Boolean field handling: Only include `True` values in API payloads; omit `False` (per SCM API requirements).
  - Serialization: Always use `.model_dump(exclude_unset=True)` for all API payloads.
  - Container argument validation: For `folder`, `snippet`, `device`, ensure exactly one is used when required, and raise if ambiguous.
  - Resource-specific validations: Enforce string length, regex, enum, and container exclusivity as required by the resource and API.
  - Security and deployment services may require extra parameters (e.g., `rulebase`) or have different pagination logic (see template).

- **Error Handling Patterns**
  - All parameter validation and API response errors must raise custom SDK exceptions, with full context.
  - See `CLAUDE.md` and `SDK_SERVICE_TEMPLATE.py` for canonical error handling code snippets.

- **Pagination Pattern**
  - Use the standard pagination loop with `limit`, `offset`, and breaking when the returned data length is less than the limit.

- **Reference & Templates**
  - For full, up-to-date examples and rationale, see:
    - `sdk_service_file_styling.md`
    - `SDK_SERVICE_TEMPLATE.py`
    - `SDK_STYLING_GUIDE.md`
    - `CLAUDE_MODELS.md`
    - `CLAUDE.md` (AI/codegen guidance)

These standards are strictly enforced for all SDK service files. If you have questions or need clarification, consult the above guides or contact the maintainers.

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
