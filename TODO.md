# Strata Cloud Manager SDK - Build TODO List

This list outlines the steps required to build the SCM SDK according to the Product Requirements Document (PRD).

## I. Project Setup & Foundation

- [ ] Initialize Git repository.
- [ ] Set up project structure (directories for `scm`, `tests`, `docs`, `examples`).
- [ ] Initialize Python project using Poetry (`poetry init`).
- [ ] Configure `pyproject.toml` with basic metadata, dependencies (Python version), and tool configurations (ruff, pytest).
- [ ] Create initial `.gitignore` file.
- [ ] Set up core logging configuration/utility.
- [ ] Define base exception classes (`APIError`, `ClientError`, `ServerError`).

## II. Authentication & Core Client

- [ ] **Authentication (`auth.md`)**
  - [ ] Implement `AuthRequestModel` for credentials.
  - [ ] Implement `OAuth2Client` class.
  - [ ] Add logic for fetching OAuth2 tokens (`requests_oauthlib`).
  - [ ] Implement token validation (expiry check, JWT validation if needed).
  - [ ] Implement automatic token refresh logic.
  - [ ] Implement retry mechanism for token fetching.
  - [ ] Add support for custom `token_url`.
  - [ ] Integrate logging for auth events.
- [ ] **Client (`client.md`)**
  - [ ] Implement `Scm` / `ScmClient` class.
  - [ ] Initialize `requests.Session`.
  - [ ] Instantiate and manage `OAuth2Client`.
  - [ ] Implement base HTTP request methods (`_get`, `_post`, `_put`, `_delete`) integrating auth token handling and refresh.
  - [ ] Implement basic response handling (checking status codes).
  - [ ] Add support for configurable API `base_url`.
  - [ ] Add support for configurable logging level.
- [ ] **Error Handling (`exceptions.md`)**
  - [ ] Define specific exception classes inheriting from base exceptions (e.g., `ObjectNotPresentError`, `NameNotUniqueError`, etc.).
  - [ ] Implement `ErrorResponse` data class.
  - [ ] Implement `ErrorHandler` class to map HTTP status codes and API error codes to specific exceptions.
  - [ ] Integrate `ErrorHandler` into the client's base request methods.

## III. Base Object & Resource Implementation

- [ ] **Base Object (`base_object.md`)**
  - [ ] Implement `BaseObject` class.
  - [ ] Add `api_client` attribute and `ENDPOINT` placeholder.
  - [ ] Implement standard public methods (`create`, `get`, `fetch`, `list`, `update`, `delete`) calling client's private methods.
  - [ ] Implement core pagination logic within the `list` method.
  - [ ] Implement client-side filtering logic (`exact_match`, `exclude_*`) within the `list` method.
  - [ ] Add support for configurable `max_limit` attribute.
- [ ] **Resource Modeling & Implementation (For *each* resource type listed in PRD Section 2.2)**
  - [ ] **Pydantic Models** (e.g., `address_models.md`)
    - [ ] Define `CreateModel` with necessary fields and validators (constraints, patterns, container check).
    - [ ] Define `UpdateModel` including `id` and relevant fields/validators.
    - [ ] Define `ResponseModel` inheriting/including `id` and all response fields.
    - [ ] Define any necessary sub-models (e.g., `GeoLocation`, `ServerModel`, `MatchListItem`).
  - [ ] **Service Class** (e.g., `address.md`)
    - [ ] Create resource-specific class inheriting from `BaseObject` (e.g., `class Address(BaseObject):`).
    - [ ] Define the specific `ENDPOINT`.
    - [ ] Implement/Override methods if specific logic is needed (e.g., custom `list` parameters, specific `fetch` logic).
    - [ ] Add type hints using the defined Pydantic models.
  - [ ] **Unified Client Integration**
    - [ ] Add property/attribute to `Scm` / `ScmClient` to instantiate and return the service class instance (e.g., `@property def address(self): return Address(self)`).
    - [ ] Add `*_max_limit` parameter to client `__init__` for per-resource pagination control.

  - **Resource Checklist:**
    - [ ] Address
    - [ ] Address Group
    - [ ] Application
    - [ ] Application Filter
    - [ ] Application Group
    - [ ] Dynamic User Group
    - [ ] External Dynamic List
    - [ ] HIP Object
    - [ ] HIP Profile
    - [ ] HTTP Server Profile
    - [ ] Log Forwarding Profile
    - [ ] Quarantined Device
    - [ ] Region
    - [ ] Schedule
    - [ ] Service
    - [ ] Service Group
    - [ ] Syslog Server Profile
    - [ ] Tag
    - [ ] IKE Crypto Profile
    - [ ] IKE Gateway
    - [ ] IPsec Crypto Profile
    - [ ] NAT Rule
    - [ ] Security Zone
    - [ ] Authentication Settings (Mobile Agent)
    - [ ] Agent Versions (Mobile Agent)
    - [ ] Bandwidth Allocation
    - [ ] BGP Routing
    - [ ] Internal DNS Servers
    - [ ] Network Location
    - [ ] Remote Network
    - [ ] Service Connection
    - [ ] Security Rule
    - [ ] Anti-Spyware Profile
    - [ ] Decryption Profile
    - [ ] DNS Security Profile
    - [ ] URL Categories
    - [ ] Vulnerability Protection Profile
    - [ ] Wildfire Antivirus Profile

