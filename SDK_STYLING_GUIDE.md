# SDK Service Class Styling Guide

This guide defines the standards and patterns for writing SDK service classes in the pan-scm-sdk project.

## Table of Contents

1. [File Structure](#file-structure)
2. [Class Structure](#class-structure)
3. [Constants](#constants)
4. [Constructor](#constructor)
5. [CRUD Methods](#crud-methods)
6. [Pagination](#pagination)
7. [Filtering](#filtering)
8. [Error Handling](#error-handling)
9. [Docstrings](#docstrings)
10. [Import Organization](#import-organization)

## File Structure

Each service class should be in its own file within the appropriate category directory:

```
scm/config/
├── __init__.py          # Contains BaseObject
├── objects/             # Address, Tag, Service, etc.
├── security/            # SecurityRule, AntiSpywareProfile, etc.
├── network/             # NatRule, IkeGateway, etc.
├── deployment/          # ServiceConnection, RemoteNetwork, etc.
├── mobile_agent/        # AuthSetting, AgentVersion, etc.
└── setup/               # Folder, Snippet, Variable, etc.
```

## Class Structure

### Required Components

Every service class must include:

1. Module docstring
2. Imports (organized by type)
3. Class definition inheriting from `BaseObject`
4. Class docstring with Attributes section
5. Class constants (`ENDPOINT`, `DEFAULT_MAX_LIMIT`, `ABSOLUTE_MAX_LIMIT`)
6. Constructor (`__init__`)
7. `max_limit` property and setter
8. CRUD methods (`create`, `get`, `update`, `delete`, `list`, `fetch`)

### Example Structure

```python
"""Service classes for interacting with Resources in Palo Alto Networks' Strata Cloud Manager.

This module provides the Resource class for performing CRUD operations on Resource
objects in the Strata Cloud Manager.
"""

# Standard library imports
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.category.resource import (
    ResourceCreateModel,
    ResourceResponseModel,
    ResourceUpdateModel,
)


class Resource(BaseObject):
    """Manages Resource objects in Palo Alto Networks' Strata Cloud Manager.

    This class provides methods for creating, retrieving, updating, and deleting
    Resource objects.

    Attributes:
        ENDPOINT: The API endpoint for Resource resources.
        DEFAULT_MAX_LIMIT: The default maximum number of items per request.
        ABSOLUTE_MAX_LIMIT: The maximum allowed items per request.

    """

    ENDPOINT = "/config/category/v1/resources"
    DEFAULT_MAX_LIMIT = 2500
    ABSOLUTE_MAX_LIMIT = 5000
```

## Constants

### ENDPOINT

- Use the full API path starting with `/config/`
- Follow the pattern: `/config/{category}/v1/{resource_plural}`

```python
ENDPOINT = "/config/objects/v1/addresses"
ENDPOINT = "/config/security/v1/security-rules"
ENDPOINT = "/config/setup/v1/variables"
```

### Pagination Limits

```python
DEFAULT_MAX_LIMIT = 2500    # Default items per API request
ABSOLUTE_MAX_LIMIT = 5000   # Maximum allowed by the API
```

## Constructor

```python
def __init__(
    self,
    api_client,
    max_limit: int = DEFAULT_MAX_LIMIT,
):
    """Initialize the Resource service class.

    Args:
        api_client: The API client instance for making HTTP requests.
        max_limit: Maximum number of items to return in a single request.
                  Defaults to DEFAULT_MAX_LIMIT.

    """
    super().__init__(api_client)
    self.max_limit = min(max_limit, self.ABSOLUTE_MAX_LIMIT)
```

### max_limit Property

Always implement as a property with validation:

```python
@property
def max_limit(self) -> int:
    """Get the maximum number of items to return in a single request."""
    return self._max_limit

@max_limit.setter
def max_limit(self, value: int) -> None:
    """Set a new maximum limit for API requests."""
    self._max_limit = self._validate_max_limit(value)

def _validate_max_limit(self, limit: Optional[int]) -> int:
    """Validate the max_limit parameter."""
    if limit is None:
        return self.DEFAULT_MAX_LIMIT

    try:
        limit_int = int(limit)
    except (TypeError, ValueError):
        raise InvalidObjectError(
            message="max_limit must be an integer",
            error_code="E003",
            http_status_code=400,
            details={"error": "Invalid max_limit type"},
        )

    if limit_int < 1:
        raise InvalidObjectError(
            message="max_limit must be greater than 0",
            error_code="E003",
            http_status_code=400,
            details={"error": "Invalid max_limit value"},
        )

    if limit_int > self.ABSOLUTE_MAX_LIMIT:
        return self.ABSOLUTE_MAX_LIMIT

    return limit_int
```

## CRUD Methods

### create()

```python
def create(
    self,
    data: Dict[str, Any],
) -> ResourceResponseModel:
    """Create a new resource in the Strata Cloud Manager.

    Args:
        data: Dictionary containing resource data.

    Returns:
        ResourceResponseModel: The created resource.

    Raises:
        InvalidObjectError: If the resource data is invalid.
        APIError: If the API request fails.

    """
    create_model = ResourceCreateModel(**data)
    payload = create_model.model_dump(exclude_unset=True)
    response = self.api_client.post(self.ENDPOINT, json=payload)
    return ResourceResponseModel.model_validate(response)
```

### get()

```python
def get(
    self,
    object_id: Union[str, UUID],
) -> ResourceResponseModel:
    """Get a resource by its ID.

    Args:
        object_id: The ID of the resource to retrieve.

    Returns:
        ResourceResponseModel: The requested resource.

    Raises:
        ObjectNotPresentError: If the resource doesn't exist.
        APIError: If the API request fails.

    """
    object_id_str = str(object_id)
    try:
        response = self.api_client.get(f"{self.ENDPOINT}/{object_id_str}")
        return ResourceResponseModel.model_validate(response)
    except APIError as e:
        if e.http_status_code == 404:
            raise ObjectNotPresentError(f"Resource with ID {object_id} not found")
        raise
```

### update()

```python
def update(
    self,
    resource: ResourceUpdateModel,
) -> ResourceResponseModel:
    """Update an existing resource.

    Args:
        resource: The ResourceUpdateModel containing the updated data.

    Returns:
        ResourceResponseModel: The updated resource.

    Raises:
        InvalidObjectError: If the update data is invalid.
        ObjectNotPresentError: If the resource doesn't exist.
        APIError: If the API request fails.

    """
    payload = resource.model_dump(exclude_unset=True)
    object_id = str(resource.id)
    payload.pop("id", None)
    endpoint = f"{self.ENDPOINT}/{object_id}"
    response = self.api_client.put(endpoint, json=payload)
    return ResourceResponseModel.model_validate(response)
```

### delete()

```python
def delete(
    self,
    object_id: Union[str, UUID],
) -> None:
    """Delete a resource.

    Args:
        object_id: The ID of the resource to delete.

    Raises:
        ObjectNotPresentError: If the resource doesn't exist.
        APIError: If the API request fails.

    """
    try:
        object_id_str = str(object_id)
        self.api_client.delete(f"{self.ENDPOINT}/{object_id_str}")
    except APIError as e:
        if e.http_status_code == 404:
            raise ObjectNotPresentError(f"Resource with ID {object_id} not found")
        raise
```

### list()

```python
def list(
    self,
    **filters: Any,
) -> List[ResourceResponseModel]:
    """List resources with optional filters.

    Args:
        **filters: Additional filters for the API.

    Returns:
        List[ResourceResponseModel]: A list of resources matching the filters.

    Raises:
        APIError: If the API request fails.

    """
    params: Dict[str, Any] = {}
    limit = self.max_limit
    offset = 0
    all_objects: List[ResourceResponseModel] = []

    while True:
        params.update({"limit": limit, "offset": offset})
        params.update({k: v for k, v in filters.items() if v is not None})
        response = self.api_client.get(self.ENDPOINT, params=params)
        data_items = response["data"] if "data" in response else response
        object_instances = [ResourceResponseModel.model_validate(item) for item in data_items]
        all_objects.extend(object_instances)

        if len(data_items) < limit:
            break
        offset += limit

    return all_objects
```

### fetch()

For resources with container scoping (folder/snippet/device):

```python
def fetch(
    self,
    name: str,
    folder: str,
) -> Optional[ResourceResponseModel]:
    """Get a resource by its name and folder.

    Args:
        name: The name of the resource to retrieve.
        folder: The folder in which the resource is defined.

    Returns:
        Optional[ResourceResponseModel]: The requested resource, or None if not found.

    """
    if not name:
        raise InvalidObjectError(
            message="Field 'name' cannot be empty",
            error_code="E003",
            http_status_code=400,
            details={"field": "name", "error": '"name" is not allowed to be empty'},
        )

    if not folder:
        raise InvalidObjectError(
            message="Field 'folder' cannot be empty",
            error_code="E003",
            http_status_code=400,
            details={"field": "folder", "error": '"folder" is not allowed to be empty'},
        )

    results = self.list(folder=folder)

    if not results:
        return None

    exact_matches = [r for r in results if r.name == name]
    return exact_matches[0] if exact_matches else None
```

For resources without container scoping:

```python
def fetch(
    self,
    name: str,
) -> Optional[ResourceResponseModel]:
    """Get a resource by its name.

    Args:
        name: The name of the resource to retrieve.

    Returns:
        Optional[ResourceResponseModel]: The requested resource, or None if not found.

    """
    results = self.list()

    if not results:
        return None

    exact_matches = [r for r in results if r.name == name]
    return exact_matches[0] if exact_matches else None
```

## Pagination

Always implement auto-pagination in `list()`:

```python
while True:
    params.update({"limit": limit, "offset": offset})
    response = self.api_client.get(self.ENDPOINT, params=params)
    data_items = response["data"] if "data" in response else response
    all_objects.extend([...])

    if len(data_items) < limit:
        break
    offset += limit
```

## Filtering

### Server-Side Filters

Pass directly to API params:

```python
if "folder" in filters:
    params["folder"] = filters["folder"]
if "labels" in filters:
    params["labels"] = ",".join(filters["labels"])
```

### Client-Side Filters

Implement `_apply_filters()` static method:

```python
@staticmethod
def _apply_filters(
    data: List["ResourceResponseModel"],
    filters: Dict[str, Any],
) -> List["ResourceResponseModel"]:
    """Apply client-side filters to a list of resources."""
    filtered = data

    if not filters:
        return filtered

    # Filter by labels (intersection: any label matches)
    if "labels" in filters:
        required_labels = set(filters["labels"])
        filtered = [
            f for f in filtered
            if getattr(f, "labels", None) and required_labels.intersection(set(f.labels))
        ]

    # Filter by exact match
    if "type" in filters:
        type_val = filters["type"]
        filtered = [f for f in filtered if getattr(f, "type", None) == type_val]

    return filtered
```

## Error Handling

### Standard Exception Pattern

```python
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError

# For validation errors
raise InvalidObjectError(
    message="Descriptive error message",
    error_code="E003",
    http_status_code=400,
    details={"field": "field_name", "error": "Specific error"},
)

# For not found errors
raise ObjectNotPresentError(f"Resource with ID {object_id} not found")

# For API errors, catch and re-raise or convert
except APIError as e:
    if e.http_status_code == 404:
        raise ObjectNotPresentError(...)
    raise
```

## Docstrings

Use Google-style docstrings:

```python
def method_name(
    self,
    param1: str,
    param2: Optional[int] = None,
) -> ReturnType:
    """Short description of what the method does.

    Longer description if needed, explaining behavior, side effects,
    or important details.

    Args:
        param1: Description of param1.
        param2: Description of param2. Defaults to None.

    Returns:
        Description of return value.

    Raises:
        ExceptionType: When this exception is raised.

    """
```

## Import Organization

Organize imports in this order with blank lines between groups:

```python
"""Module docstring."""

# Standard library imports
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.category.resource import (
    ResourceCreateModel,
    ResourceResponseModel,
    ResourceUpdateModel,
)
```

## Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Class name | PascalCase, singular | `Address`, `SecurityRule` |
| File name | snake_case, singular | `address.py`, `security_rule.py` |
| Method name | snake_case | `create`, `get`, `list`, `fetch` |
| Constant | UPPER_SNAKE_CASE | `ENDPOINT`, `DEFAULT_MAX_LIMIT` |
| Parameter | snake_case | `object_id`, `max_limit` |

## Type Hints

Always use type hints:

```python
def method(
    self,
    data: Dict[str, Any],
    object_id: Union[str, UUID],
    name: Optional[str] = None,
) -> List[ResourceResponseModel]:
```

Common types:
- `Dict[str, Any]` for arbitrary dictionaries
- `Union[str, UUID]` for IDs that can be string or UUID
- `Optional[T]` for optional parameters
- `List[T]` for lists
