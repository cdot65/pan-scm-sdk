# External Dynamic Lists Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [EDL Model Attributes](#edl-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating EDLs](#creating-edls)
    - [Retrieving EDLs](#retrieving-edls)
    - [Updating EDLs](#updating-edls)
    - [Listing EDLs](#listing-edls)
    - [Filtering Responses](#filtering-responses)
    - [Deleting EDLs](#deleting-edls)
7. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Full Script Examples](#full-script-examples)
11. [Related Models](#related-models)

## Overview

The `ExternalDynamicLists` class provides functionality to manage External Dynamic Lists (EDLs) in Palo Alto Networks' Strata
Cloud Manager. This class inherits from `BaseObject` and provides methods for creating, retrieving, updating, and deleting
EDLs of various types including IP, Domain, URL, IMSI, and IMEI lists with configurable update intervals.

## Core Methods

| Method     | Description                | Parameters                                    | Return Type                            |
|------------|----------------------------|-----------------------------------------------|----------------------------------------|
| `create()` | Creates a new EDL         | `data: Dict[str, Any]`                        | `ExternalDynamicListsResponseModel`    |
| `get()`    | Retrieves an EDL by ID    | `edl_id: str`                                 | `ExternalDynamicListsResponseModel`    |
| `update()` | Updates an existing EDL   | `edl: ExternalDynamicListsUpdateModel`       | `ExternalDynamicListsResponseModel`    |
| `delete()` | Deletes an EDL            | `edl_id: str`                                 | `None`                                 |
| `list()`   | Lists EDLs with filtering | `folder: str`, `**filters`                    | `List[ExternalDynamicListsResponseModel]` |
| `fetch()`  | Gets EDL by name          | `name: str`, `folder: str`                    | `ExternalDynamicListsResponseModel`    |

## EDL Model Attributes

| Attribute           | Type         | Required     | Description                                 |
|--------------------|--------------|--------------|---------------------------------------------|
| `name`             | str          | Yes          | Name of EDL (max 63 chars)                  |
| `id`               | UUID         | Yes*         | Unique identifier (*response only)          |
| `type`             | TypeUnion    | Yes          | EDL type configuration                      |
| `url`              | str          | Yes          | Source URL for EDL content                  |
| `description`      | str          | No           | Description (max 255 chars)                 |
| `exception_list`   | List[str]    | No           | List of exceptions                          |
| `auth`             | AuthModel    | No           | Authentication credentials                   |
| `recurring`        | RecurringUnion| Yes          | Update schedule configuration               |
| `folder`           | str          | Yes**        | Folder location (**one container required)  |
| `snippet`          | str          | Yes**        | Snippet location (**one container required) |
| `device`           | str          | Yes**        | Device location (**one container required)  |

## Exceptions

| Exception                    | HTTP Code | Description                    |
|------------------------------|-----------|--------------------------------|
| `InvalidObjectError`         | 400       | Invalid EDL data or format     |
| `MissingQueryParameterError` | 400       | Missing required parameters    |
| `NameNotUniqueError`         | 409       | EDL name already exists        |
| `ObjectNotPresentError`      | 404       | EDL not found                  |
| `ReferenceNotZeroError`      | 409       | EDL still referenced           |
| `AuthenticationError`        | 401       | Authentication failed          |
| `ServerError`                | 500       | Internal server error          |

## Basic Configuration

<div class="termy">

<!-- termynal -->
```python
from scm.client import Scm
from scm.config.objects import ExternalDynamicLists

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize EDL object
edls = ExternalDynamicLists(client)
```

</div>

## Usage Examples

### Creating EDLs

<div class="termy">

<!-- termynal -->
```python
# IP-based EDL with daily updates
ip_edl_config = {
    "name": "malicious-ips",
    "folder": "Texas",
    "type": {
        "ip": {
            "url": "https://threatfeeds.example.com/ips.txt",
            "description": "Known malicious IPs",
            "recurring": {
                "daily": {
                    "at": "03"
                }
            },
            "auth": {
                "username": "user123",
                "password": "pass123"
            }
        }
    }
}

# Create IP EDL
ip_edl = edls.create(ip_edl_config)

# Domain-based EDL with hourly updates
domain_edl_config = {
    "name": "blocked-domains",
    "folder": "Texas",
    "type": {
        "domain": {
            "url": "https://threatfeeds.example.com/domains.txt",
            "description": "Blocked domains list",
            "recurring": {
                "hourly": {}
            },
            "expand_domain": True
        }
    }
}

# Create domain EDL
domain_edl = edls.create(domain_edl_config)
```

</div>

### Retrieving EDLs

<div class="termy">

<!-- termynal -->
```python
# Fetch by name and folder
edl = edls.fetch(name="malicious-ips", folder="Texas")
print(f"Found EDL: {edl.name}")

# Get by ID
edl_by_id = edls.get(edl.id)
print(f"Retrieved EDL: {edl_by_id.name}")
```

</div>

### Updating EDLs

<div class="termy">

<!-- termynal -->
```python
# Fetch existing EDL
existing_edl = edls.fetch(name="malicious-ips", folder="Texas")

# Update attributes
existing_edl.description = "Updated malicious IP list"
existing_edl.type.ip.recurring = {
    "five_minute": {}
}

# Perform update
updated_edl = edls.update(existing_edl)
```

</div>

### Listing EDLs

<div class="termy">

<!-- termynal -->
```python
# List with direct filter parameters
filtered_edls = edls.list(
    folder='Texas',
    types=['ip', 'domain']
)

# Process results
for edl in filtered_edls:
    print(f"Name: {edl.name}")
    if hasattr(edl.type, 'ip'):
        print(f"Type: IP, URL: {edl.type.ip.url}")
    elif hasattr(edl.type, 'domain'):
        print(f"Type: Domain, URL: {edl.type.domain.url}")

# Define filter parameters as dictionary
list_params = {
    "folder": "Texas",
    "types": ["url"]
}

# List with filters as kwargs
filtered_edls = edls.list(**list_params)
```

</div>


### Filtering Responses

The `list()` method supports additional parameters to refine your query results even further. Alongside basic filters
(like `types`, `values`, and `tags`), you can leverage the `exact_match`, `exclude_folders`, `exclude_snippets`, and
`exclude_devices` parameters to control which objects are included or excluded after the initial API response is fetched.

**Parameters:**
- `exact_match (bool)`: When `True`, only objects defined exactly in the specified container (`folder`, `snippet`, or `device`) are returned. Inherited or propagated objects are filtered out.
- `exclude_folders (List[str])`: Provide a list of folder names that you do not want included in the results.
- `exclude_snippets (List[str])`: Provide a list of snippet values to exclude from the results.
- `exclude_devices (List[str])`: Provide a list of device values to exclude from the results.

**Examples:**

<div class="termy">

<!-- termynal -->

```python
# Only return edls defined exactly in 'Texas'
exact_edls = edl.list(
  folder='Texas',
  exact_match=True
)

for app in exact_edls:
  print(f"Exact match: {app.name} in {app.folder}")

# Exclude all edls from the 'All' folder
no_all_edls = edls.list(
  folder='Texas',
  exclude_folders=['All']
)

for app in no_all_edls:
  assert app.folder != 'All'
  print(f"Filtered out 'All': {app.name}")

# Exclude edls that come from 'default' snippet
no_default_snippet = edls.list(
  folder='Texas',
  exclude_snippets=['default']
)

for app in no_default_snippet:
  assert app.snippet != 'default'
  print(f"Filtered out 'default' snippet: {app.name}")

# Exclude edls associated with 'DeviceA'
no_deviceA = edls.list(
  folder='Texas',
  exclude_devices=['DeviceA']
)

for app in no_deviceA:
  assert app.device != 'DeviceA'
  print(f"Filtered out 'DeviceA': {app.name}")

# Combine exact_match with multiple exclusions
combined_filters = edls.list(
  folder='Texas',
  exact_match=True,
  exclude_folders=['All'],
  exclude_snippets=['default'],
  exclude_devices=['DeviceA']
)

for app in combined_filters:
  print(f"Combined filters result: {app.name} in {app.folder}")
```

### Deleting EDLs

<div class="termy">

<!-- termynal -->
```python
# Delete by ID
edl_id = "123e4567-e89b-12d3-a456-426655440000"
edls.delete(edl_id)
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
    "description": "Updated EDL configurations",
    "sync": True,
    "timeout": 300  # 5 minute timeout
}

# Commit the changes
result = edls.commit(**commit_params)

print(f"Commit job ID: {result.job_id}")
```

</div>

### Monitoring Jobs

<div class="termy">

<!-- termynal -->
```python
# Get status of specific job
job_status = edls.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

# List recent jobs
recent_jobs = edls.list_jobs(limit=10)
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
    # Create EDL configuration
    edl_config = {
        "name": "test-edl",
        "folder": "Texas",
        "type": {
            "ip": {
                "url": "https://example.com/ips.txt",
                "description": "Test IP list",
                "recurring": {
                    "daily": {
                        "at": "03"
                    }
                }
            }
        }
    }

    # Create the EDL
    new_edl = edls.create(edl_config)

    # Commit changes
    result = edls.commit(
        folders=["Texas"],
        description="Added test EDL",
        sync=True
    )

    # Check job status
    status = edls.get_job_status(result.job_id)

except InvalidObjectError as e:
    print(f"Invalid EDL data: {e.message}")
except NameNotUniqueError as e:
    print(f"EDL name already exists: {e.message}")
except ObjectNotPresentError as e:
    print(f"EDL not found: {e.message}")
except ReferenceNotZeroError as e:
    print(f"EDL still in use: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing parameter: {e.message}")
```

</div>

## Best Practices

1. **EDL Configuration**
    - Use descriptive names
    - Set appropriate update intervals
    - Configure authentication when needed
    - Validate source URLs
    - Monitor update status

2. **Container Management**
    - Always specify exactly one container
    - Use consistent container names
    - Validate container existence
    - Group related EDLs

3. **Update Scheduling**
    - Choose appropriate intervals
    - Consider source update frequency
    - Stagger updates for multiple EDLs
    - Monitor update success
    - Handle failures gracefully

4. **Performance**
    - Use appropriate pagination
    - Cache frequently accessed EDLs
    - Monitor EDL sizes
    - Consider update impact
    - Implement retry logic

5. **Security**
    - Validate source URLs
    - Use HTTPS where possible
    - Secure credentials
    - Monitor for malicious content
    - Regular audits

## Full Script Examples

Refer to
the [external_dynamic_lists.py example](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/objects/external_dynamic_lists.py).

## Related Models

- [ExternalDynamicListsCreateModel](../../models/objects/external_dynamic_lists_models.md#Overview)
- [ExternalDynamicListsUpdateModel](../../models/objects/external_dynamic_lists_models.md#Overview)
- [ExternalDynamicListsResponseModel](../../models/objects/external_dynamic_lists_models.md#Overview)
