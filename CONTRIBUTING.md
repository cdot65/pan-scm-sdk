# Contributing to `pan-scm-sdk`

We welcome contributions to `pan-scm-sdk`! This document provides guidelines and instructions on how to contribute effectively.

## Quick Start

```bash
git clone https://github.com/cdot65/pan-scm-sdk.git
cd pan-scm-sdk
make setup  # Install deps + pre-commit hooks
```

## Development Resources

Before making changes, review the relevant styling guides:

| Guide | Purpose |
|-------|---------|
| `SDK_STYLING_GUIDE.md` | Service class patterns and standards |
| `PYDANTIC_MODELS_GUIDE.md` | Pydantic model patterns and conventions |
| `SDK_SERVICE_TEMPLATE.py` | Copy-paste template for new services |

## How to Contribute

- **Reporting Bugs**: Open an issue with clear description and steps to reproduce
- **Suggesting Enhancements**: Open an issue with detailed explanation
- **Pull Requests**: Ensure it does not duplicate existing work

## Pull Request Process

1. Fork the repository and create your branch from `main`
2. Make your changes following the styling guides listed above
3. Run quality checks before committing:
   ```bash
   make quality  # isort + ruff + flake8 + mypy
   make test     # Run all tests
   ```
4. Write clear, concise commit messages
5. Open a pull request with a comprehensive description of changes

## Code Patterns

### Service Class Structure

Every service class inherits from `BaseObject` and implements CRUD methods:

```python
class Resource(BaseObject):
    ENDPOINT = "/config/category/v1/resources"
    DEFAULT_MAX_LIMIT = 2500
    ABSOLUTE_MAX_LIMIT = 5000

    # Required: create, get, update, delete, list, fetch
```

### Model Hierarchy

Every resource needs four Pydantic models:

- `ResourceBaseModel` - Shared fields
- `ResourceCreateModel` - For POST requests
- `ResourceUpdateModel` - For PUT requests (includes `id`)
- `ResourceResponseModel` - API response (includes `id` + response-only fields)

### Container Validation

Most resources require exactly one of `folder`, `snippet`, or `device`.

### Payload Serialization

Always use `model.model_dump(exclude_unset=True)` for API payloads.

## Adding New Resources

1. **Service**: Copy `SDK_SERVICE_TEMPLATE.py` → `scm/config/{category}/{resource}.py`
2. **Models**: Create `scm/models/{category}/{resource}.py`
3. **Client**: Register in `scm/client.py`
4. **Tests**: Add `tests/scm/config/{category}/test_{resource}.py`
5. **Docs**: Add `docs/sdk/config/{category}/{resource}.md`

## Testing

```bash
make test                                          # All tests
make test-cov                                      # With coverage
poetry run pytest tests/path/test_file.py -v      # Single file
```

### Test Markers

- `@pytest.mark.api` - Requires API access
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.integration` - Integration tests

## Documentation

Documentation lives in `docs/sdk/`:

- `config/{category}/{resource}.md` - Service usage
- `models/{category}/{resource}_models.md` - Model reference

Key patterns:
- Use `ScmClient` unified client pattern in examples
- Update examples use fetch → dot notation → update workflow
- Include Filter Parameters table for `list()` method

Serve docs locally:
```bash
make docs-serve  # http://localhost:8000/pan-scm-sdk/
```

## Project Structure

```
scm/
├── client.py           # ScmClient entry point
├── auth.py             # OAuth2 authentication
├── config/             # Service classes
│   ├── objects/        # address, tag, service, etc.
│   ├── security/       # security_rule, profiles
│   ├── network/        # nat_rules, ike_gateway
│   ├── deployment/     # remote_networks, etc.
│   ├── mobile_agent/   # auth_settings
│   └── setup/          # folder, snippet, variable
├── models/             # Pydantic models (parallel to config/)
├── exceptions/         # Custom exceptions
└── operations/         # Jobs, candidate push
```

## Code of Conduct

Please adhere to the Code of Conduct to maintain a respectful and collaborative environment.

## Questions?

If you have any questions or need further clarification, feel free to open an issue or contact the project maintainers directly.

Thank you for contributing to `pan-scm-sdk`!
