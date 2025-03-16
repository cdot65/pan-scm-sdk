# HIP Object Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [HIP Object Model Attributes](#hip-object-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating HIP Objects](#creating-hip-objects)
    - [Retrieving HIP Objects](#retrieving-hip-objects)
    - [Updating HIP Objects](#updating-hip-objects)
    - [Listing HIP Objects](#listing-hip-objects)
    - [Deleting HIP Objects](#deleting-hip-objects)
7. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Full Script Examples](#full-script-examples)
11. [Related Models](#related-models)

## Overview

The `HIPObject` class provides functionality to manage Host Information Profile (HIP) objects in Palo Alto Networks' Strata
Cloud Manager. This class inherits from `BaseObject` and provides methods for creating, retrieving, updating, and deleting
HIP objects that define security posture requirements for endpoints.

## Core Methods

| Method     | Description                      | Parameters                         | Return Type                    |
|------------|----------------------------------|------------------------------------|--------------------------------|
| `create()` | Creates a new HIP object         | `data: Dict[str, Any]`             | `HIPObjectResponseModel`       |
| `get()`    | Retrieves a HIP object by ID     | `object_id: str`                   | `HIPObjectResponseModel`       |
| `update()` | Updates an existing HIP object   | `hip_object: HIPObjectUpdateModel` | `HIPObjectResponseModel`       |
| `delete()` | Deletes a HIP object             | `object_id: str`                   | `None`                         |
| `list()`   | Lists HIP objects with filtering | `folder: str`, `**filters`         | `List[HIPObjectResponseModel]` |
| `fetch()`  | Gets HIP object by name          | `name: str`, `folder: str`         | `HIPObjectResponseModel`       |

## HIP Object Model Attributes

| Attribute          | Type                 | Required | Description                                 |
|--------------------|----------------------|----------|---------------------------------------------|
| `name`             | str                  | Yes      | Name of HIP object (max 31 chars)           |
| `id`               | UUID                 | Yes*     | Unique identifier (*response only)          |
| `description`      | str                  | No       | Object description (max 255 chars)          |
| `host_info`        | HostInfoModel        | No       | Host information criteria                   |
| `network_info`     | NetworkInfoModel     | No       | Network information criteria                |
| `patch_management` | PatchManagementModel | No       | Patch management criteria                   |
| `disk_encryption`  | DiskEncryptionModel  | No       | Disk encryption criteria                    |
| `mobile_device`    | MobileDeviceModel    | No       | Mobile device criteria                      |
| `certificate`      | CertificateModel     | No       | Certificate criteria                        |
| `folder`           | str                  | Yes**    | Folder location (**one container required)  |
| `snippet`          | str                  | Yes**    | Snippet location (**one container required) |
| `device`           | str                  | Yes**    | Device location (**one container required)  |

## Exceptions

| Exception                    | HTTP Code | Description                        |
|------------------------------|-----------|------------------------------------|
| `InvalidObjectError`         | 400       | Invalid HIP object data or format  |
| `MissingQueryParameterError` | 400       | Missing required parameters        |
| `NameNotUniqueError`         | 409       | HIP object name already exists     |
| `ObjectNotPresentError`      | 404       | HIP object not found               |
| `ReferenceNotZeroError`      | 409       | HIP object still referenced        |
| `AuthenticationError`        | 401       | Authentication failed              |
| `ServerError`                | 500       | Internal server error              |

## Basic Configuration

<div class="termy">

<!-- termynal -->

```python
from scm.client import ScmClient

# Initialize client using the unified client approach
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
    hip_object_max_limit=5000  # Optional: set custom max_limit
)

# Access the hip_object module directly through the client
# client.hip_object is automatically initialized for you
```

</div>

You can also use the traditional approach if preferred:

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.objects import HIPObject

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize HIPObject with custom max_limit
hip_objects = HIPObject(client, max_limit=5000)
```

</div>

## Usage Examples

### Creating HIP Objects

<div class="termy">

<!-- termynal -->

```python
# Host info based HIP object
host_info_config = {
    "name": "windows-workstation",
    "folder": "Shared",
    "description": "Windows workstation requirements",
    "host_info": {
        "criteria": {
            "os": {
                "contains": {
                    "Microsoft": "All"
                }
            },
            "managed": True
        }
    }
}

# Create host info HIP object
host_info_hip = client.hip_object.create(host_info_config)

# Disk encryption based HIP object
disk_encryption_config = {
    "name": "encrypted-endpoints",
    "folder": "Shared",
    "description": "Disk encryption requirements",
    "disk_encryption": {
        "criteria": {
            "is_installed": True,
            "encrypted_locations": [
                {
                    "name": "C:",
                    "encryption_state": {"is": "encrypted"}
                }
            ]
        }
    }
}

# Create disk encryption HIP object
disk_encryption_hip = client.hip_object.create(disk_encryption_config)
```

</div>

### Retrieving HIP Objects

<div class="termy">

<!-- termynal -->

```python
# Fetch by name and folder
hip_object = client.hip_object.fetch(name="windows-workstation", folder="Shared")
print(f"Found HIP object: {hip_object.name}")

# Get by ID
hip_by_id = client.hip_object.get(hip_object.id)
print(f"Retrieved HIP object: {hip_by_id.name}")
```

</div>

### Updating HIP Objects

<div class="termy">

<!-- termynal -->

```python
# Fetch existing HIP object
existing_hip = client.hip_object.fetch(name="encrypted-endpoints", folder="Shared")

# Add additional encryption location
if existing_hip.disk_encryption and existing_hip.disk_encryption.criteria:
    existing_hip.disk_encryption.criteria.encrypted_locations.append({
        "name": "D:",
        "encryption_state": {"is": "encrypted"}
    })

# Update description
existing_hip.description = "Updated disk encryption requirements"

# Perform update
updated_hip = client.hip_object.update(existing_hip)
```

</div>

### Listing HIP Objects

<div class="termy">

<!-- termynal -->

```python
# List with direct filter parameters
filtered_hips = client.hip_object.list(
    folder='Shared',
    criteria_types=['host_info', 'disk_encryption'],
    exact_match=True
)

# Process results
for hip in filtered_hips:
    print(f"Name: {hip.name}")
    if hip.host_info:
        print("Type: Host Info")
    elif hip.disk_encryption:
        print("Type: Disk Encryption")

# Define filter parameters as dictionary
list_params = {
    "folder": "Shared",
    "criteria_types": ["mobile_device"],
    "exclude_folders": ["Test", "Development"]
}

# List with filters as kwargs
filtered_hips = client.hip_object.list(**list_params)
```

</div>

### Deleting HIP Objects

<div class="termy">

<!-- termynal -->

```python
# Delete by ID
hip_id = "123e4567-e89b-12d3-a456-426655440000"
client.hip_object.delete(hip_id)
```

</div>

## Managing Configuration Changes

### Performing Commits

<div class="termy">

<!-- termynal -->

```python
# Prepare commit parameters
commit_params = {
    "folders": ["Shared"],
    "description": "Updated HIP objects",
    "sync": True,
    "timeout": 300  # 5 minute timeout
}

# Commit the changes
result = client.commit(**commit_params)

print(f"Commit job ID: {result.job_id}")
```

</div>

### Monitoring Jobs

<div class="termy">

<!-- termynal -->

```python
# Get status of specific job
job_status = client.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

# List recent jobs
recent_jobs = client.list_jobs(limit=10)
for job in recent_jobs.data:
    print(f"Job {job.id}: {job.type_str} - {job.status_str}")
```

</div>

## Error Handling

<div class="termy">

<!-- termynal -->

```python
from scm.client import ScmClient
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
    NameNotUniqueError,
    ObjectNotPresentError,
    ReferenceNotZeroError
)

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

try:
    # Create HIP object configuration
    hip_config = {
        "name": "test-hip",
        "folder": "Shared",
        "description": "Test HIP object",
        "host_info": {
            "criteria": {
                "managed": True
            }
        }
    }

    # Create the HIP object using the unified client
    new_hip = client.hip_object.create(hip_config)

    # Commit changes directly on the client
    result = client.commit(
        folders=["Shared"],
        description="Added test HIP object",
        sync=True
    )

    # Check job status on the client
    status = client.get_job_status(result.job_id)

except InvalidObjectError as e:
    print(f"Invalid HIP object data: {e.message}")
except NameNotUniqueError as e:
    print(f"HIP object name already exists: {e.message}")
except ObjectNotPresentError as e:
    print(f"HIP object not found: {e.message}")
except ReferenceNotZeroError as e:
    print(f"HIP object still in use: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing parameter: {e.message}")
```

</div>

## Best Practices

1. **Client Usage**
    - Use the unified `ScmClient` approach for simpler code
    - Access HIP object operations via `client.hip_object` property
    - Perform commit operations directly on the client
    - Monitor jobs directly on the client
    - Set appropriate max_limit parameters for large datasets using `hip_object_max_limit`

2. **HIP Object Design**
    - Use descriptive names for clarity
    - Define specific criteria for each type
    - Combine criteria types logically
    - Document requirements clearly
    - Keep criteria focused and minimal

3. **Container Management**
    - Always specify exactly one container
    - Use consistent container names
    - Validate container existence
    - Group related HIP objects
    - Consider inheritance patterns

4. **Performance**
    - Set appropriate max_limit values
    - Use pagination for large lists
    - Cache frequently accessed objects
    - Implement proper retry logic
    - Monitor API response times

5. **Security**
    - Follow least privilege principle
    - Validate input data
    - Use secure connection settings
    - Implement proper authentication
    - Monitor security posture changes

6. **Error Handling**
    - Implement comprehensive error handling
    - Check job status after commits
    - Log error details
    - Handle specific exceptions
    - Validate criteria before creation

## Full Script Examples

Refer to
the [hip_object.py example](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/objects/hip_object.py).

## Related Models

- [HIPObjectCreateModel](../../models/objects/hip_object_models.md#Overview)
- [HIPObjectUpdateModel](../../models/objects/hip_object_models.md#Overview)
- [HIPObjectResponseModel](../../models/objects/hip_object_models.md#Overview)
