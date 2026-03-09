# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python SDK for Palo Alto Networks Strata Cloud Manager (SCM). Provides OAuth2-authenticated CRUD operations on firewall configuration objects (addresses, security rules, NAT rules, etc.) via a unified client pattern.

## Commands

All commands run via Docker Compose (prefix with `docker compose run --rm sdk` if running manually):

```bash
make setup          # Install deps + pre-commit hooks
make test           # Run all tests
make test-cov       # Run tests with coverage (excludes @api-marked tests)
make quality        # Full quality: isort + ruff fix + format + lint + flake8 + mypy
make quality-basic  # Skip mypy
make lint           # ruff check
make mypy           # Type checking
make docs-serve     # Serve docs at localhost:8000/pan-scm-sdk/
```

Run single test: `poetry run pytest tests/scm/config/objects/test_address.py -v`

## Architecture

```
scm/
├── client.py          # Scm unified client (entry point)
├── auth.py            # OAuth2 client credentials flow
├── config/            # Service classes by category
│   ├── __init__.py    # BaseObject base class
│   ├── objects/       # address.py, tag.py, etc.
│   ├── security/      # security_rule.py, decryption_rule.py, etc.
│   ├── network/       # nat_rules.py, ike_gateway.py, etc.
│   ├── deployment/    # service_connections.py, remote_networks.py, etc.
│   ├── setup/         # folder.py, device.py, variable.py, etc.
│   ├── identity/      # authentication_profile.py, ldap_server_profile.py, etc.
│   └── mobile_agent/  # auth_settings.py, agent_versions.py
├── models/            # Pydantic models (parallel structure to config/)
│   ├── objects/       # CreateModel, UpdateModel, ResponseModel per resource
│   ├── security/
│   ├── network/
│   ├── deployment/
│   ├── setup/
│   ├── identity/
│   ├── mobile_agent/
│   ├── insights/
│   └── operations/
├── exceptions/        # APIError hierarchy + ErrorHandler
├── insights/          # Alerts service
├── operations/        # Jobs, candidate push
└── utils/             # Utility functions
```

**Usage pattern**: `client = Scm(client_id=...) → client.address.list(folder="...")`

## Key Patterns

- **Container validation**: Most resources require exactly one of `folder`, `snippet`, or `device`
- **Pagination**: Auto-pagination in `list()` via `max_limit`, typically 2500 default
- **Model serialization**: Always use `.model_dump(exclude_unset=True)` for API payloads
- **Boolean handling**: Omit `False` values from payloads (SCM API requirement)
- **Service classes**: Inherit from `BaseObject`, define `ENDPOINT`, implement CRUD methods
- **Models**: Define `<Resource>BaseModel`, `CreateModel`, `UpdateModel`, `ResponseModel` per resource

## Test Structure

```
tests/scm/
├── config/<category>/test_<resource>.py   # Unit tests per service
├── models/<category>/test_<resource>.py   # Model validation tests
├── e2e/                                   # End-to-end tests
└── integration/                           # Integration tests
```

Markers: `@pytest.mark.api`, `@pytest.mark.e2e`, `@pytest.mark.integration`

## Style

- Python 3.10+ type hints required
- Google-style docstrings
- Line length: 88 (ruff default)
- Imports: Absolute imports within `scm` package
- Naming: PascalCase classes, snake_case methods/vars, UPPER_CASE constants
