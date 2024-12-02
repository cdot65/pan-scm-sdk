# Application Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Application Model Attributes](#application-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating Applications](#creating-applications)
    - [Retrieving Applications](#retrieving-applications)
    - [Updating Applications](#updating-applications)
    - [Listing Applications](#listing-applications)
    - [Deleting Applications](#deleting-applications)
7. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Full Script Examples](#full-script-examples)
11. [Related Models](#related-models)

## Overview

The `Application` class provides functionality to manage custom application definitions in Palo Alto Networks' Strata
Cloud Manager. This class inherits from `BaseObject` and provides methods for creating, retrieving, updating, and
deleting custom applications with specific characteristics, risk levels, and behaviors.

## Core Methods

| Method     | Description                     | Parameters                            | Return Type                      |
|------------|---------------------------------|---------------------------------------|----------------------------------|
| `create()` | Creates a new application       | `data: Dict[str, Any]`                | `ApplicationResponseModel`       |
| `get()`    | Retrieves an application by ID  | `object_id: str`                      | `ApplicationResponseModel`       |
| `update()` | Updates an existing application | `application: ApplicationUpdateModel` | `ApplicationResponseModel`       |
| `delete()` | Deletes an application          | `object_id: str`                      | `None`                           |
| `list()`   | Lists apps with filtering       | `folder: str`, `**filters`            | `List[ApplicationResponseModel]` |
| `fetch()`  | Gets app by name and container  | `name: str`, `folder: str`            | `ApplicationResponseModel`       |

## Application Model Attributes

| Attribute                   | Type      | Required | Description                                 |
|-----------------------------|-----------|----------|---------------------------------------------|
| `name`                      | str       | Yes      | Name of application (max 63 chars)          |
| `id`                        | UUID      | Yes*     | Unique identifier (*response only)          |
| `category`                  | str       | Yes      | High-level category (max 50 chars)          |
| `subcategory`               | str       | Yes      | Specific sub-category (max 50 chars)        |
| `technology`                | str       | Yes      | Underlying technology (max 50 chars)        |
| `risk`                      | int       | Yes      | Risk level (1-5)                            |
| `description`               | str       | No       | Description (max 1023 chars)                |
| `ports`                     | List[str] | No       | Associated TCP/UDP ports                    |
| `folder`                    | str       | Yes**    | Folder location (**one container required)  |
| `snippet`                   | str       | Yes**    | Snippet location (**one container required) |
| `evasive`                   | bool      | No       | Uses evasive techniques                     |
| `pervasive`                 | bool      | No       | Widely used                                 |
| `excessive_bandwidth_use`   | bool      | No       | Uses excessive bandwidth                    |
| `used_by_malware`           | bool      | No       | Used by malware                             |
| `transfers_files`           | bool      | No       | Transfers files                             |
| `has_known_vulnerabilities` | bool      | No       | Has known vulnerabilities                   |
| `tunnels_other_apps`        | bool      | No       | Tunnels other applications                  |
| `prone_to_misuse`           | bool      | No       | Prone to misuse                             |
| `no_certifications`         | bool      | No       | Lacks certifications                        |

## Exceptions

| Exception                    | HTTP Code | Description                        |
|------------------------------|-----------|------------------------------------|
| `InvalidObjectError`         | 400       | Invalid application data or format |
| `MissingQueryParameterError` | 400       | Missing required parameters        |
| `NameNotUniqueError`         | 409       | Application name already exists    |
| `ObjectNotPresentError`      | 404       | Application not found              |
| `ReferenceNotZeroError`      | 409       | Application still referenced       |
| `AuthenticationError`        | 401       | Authentication failed              |
| `ServerError`                | 500       | Internal server error              |

## Basic Configuration

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.objects import Application

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize Application object
applications = Application(client)
```

</div>

## Usage Examples

### Creating Applications

<div class="termy">

<!-- termynal -->

```python
# Basic application configuration
basic_app = {
    "name": "custom-database",
    "category": "business-systems",
    "subcategory": "database",
    "technology": "client-server",
    "risk": 3,
    "description": "Custom database application",
    "ports": ["tcp/1521"],
    "folder": "Texas"
}

# Create basic application
basic_app_obj = applications.create(basic_app)

# Advanced application with security attributes
secure_app = {
    "name": "secure-chat",
    "category": "collaboration",
    "subcategory": "instant-messaging",
    "technology": "client-server",
    "risk": 2,
    "description": "Secure internal chat application",
    "ports": ["tcp/8443"],
    "folder": "Texas",
    "transfers_files": True,
    "has_known_vulnerabilities": False,
    "evasive": False,
    "pervasive": True
}

# Create secure application
secure_app_obj = applications.create(secure_app)
```

</div>

### Retrieving Applications

<div class="termy">

<!-- termynal -->

```python
# Fetch by name and folder
app = applications.fetch(name="custom-database", folder="Texas")
print(f"Found application: {app.name}")

# Get by ID
app_by_id = applications.get(app.id)
print(f"Retrieved application: {app_by_id.name}")
print(f"Risk level: {app_by_id.risk}")
```

</div>

### Updating Applications

<div class="termy">

<!-- termynal -->

```python
# Fetch existing application
existing_app = applications.fetch(name="custom-database", folder="Texas")

# Update attributes
existing_app.description = "Updated database application"
existing_app.risk = 4
existing_app.has_known_vulnerabilities = True
existing_app.ports = ["tcp/1521", "tcp/1522"]

# Perform update
updated_app = applications.update(existing_app)
```

</div>

### Listing Applications

<div class="termy">

<!-- termynal -->

```python
# List with direct filter parameters
filtered_apps = applications.list(
    folder='Texas',
    category=['business-systems'],
    risk=[3, 4, 5]
)

# Process results
for app in filtered_apps:
    print(f"Name: {app.name}")
    print(f"Category: {app.category}")
    print(f"Risk: {app.risk}")

# Define filter parameters as dictionary
list_params = {
    "folder": "Texas",
    "technology": ["client-server"],
    "subcategory": ["database"]
}

# List with filters as kwargs
filtered_apps = applications.list(**list_params)
```

</div>

### Deleting Applications

<div class="termy">

<!-- termynal -->

```python
# Delete by ID
app_id = "123e4567-e89b-12d3-a456-426655440000"
applications.delete(app_id)
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
    "description": "Updated application definitions",
    "sync": True,
    "timeout": 300  # 5 minute timeout
}

# Commit the changes
result = applications.commit(**commit_params)

print(f"Commit job ID: {result.job_id}")
```

</div>

### Monitoring Jobs

<div class="termy">

<!-- termynal -->

```python
# Get status of specific job
job_status = applications.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

# List recent jobs
recent_jobs = applications.list_jobs(limit=10)
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
    # Create application configuration
    app_config = {
        "name": "test-app",
        "category": "business-systems",
        "subcategory": "database",
        "technology": "client-server",
        "risk": 3,
        "folder": "Texas",
        "description": "Test application",
        "ports": ["tcp/1521"]
    }

    # Create the application
    new_app = applications.create(app_config)

    # Commit changes
    result = applications.commit(
        folders=["Texas"],
        description="Added test application",
        sync=True
    )

    # Check job status
    status = applications.get_job_status(result.job_id)

except InvalidObjectError as e:
    print(f"Invalid application data: {e.message}")
except NameNotUniqueError as e:
    print(f"Application name already exists: {e.message}")
except ObjectNotPresentError as e:
    print(f"Application not found: {e.message}")
except ReferenceNotZeroError as e:
    print(f"Application still in use: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing parameter: {e.message}")
```

</div>

## Best Practices

1. **Application Definition**
    - Use descriptive names and categories
    - Set appropriate risk levels
    - Document security characteristics
    - Specify all relevant ports
    - Keep descriptions current

2. **Container Management**
    - Always specify exactly one container (folder or snippet)
    - Use consistent container names
    - Validate container existence
    - Group related applications

3. **Security Attributes**
    - Accurately flag security concerns
    - Update vulnerability status
    - Document evasive behaviors
    - Track certification status
    - Monitor risk levels

4. **Performance**
    - Use appropriate pagination
    - Cache frequently accessed apps
    - Implement proper retry logic
    - Monitor bandwidth flags

5. **Error Handling**
    - Validate input data
    - Handle specific exceptions
    - Log error details
    - Monitor commit status
    - Track job completion

## Full Script Examples

Refer to
the [application.py example](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/objects/application.py).

## Related Models

- [ApplicationCreateModel](../../models/objects/application_models.md#Overview)
- [ApplicationUpdateModel](../../models/objects/application_models.md#Overview)
- [ApplicationResponseModel](../../models/objects/application_models.md#Overview)