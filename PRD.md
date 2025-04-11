# Strata Cloud Manager SDK - Product Requirements Document

## 1. Product Overview

### 1.1 Product Vision

The Strata Cloud Manager (SCM) SDK is a Python-based software development kit designed to provide developers with a robust, intuitive, and secure interface for programmatically interacting with the Palo Alto Networks Strata Cloud Manager API. It aims to simplify the automation, integration, and management of cloud-delivered security infrastructure by offering a well-structured, validated, and documented client library.

### 1.2 Guiding Principles

* **Intuitive:** Provide a clear and easy-to-use API surface, favoring the unified client pattern for streamlined development.
* **Robust:** Implement comprehensive error handling, data validation, and resilient communication (e.g., token refresh, retries).
* **Secure:** Prioritize secure authentication (OAuth2) and credential handling.
* **Extensible:** Design with a modular structure (`BaseObject`) allowing for straightforward addition of new SCM resources.
* **Well-Documented:** Offer comprehensive technical and user documentation, including examples.

### 1.3 Target Audience

* Network Security Engineers automating configuration tasks.
* DevOps Engineers integrating SCM into CI/CD pipelines and IaC workflows.
* Security Automation Engineers building custom security tools and integrations.
* Cloud Infrastructure Engineers managing SCM alongside other cloud services.
* System Administrators scripting SCM operations.

---

## 2. Core Features

### 2.1 Authentication & Client (`client.md`, `auth.md`)

* **OAuth2 Client Credentials Flow:** Implement secure authentication using `client_id`, `client_secret`, and `tsg_id`.
* **Token Management:** Automatically handle OAuth2 token acquisition, validation (JWT), and refresh using `requests_oauthlib`. Include configurable retry mechanisms and expiry buffer.
* **Custom Token URL:** Support specifying a custom `token_url` during client initialization for different environments or identity providers.
* **Unified Client (`Scm`/`ScmClient`):** Provide a primary client class offering attribute-based access to all resource services (e.g., `client.address.list()`). This is the **recommended** pattern.
* **Legacy Client Pattern:** Maintain support for the traditional pattern where service objects are instantiated manually (e.g., `Address(client)`), though deemphasized.
* **Configurable Logging:** Allow users to set the logging level (e.g., `DEBUG`, `INFO`, `ERROR`).
* **Base URL Configuration:** Allow specifying the SCM API base URL.

### 2.2 Resource Management (`index.md`, `base_object.md`, specific object `.md` files)

Provide standardized CRUD (Create, Read, Update, Delete) and specific operations for SCM configuration objects, inheriting common logic from `BaseObject`.

* **Standard Methods:** Implement consistent methods across resource types:
  * `create(data)`: Create a new resource instance.
  * `get(object_id)`: Retrieve a resource by its unique ID.
  * `fetch(name, container)`: Retrieve a resource by its name within a specific container.
  * `list(container, **filters)`: Retrieve multiple resources, supporting filtering and pagination.
  * `update(model_or_dict)`: Update an existing resource.
  * `delete(object_id_or_model)`: Delete a resource.
* **Container Support:** Enforce and manage resources within SCM containers (`folder`, `snippet`, `device`), ensuring exactly one is specified where required.
* **Filtering & Pagination (`base_object.md`):**
  * Implement server-side filtering where available via API parameters.
  * Implement client-side post-filtering options: `exact_match`, `exclude_folders`, `exclude_snippets`, `exclude_devices`.
  * Implement automatic pagination for `list` methods with configurable `max_limit` per resource type (default 2500, API max 5000).
* **Supported Resource Types (`index.md`, `release-notes.md`):**
  * **Objects:** Address, Address Group, Application, Application Filter, Application Group, Dynamic User Group, External Dynamic List, HIP Object, HIP Profile, HTTP Server Profile, Log Forwarding Profile, Quarantined Device, Region, Schedule, Service, Service Group, Syslog Server Profile, Tag. *(Confirm Auto Tag Actions)*
  * **Network:** IKE Crypto Profile, IKE Gateway, IPsec Crypto Profile, NAT Rule, Security Zone.
  * **Mobile Agent:** Authentication Settings, Agent Versions (Read-Only).
  * **Deployment:** Bandwidth Allocation, BGP Routing, Internal DNS Servers, Network Location, Remote Network, Service Connection.
  * **Security Services:** Security Rule, Anti-Spyware Profile, Decryption Profile, DNS Security Profile, URL Categories, Vulnerability Protection Profile, Wildfire Antivirus Profile.

