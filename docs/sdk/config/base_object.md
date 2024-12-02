# Base Configuration Object

## Overview

The `BaseObject` class serves as the foundation for all configuration objects in the SCM SDK. It provides a standardized
interface for CRUD operations (Create, Read, Update, Delete) and job management functionality that is inherited by all
configuration object types.

## Class Methods

### CRUD Operations

| Method     | Description                           | Parameters             |
|------------|---------------------------------------|------------------------|
| `create()` | Creates a new configuration object    | `data: Dict[str, Any]` |
| `get()`    | Retrieves an object by ID             | `object_id: str`       |
| `update()` | Updates an existing object            | `data: Dict[str, Any]` |
| `delete()` | Deletes an object                     | `object_id: str`       |
| `list()`   | Lists objects with optional filtering | `**filters`            |

### Job Management

| Method             | Description                              | Parameters                                           |
|--------------------|------------------------------------------|------------------------------------------------------|
| `list_jobs()`      | Lists jobs with pagination and filtering | `limit`, `offset`, `parent_id`                       |
| `get_job_status()` | Gets status of a specific job            | `job_id: str`                                        |
| `commit()`         | Commits configuration changes            | `folders`, `description`, `admin`, `sync`, `timeout` |

## Class Definition

<div class="termy">

<!-- termynal -->

```python
class BaseObject:
    def __init__(self, api_client: Scm):
        self.api_client = api_client
        if not hasattr(self, "ENDPOINT"):
            raise AttributeError("ENDPOINT must be defined in the subclass")
```

</div>

## Usage Examples

### Creating Objects

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.objects import Address

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize address object
addresses = Address(client)

# Create new address
new_address = addresses.create({
    "name": "test-address",
    "ip_netmask": "192.168.1.0/24",
    "folder": "Texas"
})
```

</div>

### Managing Objects

<div class="termy">

<!-- termynal -->

```python
# Get object by ID
object_data = addresses.get("object-id")

# Update object
updated = addresses.update({
    "id": "object-id",
    "name": "updated-name",
    "folder": "Texas"
})

# Delete object
addresses.delete("object-id")

# List objects with filters
objects = addresses.list(folder="Texas", limit=100)
```

</div>

### Job Management

<div class="termy">

<!-- termynal -->

```python
# List jobs
jobs = addresses.list_jobs(limit=10)

# Get job status
status = addresses.get_job_status("job-id")

# Commit changes
result = addresses.commit(
    folders=["Texas"],
    description="Update configuration",
    sync=True
)
```

</div>

## Error Handling

The BaseObject class uses the same exception hierarchy as the client:

- `APIError`: Base exception for all API errors
- `AuthenticationError`: Authentication failures
- `InvalidObjectError`: Invalid object data
- `NotFoundError`: Object not found
- `ServerError`: Server-side errors

<div class="termy">

<!-- termynal -->

```python
from scm.exceptions import APIError, InvalidObjectError

try:
    result = addresses.create({
        "name": "test-address",
        "ip_netmask": "invalid-ip",
        "folder": "Texas"
    })
except InvalidObjectError as e:
    print(f"Invalid data: {e.message}")
except APIError as e:
    print(f"API error: {str(e)}")
```

</div>

## Best Practices

1. **Object Creation**
    - Always validate object data before creation
    - Use proper error handling for validation failures
    - Include required attributes for each object type

2. **Job Management**
    - Monitor job status after operations
    - Use appropriate timeouts for different operations
    - Handle child jobs for complex operations

3. **Error Handling**
    - Implement comprehensive error handling
    - Log errors for troubleshooting
    - Handle specific exceptions appropriately

4. **Performance**
    - Reuse object instances when possible
    - Use appropriate pagination for list operations
    - Implement proper retry mechanisms