## IV. Configuration Management Implementation

- [ ] **Client Methods (`client.md`)**
  - [ ] Implement `commit` method with support for `folders`, `description`, `admin`, `sync`, `timeout`.
  - [ ] Implement `list_jobs` method with pagination parameters.
  - [ ] Implement `get_job_status` method.
  - [ ] Implement `wait_for_job` method with polling logic and timeout.
  - [ ] Define associated Pydantic models for job/commit responses (`CandidatePushResponseModel`, `JobListResponse`, `JobStatusResponse`).

## V. Quality Assurance

- [ ] **Testing Setup**
  - [ ] Configure `pytest` in `pyproject.toml`.
  - [ ] Set up test structure (`tests/unit`, `tests/integration`).
  - [ ] Implement test fixtures (e.g., mock client, sample data).
- [ ] **Unit Tests**
  - [ ] Write tests for Pydantic model validation (valid/invalid cases).
  - [ ] Write tests for `auth` module logic (mock API calls).
  - [ ] Write tests for `client` module methods (mock API calls).
  - [ ] Write tests for `BaseObject` logic (mock client methods).
  - [ ] Write tests for *each* resource service class (mock client methods).
  - [ ] Write tests for `ErrorHandler` mapping.
  - [ ] Write tests for utility functions.
- [ ] **Integration Tests**
  - [ ] Choose strategy (mock server, VCR/cassettes, live test tenant).
  - [ ] Implement tests for core end-to-end workflows (e.g., auth -> create resource -> commit -> check job).
- [ ] **Code Coverage**
  - [ ] Configure `coverage.py`.
  - [ ] Integrate coverage reporting (e.g., Codecov).
  - [ ] Strive to meet coverage target (>80%).
- [ ] **Code Quality**
  - [ ] Configure `ruff` rules in `pyproject.toml`.
  - [ ] Set up pre-commit hooks (`pre-commit install`).
  - [ ] Ensure all checks pass in CI.
  - [ ] Enforce docstring standards.

## VI. Documentation

- [ ] **Setup**
  - [ ] Initialize MkDocs (`mkdocs new .`).
  - [ ] Choose and configure a theme (e.g., `material`).
  - [ ] Configure `mkdocstrings` for API reference generation.
  - [ ] Set up `mkdocs.yml`.
- [ ] **Content Creation**
  - [ ] Write `README.md`.
  - [ ] Write `docs/about/introduction.md`.
  - [ ] Write `docs/about/installation.md`.
  - [ ] Write `docs/about/getting-started.md`.
  - [ ] Write `docs/sdk/client.md`.
  - [ ] Write `docs/sdk/auth.md`.
  - [ ] Write `docs/sdk/exceptions.md`.
  - [ ] Write `docs/sdk/config/base_object.md`.
  - [ ] Write documentation page for *each* resource service (e.g., `docs/sdk/config/objects/address.md`).
  - [ ] Write documentation page for *each* group of resource models (e.g., `docs/sdk/models/objects/address_models.md`).
  - [ ] Write `docs/about/contributing.md`.
  - [ ] Write `docs/about/release-notes.md` (initial version).
  - [ ] Write `docs/about/troubleshooting.md`.
  - [ ] Write `LICENSE.md` (confirm Apache 2.0).
  - [ ] Write `SUPPORT.md`.
- [ ] **Examples**
  - [ ] Create runnable Python script examples in `examples/` directory for common use cases and resources.
  - [ ] Embed concise code snippets within documentation pages.
- [ ] **Deployment**
  - [ ] Set up GitHub Actions workflow to build and deploy docs to GitHub Pages.

## VII. Development Process & Release

- [ ] **Version Control**
  - [ ] Establish branching strategy (e.g., Gitflow-like).
  - [ ] Configure Pull Request templates and review requirements.
- [ ] **Release Management**
  - [ ] Define process for version bumping (manual/tooling).
  - [ ] Set up CI/CD workflow for building dist (`poetry build`).
  - [ ] Set up CI/CD workflow for publishing to PyPI (`poetry publish`).
  - [ ] Ensure Changelog/Release Notes are updated before release.
  - [ ] Create Git tags for releases.

## VIII. Final Review & Polish

- [ ] Review all code for consistency and adherence to principles.
- [ ] Review all tests for completeness.
- [ ] Proofread all documentation and examples.
- [ ] Ensure all requirements from the PRD are met.
- [ ] Perform final testing of core workflows.