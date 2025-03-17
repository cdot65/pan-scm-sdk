# Dynamic User Group Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Dynamic User Group Model Attributes](#dynamic-user-group-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating Dynamic User Groups](#creating-dynamic-user-groups)
    - [Retrieving Dynamic User Groups](#retrieving-dynamic-user-groups)
    - [Updating Dynamic User Groups](#updating-dynamic-user-groups)
    - [Listing Dynamic User Groups](#listing-dynamic-user-groups)
    - [Filtering Responses](#filtering-responses)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Deleting Dynamic User Groups](#deleting-dynamic-user-groups)
7. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Related Models](#related-models)

## Overview

The `DynamicUserGroup` class provides functionality to manage dynamic user group objects in Palo Alto Networks' Strata Cloud Manager. This class inherits from `BaseObject` and provides methods for creating, retrieving, updating, and deleting dynamic user group objects that can be used for user-based policies and filtering.

## Core Methods

| Method     | Description                                   | Parameters                                        | Return Type                           |
|------------|-----------------------------------------------|---------------------------------------------------|---------------------------------------|
| `create()` | Creates a new dynamic user group object       | `data: Dict[str, Any]`                            | `DynamicUserGroupResponseModel`       |
| `get()`    | Retrieves a dynamic user group by ID          | `object_id: str`                                  | `DynamicUserGroupResponseModel`       |
| `update()` | Updates an existing dynamic user group        | `dynamic_user_group: DynamicUserGroupUpdateModel` | `DynamicUserGroupResponseModel`       |
| `delete()` | Deletes a dynamic user group                  | `object_id: str`                                  | `None`                                |
| `list()`   | Lists dynamic user groups with filtering      | `folder: str`, `**filters`                        | `List[DynamicUserGroupResponseModel]` |
| `fetch()`  | Gets dynamic user group by name and container | `name: str`, `folder: str`                        | `DynamicUserGroupResponseModel`       |

## Dynamic User Group Model Attributes

| Attribute     | Type      | Required     | Description                                 |
|---------------|-----------|--------------|---------------------------------------------|
| `name`        | str       | Yes          | Name of dynamic user group object           |
| `id`          | UUID      | Yes*         | Unique identifier (*response only)          |
| `filter`      | str       | Yes          | Filter expression for matching users        |
| `description` | str       | No           | Object description                          |
| `tag`         | List[str] | No           | List of tags                                |
| `folder`      | str       | Yes**        | Folder location (**one container required)  |
| `snippet`     | str       | Yes**        | Snippet location (**one container required) |
| `device`      | str       | Yes**        | Device location (**one container required)  |

## Exceptions

| Exception                    | HTTP Code | Description                               |
|------------------------------|-----------|-------------------------------------------|
| `InvalidObjectError`         | 400       | Invalid dynamic user group data or format |
| `MissingQueryParameterError` | 400       | Missing required parameters               |
| `NameNotUniqueError`         | 409       | Dynamic user group name already exists    |
| `ObjectNotPresentError`      | 404       | Dynamic user group not found              |
| `ReferenceNotZeroError`      | 409       | Dynamic user group still referenced       |
| `AuthenticationError`        | 401       | Authentication failed                     |
| `ServerError`                | 500       | Internal server error                     |

## Basic Configuration

<div class="termy">

<!-- termynal -->

```python
from scm.client import ScmClient

# Initialize client using the unified client approach
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the dynamic_user_group module directly through the client
# client.dynamic_user_group is automatically initialized for you
```

</div>

You can also use the traditional approach if preferred:

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.objects import DynamicUserGroup

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize DynamicUserGroup object
dynamic_user_groups = DynamicUserGroup(client)
```

</div>

## Usage Examples

### Creating Dynamic User Groups

<div class="termy">

<!-- termynal -->

```python
# Prepare dynamic user group configuration
dug_config = {
   "name": "high_risk_users",
   "filter": "tag.criticality.high",
   "description": "Users with high risk classification",
   "folder": "Security",
   "tag": ["RiskManagement", "Automation"]
}

# Create the dynamic user group object
dug = client.dynamic_user_group.create(dug_config)
print(f"Created dynamic user group: {dug.name} with ID: {dug.id}")

# Create another dynamic user group with different filter
another_dug_config = {
   "name": "external_contractors",
   "filter": "tag.user_type.contractor",
   "folder": "Security",
   "description": "All external contractor accounts"
}

# Create the dynamic user group object
another_dug = client.dynamic_user_group.create(another_dug_config)
```

</div>

### Retrieving Dynamic User Groups

<div class="termy">

<!-- termynal -->

```python
# Fetch by name and folder
dug = client.dynamic_user_group.fetch(name="high_risk_users", folder="Security")
print(f"Found dynamic user group: {dug.name}")

# Get by ID
dug_by_id = client.dynamic_user_group.get(dug.id)
print(f"Retrieved dynamic user group: {dug_by_id.name}")
```

</div>

### Updating Dynamic User Groups

<div class="termy">

<!-- termynal -->

```python
# Fetch existing dynamic user group
existing_dug = client.dynamic_user_group.fetch(name="high_risk_users", folder="Security")

# Update specific attributes
existing_dug.description = "Users with high risk assessment score"
existing_dug.filter = "tag.criticality.high or tag.risk_score.gt.80"
existing_dug.tag = ["RiskManagement", "Automation", "HighPriority"]

# Perform update
updated_dug = client.dynamic_user_group.update(existing_dug)
```

</div>

### Listing Dynamic User Groups

<div class="termy">

<!-- termynal -->

```python
# List dynamic user groups in the Security folder
all_dugs = client.dynamic_user_group.list(folder='Security')

# Process results
for dug in all_dugs:
   print(f"Name: {dug.name}, Filter: {dug.filter}")

# Pass filters directly into the list method
filtered_dugs = client.dynamic_user_group.list(
     folder='Security',
     tags=['Automation']
)

# Process results
for dug in filtered_dugs:
   print(f"Name: {dug.name}, Filter: {dug.filter}")

# Define filter parameters as a dictionary
list_params = {
   "folder": "Security",
   "filters": ["tag.criticality"]
}

# List dynamic user groups with filters as kwargs
filtered_dugs = client.dynamic_user_group.list(**list_params)

# Process results
for dug in filtered_dugs:
   print(f"Name: {dug.name}, Filter: {dug.filter}")
```

</div>

### Filtering Responses

The `list()` method supports additional parameters to refine your query results even further. Alongside basic filters
(like `tags` and `filters`), you can leverage the `exact_match`, `exclude_folders`, `exclude_snippets`, and
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
# Only return dynamic user groups defined exactly in 'Security'
exact_dugs = client.dynamic_user_group.list(
   folder='Security',
   exact_match=True
)

for dug in exact_dugs:
   print(f"Exact match: {dug.name} in {dug.folder}")

# Exclude all dynamic user groups from the 'All' folder
no_all_dugs = client.dynamic_user_group.list(
   folder='Security',
   exclude_folders=['All']
)

for dug in no_all_dugs:
   assert dug.folder != 'All'
   print(f"Filtered out 'All': {dug.name}")

# Exclude dynamic user groups that come from 'default' snippet
no_default_snippet = client.dynamic_user_group.list(
   folder='Security',
   exclude_snippets=['default']
)

for dug in no_default_snippet:
   assert dug.snippet != 'default'
   print(f"Filtered out 'default' snippet: {dug.name}")

# Combine exact_match with multiple exclusions
combined_filters = client.dynamic_user_group.list(
   folder='Security',
   exact_match=True,
   exclude_folders=['All'],
   exclude_snippets=['default'],
   exclude_devices=['DeviceA']
)

for dug in combined_filters:
   print(f"Combined filters result: {dug.name} in {dug.folder}")
```

</div>

### Controlling Pagination with max_limit

The SDK supports pagination through the `max_limit` parameter, which defines how many objects are retrieved per API call. By default, `max_limit` is set to 2500. The API itself imposes a maximum allowed value of 5000. If you set `max_limit` higher than 5000, it will be capped to the API's maximum. The `list()` method will continue to iterate through all objects until all results have been retrieved. Adjusting `max_limit` can help manage retrieval performance and memory usage when working with large datasets.

**Example:**

<div class="termy">

<!-- termynal -->

```python
# Initialize the ScmClient with a custom max_limit for dynamic user groups
# This will retrieve up to 4000 objects per API call, up to the API limit of 5000.
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
    dynamic_user_group_max_limit=4000
)

# Now when we call list(), it will use the specified max_limit for each request
# while auto-paginating through all available objects.
all_dugs = client.dynamic_user_group.list(folder='Security')

# 'all_dugs' contains all objects from 'Security', fetched in chunks of up to 4000 at a time.
```

</div>

### Deleting Dynamic User Groups

<div class="termy">

<!-- termynal -->

```python
# Delete by ID
dug_id = "123e4567-e89b-12d3-a456-426655440000"
client.dynamic_user_group.delete(dug_id)
```

</div>

## Managing Configuration Changes

### Performing Commits

<div class="termy">

<!-- termynal -->

```python
# Prepare commit parameters
commit_params = {
   "folders": ["Security"],
   "description": "Added new dynamic user groups",
   "sync": True,
   "timeout": 300  # 5 minute timeout
}

# Commit the changes directly on the client
# Note: All commit operations should be performed on the client directly
result = client.commit(**commit_params)

print(f"Commit job ID: {result.job_id}")
```

</div>

### Monitoring Jobs

<div class="termy">

<!-- termynal -->

```python
# Get status of specific job directly on the client
job_status = client.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

# List recent jobs directly on the client
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
   ObjectNotPresentError
)

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

try:
   # Create dynamic user group configuration
   dug_config = {
      "name": "test_group",
      "filter": "tag.department.it",
      "folder": "Security",
      "description": "IT department users",
      "tag": ["Test"]
   }

   # Create the dynamic user group using the unified client
   new_dug = client.dynamic_user_group.create(dug_config)

   # Commit changes directly on the client
   result = client.commit(
      folders=["Security"],
      description="Added test dynamic user group",
      sync=True
   )

   # Check job status on the client
   status = client.get_job_status(result.job_id)

except InvalidObjectError as e:
   print(f"Invalid dynamic user group data: {e.message}")
except NameNotUniqueError as e:
   print(f"Dynamic user group name already exists: {e.message}")
except ObjectNotPresentError as e:
   print(f"Dynamic user group not found: {e.message}")
except MissingQueryParameterError as e:
   print(f"Missing parameter: {e.message}")
```

</div>

## Best Practices

1. **Client Usage**
    - Use the unified `ScmClient` approach for simpler code
    - Access dynamic user group operations via `client.dynamic_user_group` property
    - Perform commit operations directly on the client
    - Monitor jobs directly on the client
    - Set appropriate max_limit parameters for large datasets using `dynamic_user_group_max_limit`

2. **Container Management**
    - Always specify exactly one container (folder, snippet, or device)
    - Use consistent container names across operations
    - Validate container existence before operations

3. **Error Handling**
    - Implement comprehensive error handling for all operations
    - Check job status after commits
    - Handle specific exceptions before generic ones
    - Log error details for troubleshooting

4. **Filter Expressions**
    - Ensure filter expressions follow the required syntax
    - Test filter expressions before implementing in production
    - Document filter expressions for future maintenance
    - Use consistent naming conventions for tags referenced in filters

5. **Performance**
    - Reuse client instances
    - Use appropriate pagination for list operations
    - Implement proper retry mechanisms
    - Cache frequently accessed objects

6. **Security**
    - Follow the least privilege principle
    - Validate input data
    - Use secure connection settings
    - Implement proper authentication handling

## Full Script Examples

Refer to
the [dynamic_user_group.py example](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/objects/dynamic_user_group.py).

## Related Models

- [DynamicUserGroupCreateModel](../../models/objects/dynamic_user_group_models.md#Overview)
- [DynamicUserGroupUpdateModel](../../models/objects/dynamic_user_group_models.md#Overview)
- [DynamicUserGroupResponseModel](../../models/objects/dynamic_user_group_models.md#Overview)
