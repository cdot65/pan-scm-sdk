# Application Group Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Application Group Model Attributes](#application-group-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating Application Groups](#creating-application-groups)
    - [Retrieving Application Groups](#retrieving-application-groups)
    - [Updating Application Groups](#updating-application-groups)
    - [Listing Application Groups](#listing-application-groups)
    - [Filtering Responses](#filtering-responses)
    - [Deleting Application Groups](#deleting-application-groups)
7. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Full Script Examples](#full-script-examples)
11. [Related Models](#related-models)

## Overview

The `ApplicationGroup` class provides functionality to manage application groups in Palo Alto Networks' Strata Cloud
Manager. This class inherits from `BaseObject` and provides methods for creating, retrieving, updating, and deleting
application groups that organize collections of applications for use in security policies.

## Core Methods

| Method     | Description                   | Parameters                               | Return Type                           |
|------------|-------------------------------|------------------------------------------|---------------------------------------|
| `create()` | Creates a new app group       | `data: Dict[str, Any]`                   | `ApplicationGroupResponseModel`       |
| `get()`    | Retrieves a group by ID       | `object_id: str`                         | `ApplicationGroupResponseModel`       |
| `update()` | Updates an existing group     | `app_group: ApplicationGroupUpdateModel` | `ApplicationGroupResponseModel`       |
| `delete()` | Deletes a group               | `object_id: str`                         | `None`                                |
| `list()`   | Lists groups with filtering   | `folder: str`, `**filters`               | `List[ApplicationGroupResponseModel]` |
| `fetch()`  | Gets group by name and folder | `name: str`, `folder: str`               | `ApplicationGroupResponseModel`       |

## Application Group Model Attributes

| Attribute | Type      | Required | Description                                 |
|-----------|-----------|----------|---------------------------------------------|
| `name`    | str       | Yes      | Name of group (max 63 chars)                |
| `id`      | UUID      | Yes*     | Unique identifier (*response only)          |
| `members` | List[str] | Yes      | List of application names                   |
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
from scm.config.objects import ApplicationGroup

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize ApplicationGroup object
application_groups = ApplicationGroup(client)
```

</div>

## Usage Examples

### Creating Application Groups

<div class="termy">

<!-- termynal -->

```python
# Basic application group configuration
basic_group = {
    "name": "web-apps",
    "members": ["ssl", "web-browsing"],
    "folder": "Texas"
}

# Create basic group
basic_group_obj = application_groups.create(basic_group)

# Microsoft 365 application group
ms365_group = {
    "name": "microsoft-365",
    "members": [
        "ms-office365",
        "ms-exchange-online",
        "ms-sharepoint-online"
    ],
    "folder": "Texas"
}

# Create Microsoft 365 group
ms365_group_obj = application_groups.create(ms365_group)
```

</div>

### Retrieving Application Groups

<div class="termy">

<!-- termynal -->

```python
# Fetch by name and folder
group = application_groups.fetch(name="web-apps", folder="Texas")
print(f"Found group: {group.name}")

# Get by ID
group_by_id = application_groups.get(group.id)
print(f"Retrieved group: {group_by_id.name}")
print(f"Members: {', '.join(group_by_id.members)}")
```

</div>

### Updating Application Groups

<div class="termy">

<!-- termynal -->

```python
# Fetch existing group
existing_group = application_groups.fetch(name="web-apps", folder="Texas")

# Update members
existing_group.members = ["ssl", "web-browsing", "dns"]

# Perform update
updated_group = application_groups.update(existing_group)
```

</div>

### Listing Application Groups

<div class="termy">

<!-- termynal -->

```python
# List with direct filter parameters
filtered_groups = application_groups.list(
    folder='Texas',
    members=['ssl']
)

# Process results
for group in filtered_groups:
    print(f"Name: {group.name}")
    print(f"Members: {', '.join(group.members)}")

# Define filter parameters as dictionary
list_params = {
    "folder": "Texas",
    "members": ["ms-office365"]
}

# List with filters as kwargs
filtered_groups = application_groups.list(**list_params)
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
# Only return application groups defined exactly in 'Texas'
exact_application_groups = application_groups.list(
  folder='Texas',
  exact_match=True
)

for app in application_groups:
  print(f"Exact match: {app.name} in {app.folder}")

# Exclude all application groups from the 'All' folder
no_all_applications = application_groups.list(
  folder='Texas',
  exclude_folders=['All']
)

for app in no_all_application_groups:
  assert app.folder != 'All'
  print(f"Filtered out 'All': {app.name}")

# Exclude application groups that come from 'default' snippet
no_default_snippet = application_groups.list(
  folder='Texas',
  exclude_snippets=['default']
)

for app in no_default_snippet:
  assert app.snippet != 'default'
  print(f"Filtered out 'default' snippet: {app.name}")

# Exclude application groups associated with 'DeviceA'
no_deviceA = application_groups.list(
  folder='Texas',
  exclude_devices=['DeviceA']
)

for app in no_deviceA:
  assert app.device != 'DeviceA'
  print(f"Filtered out 'DeviceA': {app.name}")

# Combine exact_match with multiple exclusions
combined_filters = application_groups.list(
  folder='Texas',
  exact_match=True,
  exclude_folders=['All'],
  exclude_snippets=['default'],
  exclude_devices=['DeviceA']
)

for app in combined_filters:
  print(f"Combined filters result: {app.name} in {app.folder}")
```

### Deleting Application Groups

<div class="termy">

<!-- termynal -->

```python
# Delete by ID
group_id = "123e4567-e89b-12d3-a456-426655440000"
application_groups.delete(group_id)
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
    "description": "Updated application groups",
    "sync": True,
    "timeout": 300  # 5 minute timeout
}

# Commit the changes
result = application_groups.commit(**commit_params)

print(f"Commit job ID: {result.job_id}")
```

</div>

### Monitoring Jobs

<div class="termy">

<!-- termynal -->

```python
# Get status of specific job
job_status = application_groups.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

# List recent jobs
recent_jobs = application_groups.list_jobs(limit=10)
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
        "name": "test_group",
        "members": ["ssl", "web-browsing"],
        "folder": "Texas"
    }

    # Create the group
    new_group = application_groups.create(group_config)

    # Commit changes
    result = application_groups.commit(
        folders=["Texas"],
        description="Added test group",
        sync=True
    )

    # Check job status
    status = application_groups.get_job_status(result.job_id)

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

1. **Group Management**
    - Use descriptive group names
    - Organize related applications together
    - Keep member lists current
    - Document group purposes
    - Review group memberships regularly

2. **Container Management**
    - Always specify exactly one container (folder, snippet, or device)
    - Use consistent container names
    - Validate container existence
    - Group related configurations

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
    - Batch related changes

5. **Security**
    - Follow least privilege principle
    - Validate input data
    - Use secure connection settings
    - Implement proper authentication
    - Monitor policy references

## Full Script Examples

Refer to
the [application_group.py example](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/objects/application_group.py).

## Related Models

- [ApplicationGroupCreateModel](../../models/objects/application_group_models.md#Overview)
- [ApplicationGroupUpdateModel](../../models/objects/application_group_models.md#Overview)
- [ApplicationGroupResponseModel](../../models/objects/application_group_models.md#Overview)