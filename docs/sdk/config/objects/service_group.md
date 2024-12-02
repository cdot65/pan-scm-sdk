# Service Group Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Service Group Model Attributes](#service-group-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating Service Groups](#creating-service-groups)
    - [Retrieving Service Groups](#retrieving-service-groups)
    - [Updating Service Groups](#updating-service-groups)
    - [Listing Service Groups](#listing-service-groups)
    - [Deleting Service Groups](#deleting-service-groups)
7. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Full Script Examples](#full-script-examples)
11. [Related Models](#related-models)

## Overview

The `ServiceGroup` class provides functionality to manage service groups in Palo Alto Networks' Strata Cloud Manager.
This
class inherits from `BaseObject` and provides methods for creating, retrieving, updating, and deleting service groups
that can be used to organize and manage collections of services for security policies and NAT rules.

## Core Methods

| Method     | Description                      | Parameters                               | Return Type                       |
|------------|----------------------------------|------------------------------------------|-----------------------------------|
| `create()` | Creates a new service group      | `data: Dict[str, Any]`                   | `ServiceGroupResponseModel`       |
| `get()`    | Retrieves a group by ID          | `object_id: str`                         | `ServiceGroupResponseModel`       |
| `update()` | Updates an existing group        | `service_group: ServiceGroupUpdateModel` | `ServiceGroupResponseModel`       |
| `delete()` | Deletes a group                  | `object_id: str`                         | `None`                            |
| `list()`   | Lists groups with filtering      | `folder: str`, `**filters`               | `List[ServiceGroupResponseModel]` |
| `fetch()`  | Gets group by name and container | `name: str`, `folder: str`               | `ServiceGroupResponseModel`       |

## Service Group Model Attributes

| Attribute | Type      | Required | Description                                 |
|-----------|-----------|----------|---------------------------------------------|
| `name`    | str       | Yes      | Name of group (max 63 chars)                |
| `id`      | UUID      | Yes*     | Unique identifier (*response only)          |
| `members` | List[str] | Yes      | List of service members                     |
| `tag`     | List[str] | No       | List of tags (max 64 chars each)            |
| `folder`  | str       | Yes**    | Folder location (**one container required)  |
| `snippet` | str       | Yes**    | Snippet location (**one container required) |
| `device`  | str       | Yes**    | Device location (**one container required)  |

## Exceptions

| Exception                    | HTTP Code | Description                        |
|------------------------------|-----------|------------------------------------|
| `InvalidObjectError`         | 400       | Invalid group data or format       |
| `MissingQueryParameterError` | 400       | Missing required parameters        |
| `NameNotUniqueError`         | 409       | Group name already exists          |
| `ObjectNotPresentError`      | 404       | Group not found                    |
| `ReferenceNotZeroError`      | 409       | Group still referenced by policies |
| `AuthenticationError`        | 401       | Authentication failed              |
| `ServerError`                | 500       | Internal server error              |

## Basic Configuration

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.objects import ServiceGroup

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize ServiceGroup object
service_groups = ServiceGroup(client)
```

</div>

## Usage Examples

### Creating Service Groups

<div class="termy">

<!-- termynal -->

```python
# Basic service group configuration
basic_group = {
    "name": "web-services",
    "members": ["HTTP", "HTTPS"],
    "folder": "Texas",
    "tag": ["Web"]
}

# Create basic group
basic_group_obj = service_groups.create(basic_group)

# Extended service group configuration
extended_group = {
    "name": "app-services",
    "members": ["HTTP", "HTTPS", "SSH", "FTP"],
    "folder": "Texas",
    "tag": ["Application", "Production"]
}

# Create extended group
extended_group_obj = service_groups.create(extended_group)
```

</div>

### Retrieving Service Groups

<div class="termy">

<!-- termynal -->

```python
# Fetch by name and folder
group = service_groups.fetch(name="web-services", folder="Texas")
print(f"Found group: {group.name}")

# Get by ID
group_by_id = service_groups.get(group.id)
print(f"Retrieved group: {group_by_id.name}")
print(f"Members: {', '.join(group_by_id.members)}")
```

</div>

### Updating Service Groups

<div class="termy">

<!-- termynal -->

```python
# Fetch existing group
existing_group = service_groups.fetch(name="web-services", folder="Texas")

# Update members
existing_group.members = ["HTTP", "HTTPS", "HTTP-8080"]
existing_group.tag = ["Web", "Updated"]

# Perform update
updated_group = service_groups.update(existing_group)
```

</div>

### Listing Service Groups

<div class="termy">

<!-- termynal -->

```python
# List with direct filter parameters
filtered_groups = service_groups.list(
    folder='Texas',
    values=['HTTP', 'HTTPS'],
    tags=['Production']
)

# Process results
for group in filtered_groups:
    print(f"Name: {group.name}")
    print(f"Members: {', '.join(group.members)}")

# Define filter parameters as dictionary
list_params = {
    "folder": "Texas",
    "values": ["SSH", "FTP"],
    "tags": ["Application"]
}

# List with filters as kwargs
filtered_groups = service_groups.list(**list_params)
```

</div>

### Deleting Service Groups

<div class="termy">

<!-- termynal -->

```python
# Delete by ID
group_id = "123e4567-e89b-12d3-a456-426655440000"
service_groups.delete(group_id)
```

</div>

## Managing Configuration Changes

### Performing Commits

<div class="termy">

<!-- termynal -->

```python
# Prepare commit parameters
commit_params = {
    "folders": ["Texas"],
    "description": "Updated service groups",
    "sync": True,
    "timeout": 300  # 5 minute timeout
}

# Commit the changes
result = service_groups.commit(**commit_params)

print(f"Commit job ID: {result.job_id}")
```

</div>

### Monitoring Jobs

<div class="termy">

<!-- termynal -->

```python
# Get status of specific job
job_status = service_groups.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

# List recent jobs
recent_jobs = service_groups.list_jobs(limit=10)
for job in recent_jobs.data:
    print(f"Job {job.id}: {job.type_str} - {job.status_str}")
```

</div>

## Error Handling

<div class="termy">

<!-- termynal -->

```python
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
    NameNotUniqueError,
    ObjectNotPresentError,
    ReferenceNotZeroError
)

try:
    # Create group configuration
    group_config = {
        "name": "test-group",
        "members": ["HTTP", "HTTPS"],
        "folder": "Texas",
        "tag": ["Test"]
    }

    # Create the group
    new_group = service_groups.create(group_config)

    # Commit changes
    result = service_groups.commit(
        folders=["Texas"],
        description="Added test group",
        sync=True
    )

    # Check job status
    status = service_groups.get_job_status(result.job_id)

except InvalidObjectError as e:
    print(f"Invalid group data: {e.message}")
except NameNotUniqueError as e:
    print(f"Group name already exists: {e.message}")
except ObjectNotPresentError as e:
    print(f"Group not found: {e.message}")
except ReferenceNotZeroError as e:
    print(f"Group still in use: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing parameter: {e.message}")
```

</div>

## Best Practices

1. **Member Management**
    - Use descriptive member names
    - Keep member lists organized
    - Document member purposes
    - Validate member existence
    - Monitor member changes

2. **Container Management**
    - Always specify exactly one container (folder, snippet, or device)
    - Use consistent container names
    - Validate container existence
    - Group related service groups

3. **Error Handling**
    - Implement comprehensive error handling
    - Check job status after commits
    - Handle specific exceptions
    - Log error details
    - Monitor commit status

4. **Performance**
    - Use appropriate pagination
    - Cache frequently accessed groups
    - Implement proper retry logic
    - Monitor group sizes

5. **Security**
    - Follow least privilege principle
    - Validate input data
    - Use secure connection settings
    - Implement proper authentication
    - Monitor policy references

## Full Script Examples

Refer to
the [service_group.py example](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/objects/service_group.py).

## Related Models

- [ServiceGroupCreateModel](../../models/objects/service_group_models.md#Overview)
- [ServiceGroupUpdateModel](../../models/objects/service_group_models.md#Overview)
- [ServiceGroupResponseModel](../../models/objects/service_group_models.md#Overview)