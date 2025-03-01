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
    - [Filtering Responses](#filtering-responses)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
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

The Application service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

### Unified Client Interface (Recommended)

<div class="termy">

<!-- termynal -->

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the Application service directly through the client
# No need to create a separate Application instance
applications = client.application
```

</div>

### Traditional Service Instantiation (Legacy)

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

# Initialize Application object explicitly
applications = Application(client)
```

</div>

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

## Usage Examples

### Creating Applications

<div class="termy">

<!-- termynal -->

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

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

# Create basic application using the unified client interface
basic_app_obj = client.application.create(basic_app)

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

# Create secure application using the unified client interface
secure_app_obj = client.application.create(secure_app)
```

</div>

### Retrieving Applications

<div class="termy">

<!-- termynal -->

```python
# Fetch by name and folder using the unified client interface
app = client.application.fetch(name="custom-database", folder="Texas")
print(f"Found application: {app.name}")

# Get by ID using the unified client interface
app_by_id = client.application.get(app.id)
print(f"Retrieved application: {app_by_id.name}")
print(f"Risk level: {app_by_id.risk}")
```

</div>

### Updating Applications

<div class="termy">

<!-- termynal -->

```python
# Fetch existing application using the unified client interface
existing_app = client.application.fetch(name="custom-database", folder="Texas")

# Update attributes
existing_app.description = "Updated database application"
existing_app.risk = 4
existing_app.has_known_vulnerabilities = True
existing_app.ports = ["tcp/1521", "tcp/1522"]

# Perform update using the unified client interface
updated_app = client.application.update(existing_app)
```

</div>

### Listing Applications

<div class="termy">

<!-- termynal -->

```python
# List with direct filter parameters using the unified client interface
filtered_apps = client.application.list(
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

# List with filters as kwargs using the unified client interface
filtered_apps = client.application.list(**list_params)
```

</div>

### Filtering Responses

The `list()` method supports additional parameters to refine your query results even further. Alongside basic filters
(like `types`, `values`, and `tags`), you can leverage the `exact_match`, `exclude_folders`, and `exclude_snippets`
parameters to control which objects are included or excluded after the initial API response is fetched.

**Parameters:**

- `exact_match (bool)`: When `True`, only objects defined exactly in the specified container (`folder` or `snippet`) are returned. Inherited or propagated objects are filtered out.
- `exclude_folders (List[str])`: Provide a list of folder names that you do not want included in the results.
- `exclude_snippets (List[str])`: Provide a list of snippet values to exclude from the results.

**Examples:**

<div class="termy">

<!-- termynal -->

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Only return applications defined exactly in 'Texas' using the unified client interface
exact_applications = client.application.list(
    folder='Texas',
    exact_match=True
)

for app in exact_applications:
    print(f"Exact match: {app.name} in {app.folder}")

# Exclude all applications from the 'All' folder using the unified client interface
no_all_applications = client.application.list(
    folder='Texas',
    exclude_folders=['All']
)

for app in no_all_applications:
    assert app.folder != 'All'
    print(f"Filtered out 'All': {app.name}")

# Exclude applications that come from 'default' snippet using the unified client interface
no_default_snippet = client.application.list(
    folder='Texas',
    exclude_snippets=['default']
)

for app in no_default_snippet:
    assert app.snippet != 'default'
    print(f"Filtered out 'default' snippet: {app.name}")

# Combine exact_match with multiple exclusions using the unified client interface
combined_filters = client.application.list(
    folder='Texas',
    exact_match=True,
    exclude_folders=['All'],
    exclude_snippets=['default']
)

for app in combined_filters:
    print(f"Combined filters result: {app.name} in {app.folder}")
```

</div>

### Controlling Pagination with max_limit

The SDK supports pagination through the `max_limit` parameter, which defines how many objects are retrieved per API call. By default, `max_limit` is set to 2500. The API itself imposes a maximum allowed value of 5000. If you set `max_limit` higher than 5000, it will be capped to the API's maximum. The `list()` method will continue to iterate through all objects until all results have been retrieved. Adjusting `max_limit` can help manage retrieval performance and memory usage when working with large datasets.

<div class="termy">

<!-- termynal -->

```python
from scm.client import ScmClient
from scm.config.objects import Application

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Two options for setting max_limit:

# Option 1: Use the unified client interface but create a custom Application instance with max_limit
app_service = Application(client, max_limit=4321)
all_apps1 = app_service.list(folder='Texas')

# Option 2: Use the unified client interface directly
# This will use the default max_limit (2500)
all_apps2 = client.application.list(folder='Texas')

# Both options will auto-paginate through all available objects.
# The applications are fetched in chunks according to the max_limit.
```

</div>

### Deleting Applications

<div class="termy">

<!-- termynal -->

```python
# Delete by ID using the unified client interface
app_id = "123e4567-e89b-12d3-a456-426655440000"
client.application.delete(app_id)
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

# Commit the changes directly using the client
# Note: Commits should always be performed on the client object directly, not on service objects
result = client.commit(**commit_params)

print(f"Commit job ID: {result.job_id}")
```

</div>

### Monitoring Jobs

<div class="termy">

<!-- termynal -->

```python
# Get status of specific job directly from the client
job_status = client.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

# List recent jobs directly from the client
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

    # Create the application using the unified client interface
    new_app = client.application.create(app_config)

    # Commit changes directly from the client
    result = client.commit(
        folders=["Texas"],
        description="Added test application",
        sync=True
    )

    # Check job status directly from the client
    status = client.get_job_status(result.job_id)

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

1. **Client Usage**
    - Use the unified client interface (`client.application`) for streamlined code
    - Create a single client instance and reuse it across your application
    - Perform commit operations directly on the client object (`client.commit()`)
    - For custom max_limit settings, create a dedicated service instance if needed

2. **Application Definition**
    - Use descriptive names and categories
    - Set appropriate risk levels
    - Document security characteristics
    - Specify all relevant ports
    - Keep descriptions current

3. **Container Management**
    - Always specify exactly one container (folder or snippet)
    - Use consistent container names
    - Validate container existence
    - Group related applications

4. **Security Attributes**
    - Accurately flag security concerns
    - Update vulnerability status
    - Document evasive behaviors
    - Track certification status
    - Monitor risk levels

5. **Performance**
    - Create a single client instance and reuse it
    - Use appropriate pagination
    - Cache frequently accessed apps
    - Implement proper retry logic
    - Monitor bandwidth flags

6. **Error Handling**
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
