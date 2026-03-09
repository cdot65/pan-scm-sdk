# Base Configuration Object

Serves as the foundation for all configuration objects in Palo Alto Networks Strata Cloud Manager.

## Class Overview

The `BaseObject` class provides standardized CRUD operations (Create, Read, Update, Delete) and job management functionality that is inherited by all configuration object types.

### Methods

| Method             | Description                   | Parameters                                           | Return Type             |
|--------------------|-------------------------------|------------------------------------------------------|-------------------------|
| `create()`         | Creates new object            | `data: Dict[str, Any]`                               | `Dict[str, Any]`        |
| `get()`            | Retrieves object by ID        | `object_id: str`                                     | `Dict[str, Any]`        |
| `update()`         | Updates existing object       | `data: Dict[str, Any]`                               | `Dict[str, Any]`        |
| `delete()`         | Deletes object                | `object_id: str`                                     | `None`                  |
| `list()`           | Lists objects with filtering  | `**filters`                                          | `List[Dict[str, Any]]`  |
| `list_jobs()`      | Lists jobs with pagination    | `limit: int`, `offset: int`, `parent_id: str`        | `JobListResponse`       |
| `get_job_status()` | Gets job status               | `job_id: str`                                        | `JobStatusResponse`     |
| `commit()`         | Commits configuration changes | `folders: List[str]`, `description: str`, `**kwargs` | `CandidatePushResponse` |

### Model Attributes

| Attribute    | Type | Required | Description                             |
|--------------|------|----------|-----------------------------------------|
| `ENDPOINT`   | str  | Yes      | API endpoint path for object operations |
| `api_client` | Scm  | Yes      | Instance of SCM API client              |

### Exceptions

| Exception                    | HTTP Code | Description                   |
|------------------------------|-----------|-------------------------------|
| `InvalidObjectError`         | 400       | Invalid object data or format |
| `MissingQueryParameterError` | 400       | Missing required parameters   |
| `NotFoundError`              | 404       | Object not found              |
| `AuthenticationError`        | 401       | Authentication failed         |
| `AuthorizationError`         | 403       | Permission denied             |
| `ConflictError`              | 409       | Object conflict               |
| `ServerError`                | 500       | Internal server error         |

### Basic Configuration

```python
from scm.client import ScmClient

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Most objects can be accessed directly through the client
# Example: client.address, client.service_group, client.security_rule, etc.
```

For custom or extended objects:

```python
from scm.client import Scm
from scm.config.objects import BaseObject

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

class CustomObject(BaseObject):
    ENDPOINT = "/config/objects/v1/custom"

custom_obj = CustomObject(client)
```

## Methods

### List Objects

```python
list_params = {
    "folder": "Texas",
    "limit": 100,
    "offset": 0
}
objects = custom_obj.list(**list_params)
for obj in objects:
    print(f"Name: {obj['name']}")
```

**Filtering responses:**

```python
# Only return objects defined exactly in 'Texas'
exact_objects = custom_obj.list(
    folder='Texas',
    exact_match=True
)

# Exclude all objects from the 'All' folder
no_all_objects = custom_obj.list(
    folder='Texas',
    exclude_folders=['All']
)
```

**Controlling pagination with max_limit:**

```python
custom_obj = CustomObject(client, max_limit=4321)

all_objects = custom_obj.list(folder='Texas')
```

### Create an Object

```python
object_data = {
    "name": "test-object",
    "description": "Test object creation",
    "folder": "Texas"
}
new_object = custom_obj.create(object_data)
print(f"Created object with ID: {new_object['id']}")
```

### Update an Object

```python
update_data = {
    "id": "123e4567-e89b-12d3-a456-426655440000",
    "name": "updated-object",
    "description": "Updated description",
    "folder": "Texas"
}
updated_object = custom_obj.update(update_data)
```

### Delete an Object

```python
custom_obj.delete("123e4567-e89b-12d3-a456-426655440000")
```

### Get an Object by ID

```python
retrieved_object = custom_obj.get("123e4567-e89b-12d3-a456-426655440000")
print(f"Retrieved object: {retrieved_object['name']}")
```

## Use Cases

### Committing Changes

```python
result = client.commit(
    folders=["Texas"],
    description="Configuration update",
    sync=True,
    timeout=300
)
print(f"Commit job ID: {result.job_id}")
```

### Monitoring Jobs

```python
job_status = client.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

recent_jobs = client.list_jobs(limit=10)
for job in recent_jobs.data:
    print(f"Job {job.id}: {job.type_str} - {job.status_str}")
```

## Error Handling

```python
from scm.exceptions import (
    InvalidObjectError,
    NotFoundError,
    AuthenticationError,
    ServerError
)

try:
    result = custom_obj.create({
        "name": "test-object",
        "folder": "Texas"
    })
    commit_result = client.commit(
        folders=["Texas"],
        description="Added test object",
        sync=True
    )
    status = client.get_job_status(commit_result.job_id)

except InvalidObjectError as e:
    print(f"Invalid object data: {e.message}")
except NotFoundError as e:
    print(f"Object not found: {e.message}")
except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
except ServerError as e:
    print(f"Server error: {e.message}")
```

## Related Topics

- [Job Models](../models/operations/jobs.md)
- [Candidate Push Models](../models/operations/candidate_push.md)
- [API Client](../client.md)
- [Full Example Scripts](https://github.com/cdot65/pan-scm-sdk/tree/main/examples)
