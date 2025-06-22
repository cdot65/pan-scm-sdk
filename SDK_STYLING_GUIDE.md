# SDK Service File Styling Guide

This guide provides comprehensive instructions for creating consistent SDK service files in the pan-scm-sdk project.

## Quick Start

When creating a new SDK service:

1. Use `SDK_SERVICE_TEMPLATE.py` as your starting point
2. Reference existing services like `address.py` or `address_group.py` for patterns
3. Follow the naming conventions and structure outlined below
4. Create corresponding model files using `CLAUDE_MODELS.md` as a guide

## File Organization

### Service Files
```
scm/config/<category>/<resource>.py
```

Examples:
- `scm/config/objects/address.py`
- `scm/config/security/security_rule.py`
- `scm/config/deployment/service_connections.py`

### Model Files
```
scm/models/<category>/<resource>.py
```

Examples:
- `scm/models/objects/address.py`
- `scm/models/security/security_rules.py`
- `scm/models/deployment/service_connections.py`

### Key Conventions
- **One main service class per file** (named after the resource in PascalCase, singular)
- **Line length**: 88 characters (ruff default)
- **Imports**: Always use absolute imports for SDK-internal modules
- **Type hints**: Required for all parameters and return values (Python 3.10+)
- **Docstrings**: Google-style, required for all public classes and methods

## Service File Structure

### 1. Module Documentation
```python
"""<Resource> configuration service for Strata Cloud Manager SDK.

Provides service class for managing <resource> objects via the SCM API.
"""

# scm/config/<category>/<resource>.py
```

**Important**: Google-style docstring is required, describing both the file's purpose and resource

### 2. Imports
```python
# Standard library imports
import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import (...)
from scm.models.<category> import (...)
```

### 3. Class Definition
```python
class <Resource>(BaseObject):
    """Manages <Resource> objects in Palo Alto Networks' Strata Cloud Manager.

    Args:
        api_client: The API client instance
        max_limit (Optional[int]): Maximum number of objects to return in a single API request.
            Defaults to 2500. Must be between 1 and 5000.

    """

    ENDPOINT = "/config/<category>/v1/<resources>"
    DEFAULT_MAX_LIMIT = 2500
    ABSOLUTE_MAX_LIMIT = 5000
```

## Common Patterns

### Container Validation
Most resources require exactly one container:

```python
container_parameters = self._build_container_params(folder, snippet, device)

if len(container_parameters) != 1:
    raise InvalidObjectError(
        message="Exactly one of 'folder', 'snippet', or 'device' must be provided.",
        error_code="E003",
        http_status_code=400,
        details={"error": "Invalid container parameters"},
    )
```

### Pagination
Standard pagination pattern:

```python
limit = self._max_limit
offset = 0
all_objects = []

while True:
    params = container_parameters.copy()
    params["limit"] = limit
    params["offset"] = offset

    response = self.api_client.get(self.ENDPOINT, params=params)

    # Process response...

    if len(data) < limit:
        break

    offset += limit
```

### Error Handling
Consistent error patterns:

```python
# Empty string validation
if folder == "":
    raise MissingQueryParameterError(
        message="Field 'folder' cannot be empty",
        error_code="E003",
        http_status_code=400,
        details={
            "field": "folder",
            "error": '"folder" is not allowed to be empty',
        },
    )

# Response validation
if not isinstance(response, dict):
    raise InvalidObjectError(
        message="Invalid response format: expected dictionary",
        error_code="E003",
        http_status_code=500,
        details={"error": "Response is not a dictionary"},
    )
```

## Special Cases & Behaviors

### Boolean Field Handling
- **Important**: Only include `True` values in API payloads
- Omit `False` values from payloads (SCM API requirement)
- Always use `.model_dump(exclude_unset=True)` for serialization

### Security Rules
- Include `rulebase` parameter (enum: "pre" or "post")
- Special `move()` method
- Additional validation for rulebase

### Service Connections
- Simplified `list()` method without containers
- Fixed folder value: "Service Connections"
- Different pagination limits (200 vs 2500)

### Deployment Services
- May have different max limits
- Sometimes no container validation required

### API Call Patterns
- All API calls must go through `self.api_client`
- Always specify endpoint and parameters explicitly
- Use model-driven approach for all data validation/serialization

## Testing Guidelines

Each service should have comprehensive tests:

```python
# Test file location
tests/config/<category>/test_<resource>.py

# Test structure
class TestResource:
    def test_create(self, mock_api_client):
        """Test creating a resource."""

    def test_get(self, mock_api_client):
        """Test getting a resource by ID."""

    def test_list(self, mock_api_client):
        """Test listing resources."""

    def test_update(self, mock_api_client):
        """Test updating a resource."""

    def test_delete(self, mock_api_client):
        """Test deleting a resource."""

    def test_fetch(self, mock_api_client):
        """Test fetching a resource by name."""
```

## Checklist for New Services

- [ ] Create service file using `SDK_SERVICE_TEMPLATE.py`
- [ ] Create model files for Create, Update, and Response models
- [ ] Update `__init__.py` files in both service and model directories
- [ ] Implement standard CRUD methods
- [ ] Add proper docstrings to all classes and methods
- [ ] Implement proper error handling
- [ ] Create comprehensive tests
- [ ] Update client.py to include new service
- [ ] Run linting and formatting: `make quality`
- [ ] Ensure >80% test coverage

## Common Mistakes to Avoid

1. **Inconsistent naming**: Ensure PascalCase for classes, snake_case for methods
2. **Missing validation**: Always validate inputs, especially containers
3. **Incorrect exception types**: Use appropriate exceptions from `scm.exceptions`
4. **Missing docstrings**: Every public method needs a Google-style docstring
5. **Hardcoded values**: Use class constants for limits and endpoints
6. **Ignoring pagination**: Always implement proper pagination for list methods
7. **Not following patterns**: Reference existing services for consistent patterns
8. **Wrong imports**: Use absolute imports only for SDK-internal modules
9. **Incorrect boolean handling**: Remember to omit `False` values from payloads
10. **Wrong serialization**: Always use `.model_dump(exclude_unset=True)`

## Resources

- `SDK_SERVICE_TEMPLATE.py`: Template for new service files
- `CLAUDE_MODELS.md`: Guide for creating Pydantic models
- `WINDSURF_RULES.md`: Overall project guidelines
- `PRD.md`: Product requirements and vision
- Example services: `address.py`, `address_group.py`, `security_rule.py`