### 2.3 Configuration Management (`base_object.md`, `client.md`)

* **Commit Operation (`client.commit`):** Implement functionality to push candidate configurations live, supporting `folders`, `description`, `admin`, `sync` (wait for completion), and `timeout` parameters.
* **Job Management (`client.list_jobs`, `client.get_job_status`, `client.wait_for_job`):** Provide methods to list jobs, check the status of a specific job (including commit jobs), and wait for job completion with polling.

### 2.4 Data Validation (`exceptions.md`, specific model `.md` files)

* **Pydantic Models:** Utilize Pydantic for defining request and response data structures for all supported resources.
* **Input Validation:** Enforce required fields, data types, string lengths, value constraints (e.g., color lists, risk levels), and regex patterns (e.g., names, FQDNs).
* **Constraint Validation:** Implement model validators for complex rules (e.g., exactly one container, exactly one address type, exactly one schedule type).
* **Serialization/Deserialization:** Automatically handle conversion between Python objects and JSON payloads for API interaction.

### 2.5 Error Handling (`exceptions.md`)

* **Custom Exception Hierarchy:** Define a clear hierarchy inheriting from `APIError`, including `ClientError` and `ServerError`.
* **Specific Exceptions:** Map API error codes and HTTP status codes to specific, informative Python exceptions (e.g., `ObjectNotPresentError`, `NameNotUniqueError`, `AuthenticationError`, `InvalidObjectError`, `ReferenceNotZeroError`).
* **Standardized Error Response:** Parse API error responses into a consistent `ErrorResponse` structure within exceptions.

---

## 3. Technical Requirements

### 3.1 System Requirements

* **Python Version:** Python 3.10 or higher.
* **Operating Systems:** Support modern versions of Windows, macOS, and Linux.
* **Connectivity:** Requires HTTPS internet connectivity to Strata Cloud Manager API endpoints.

### 3.2 Dependencies (`pyproject.toml`, `auth.md`)

* **Package Management:** Use Poetry for dependency management and packaging.
* **Core Dependencies:** Explicitly list key external dependencies (e.g., `requests`, `requests-oauthlib`, `pydantic`, `python-jose[cryptography]`/`pyjwt`).
* **Minimize Footprint:** Aim for a minimal and well-justified set of external dependencies.

### 3.3 Security Requirements

* **Authentication:** Enforce OAuth2 client credentials flow.
* **Transport:** All API communication must use HTTPS/TLS.
* **Credential Handling:** Avoid storing credentials directly in code; recommend environment variables or secure configuration methods. SDK should not persist credentials unnecessarily.
* **Token Security:** Handle tokens securely in memory; avoid logging sensitive token data.

### 3.4 Licensing

* **License:** Apache 2.0 License (`license.md`).

---

## 4. API Design

### 4.1 Client Architecture

* **Primary Interface:** The `Scm` (or `ScmClient`) class serves as the unified entry point.
* **Service Access:** Resource management logic is accessed via attributes on the client instance (e.g., `client.address`).
* **Modularity:** Internal implementation uses service classes (e.g., `Address`, `Tag`) inheriting from `BaseObject`.
* **Consistency:** Maintain consistent method signatures and parameter names across different resource types where applicable.

### 4.2 Method Standardization (Covered in 2.2)

* Standard CRUD + `fetch` methods.
* Standard `commit` and job methods on the client.

### 4.3 Parameter Standardization (Covered in 2.2)

* Consistent use of `folder`, `snippet`, `device` for container specification.
* Consistent use of `name` and `id` for object identification.
* Standardized filtering parameters for `list` methods.

### 4.4 Data Structures (Covered in 2.4)

* Use Pydantic models for all API request payloads and response parsing.
* Define separate models for Create, Update, and Response where structures differ significantly.

---

## 5. Quality Assurance

### 5.1 Testing Requirements

* **Unit Tests:** Implement comprehensive unit tests using `pytest` covering model validation, helper functions, and individual service method logic.
* **Integration Tests:** Develop integration tests (potentially using recorded interactions or a dedicated test tenant) to verify end-to-end API communication for core workflows.
* **Code Coverage:** Target a minimum code coverage of 80%, measured using `coverage.py` / `codecov`.
* **CI/CD:** Integrate testing and quality checks into a CI/CD pipeline (e.g., GitHub Actions).

### 5.2 Code Quality (`README.md`, `CONTRIBUTING.md`)

* **Linting & Formatting:** Enforce code style and quality using `ruff`. Configuration defined in `pyproject.toml`.
* **Pre-commit Hooks:** Utilize pre-commit hooks to automatically run checks (linting, formatting, basic syntax) before commits.
* **Type Checking:** Use type hints extensively and consider integrating `mypy` or relying on Pydantic's runtime checking.
* **Docstrings:** Require clear and concise docstrings for all public classes, methods, and functions following a standard format (e.g., Google style).

---

## 6. Documentation (`README.md`, `index.md` (docs))

### 6.1 Technical Documentation

* **API Reference:** Auto-generate API reference documentation from docstrings (e.g., using MkDocs with `mkdocstrings`).
* **Model Documentation:** Provide dedicated pages detailing attributes, validation, and usage for each Pydantic model group (as seen in provided examples).
* **Core Modules:** Document key modules like `client`, `auth`, `exceptions`, and `BaseObject`.

### 6.2 User Documentation

* **README:** Maintain a comprehensive README with overview, features, installation, basic usage, and contribution guidelines.
* **Installation Guide:** Clear instructions for installing the SDK (`installation.md`).
* **Getting Started Guide:** A tutorial guiding new users through authentication and basic operations (`getting-started.md`).
* **Usage Examples:** Provide practical, runnable examples for common tasks and supported resources in an `examples/` directory and embedded in documentation.
* **Troubleshooting Guide:** Common issues and solutions (`troubleshooting.md`).
* **Release Notes:** Maintain a `release-notes.md` detailing changes in each version.
* **Deployment:** Host documentation publicly (e.g., using GitHub Pages).

---

## 7. Development Process

### 7.1 Version Control

* **Repository:** Use Git hosted on GitHub.
* **Branching:** Employ a feature branch workflow (e.g., `feature/`, `fix/`, `docs/`).
* **Pull Requests:** Require Pull Requests for merging changes into the main branch. Implement PR templates and require reviews.
* **Commits:** Encourage clear and atomic commit messages.

### 7.2 Release Management

* **Versioning:** Use Semantic Versioning (SemVer - MAJOR.MINOR.PATCH).
* **Changelog:** Automatically generate or manually maintain a CHANGELOG file.
* **Tagging:** Create Git tags for each release.
* **Packaging:** Build and publish releases to PyPI using Poetry.

---

## 8. Support and Maintenance

### 8.1 Support Channels

* **Issue Tracking:** Use GitHub Issues for bug reports, feature requests, and questions.
* **Documentation:** Provide up-to-date documentation as the primary support resource.
* *(Optional: Community forum or mailing list)*

### 8.2 Maintenance Plan

* **Bug Fixes:** Address critical bugs promptly in patch releases.
* **Security:** Monitor dependencies for vulnerabilities and issue patches as needed. Address any reported SDK vulnerabilities.
* **Compatibility:** Maintain compatibility with supported Python versions and SCM API changes where feasible.
* **Dependency Updates:** Regularly update dependencies.
* **Refactoring:** Periodically refactor code for maintainability and performance.

---

## 9. Future Enhancements

### 9.1 Potential Features

* Support for additional SCM resources as they become available via API.
* Enhanced filtering capabilities (e.g., more complex query logic if API supports).
* Async client support (`asyncio`).
* Helper functions for common multi-step workflows.
* Support for different SCM API versions if applicable.

### 9.2 Potential Integrations

* Examples demonstrating integration with IaC tools (Terraform, Ansible).
* Integration with popular automation frameworks.
* Use cases for integration with SIEM/SOAR platforms.

---

## 10. Success Metrics

### 10.1 Technical Metrics

* **Code Coverage:** Maintain >80% coverage.
* **API Call Success Rate:** Monitor via logging or external tools if possible.
* **Average API Response Time:** Track performance characteristics.
* **Build/Test Success Rate:** Monitor CI/CD pipeline health.
* **Dependency Vulnerabilities:** Track number of known vulnerabilities in dependencies.

### 10.2 User & Community Metrics

* **Downloads/Adoption:** Track PyPI download statistics.
* **GitHub Activity:** Monitor stars, forks, issues reported, PRs submitted.
* **Issue Resolution Time:** Track time to close reported issues.
* **Community Contributions:** Number of unique contributors.
* **Documentation Page Views:** Track usage of the documentation site.
