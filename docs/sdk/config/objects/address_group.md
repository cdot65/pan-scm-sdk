# Address Group Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Address Group Model Attributes](#address-group-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating Address Groups](#creating-address-groups)
    - [Retrieving Address Groups](#retrieving-address-groups)
    - [Updating Address Groups](#updating-address-groups)
    - [Listing Address Groups](#listing-address-groups)
    - [Filtering Responses](#filtering-responses)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Deleting Address Groups](#deleting-address-groups)
7. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Full Script Examples](#full-script-examples)
11. [Related Models](#related-models)

## Overview

The `AddressGroup` class provides functionality to manage address groups in Palo Alto Networks' Strata Cloud Manager.
This
class inherits from `BaseObject` and provides methods for creating, retrieving, updating, and deleting address groups
that can be either static (explicit list of addresses) or dynamic (tag-based filters).

## Core Methods

| Method     | Description                      | Parameters                               | Return Type                       |
|------------|----------------------------------|------------------------------------------|-----------------------------------|
| `create()` | Creates a new address group      | `data: Dict[str, Any]`                   | `AddressGroupResponseModel`       |
| `get()`    | Retrieves a group by ID          | `object_id: str`                         | `AddressGroupResponseModel`       |
| `update()` | Updates an existing group        | `address_group: AddressGroupUpdateModel` | `AddressGroupResponseModel`       |
| `delete()` | Deletes a group                  | `object_id: str`                         | `None`                            |
| `list()`   | Lists groups with filtering      | `folder: str`, `**filters`               | `List[AddressGroupResponseModel]` |
| `fetch()`  | Gets group by name and container | `name: str`, `folder: str`               | `AddressGroupResponseModel`       |

## Address Group Model Attributes

| Attribute     | Type          | Required     | Description                                 |
|---------------|---------------|--------------|---------------------------------------------|
| `name`        | str           | Yes          | Name of group (max 63 chars)                |
| `id`          | UUID          | Yes*         | Unique identifier (*response only)          |
| `static`      | List[str]     | One Required | List of static addresses                    |
| `dynamic`     | DynamicFilter | One Required | Tag-based filter for dynamic membership     |
| `description` | str           | No           | Object description (max 1023 chars)         |
| `tag`         | List[str]     | No           | List of tags (max 64 chars each)            |
| `folder`      | str           | Yes**        | Folder location (**one container required)  |
| `snippet`     | str           | Yes**        | Snippet location (**one container required) |
| `device`      | str           | Yes**        | Device location (**one container required)  |

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
from scm.config.objects import AddressGroup

# Initialize client
client = Scm(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Initialize AddressGroup object
address_groups = AddressGroup(client)
```

</div>

## Usage Examples

### Creating Address Groups

<div class="termy">

<!-- termynal -->

```python
# Static group configuration
static_config = {
   "name": "web_servers",
   "static": ["web-server1", "web-server2"],
   "description": "Web server group",
   "folder": "Texas",
   "tag": ["Production", "Web"]
}

# Create static group
static_group = address_groups.create(static_config)

# Dynamic group configuration
dynamic_config = {
   "name": "python_servers",
   "dynamic": {
      "filter": "'Python' and 'Production'"
   },
   "description": "Python production servers",
   "folder": "Texas",
   "tag": ["Automation"]
}

# Create dynamic group
dynamic_group = address_groups.create(dynamic_config)
```

</div>

### Retrieving Address Groups

<div class="termy">

<!-- termynal -->

```python
# Fetch by name and folder
group = address_groups.fetch(name="web_servers", folder="Texas")
print(f"Found group: {group.name}")

# Get by ID
group_by_id = address_groups.get(group.id)
print(f"Retrieved group: {group_by_id.name}")
```

</div>

### Updating Address Groups

<div class="termy">

<!-- termynal -->

```python
# Fetch existing group
existing_group = address_groups.fetch(name="web_servers", folder="Texas")

# Update static members
existing_group.static = ["web-server1", "web-server2", "web-server3"]
existing_group.description = "Updated web server group"
existing_group.tag = ["Production", "Web", "Updated"]

# Perform update
updated_group = address_groups.update(existing_group)
```

</div>

### Listing Address Groups

<div class="termy">

<!-- termynal -->

```python
# List with direct filter parameters
filtered_groups = address_groups.list(
   folder='Texas',
   types=['static'],
   tags=['Production']
)

# Process results
for group in filtered_groups:
   print(f"Name: {group.name}")
   if group.static:
      print(f"Members: {', '.join(group.static)}")
   elif group.dynamic:
      print(f"Filter: {group.dynamic.filter}")

# Define filter parameters as dictionary
list_params = {
   "folder": "Texas",
   "types": ["dynamic"],
   "tags": ["Automation"]
}

# List with filters as kwargs
filtered_groups = address_groups.list(**list_params)
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
# Only return address groups defined exactly in 'Texas'
exact_address_groups = address_groups.list(
   folder='Texas',
   exact_match=True
)

for each in exact_address_groups:
   print(f"Exact match: {each.name} in {each.folder}")

# Exclude all address groups from the 'All' folder
no_all_address_groups = address_groups.list(
   folder='Texas',
   exclude_folders=['All']
)

for each in no_all_address_groups:
   assert each.folder != 'All'
   print(f"Filtered out 'All': {each.name}")

# Exclude address groups that come from 'default' snippet
no_default_snippet = address_groups.list(
   folder='Texas',
   exclude_snippets=['default']
)

for addr in no_default_snippet:
   assert addr.snippet != 'default'
   print(f"Filtered out 'default' snippet: {addr.name}")

# Exclude address groups associated with 'DeviceA'
no_deviceA = address_groups.list(
   folder='Texas',
   exclude_devices=['DeviceA']
)

for each in no_deviceA:
   assert each.device != 'DeviceA'
   print(f"Filtered out 'DeviceA': {each.name}")

# Combine exact_match with multiple exclusions
combined_filters = address_groups.list(
   folder='Texas',
   exact_match=True,
   exclude_folders=['All'],
   exclude_snippets=['default'],
   exclude_devices=['DeviceA']
)

for each in combined_filters:
   print(f"Combined filters result: {each.name} in {each.folder}")
```

</div>

### Controlling Pagination with max_limit

The SDK supports pagination through the `max_limit` parameter, which defines how many objects are retrieved per API call. By default, `max_limit` is set to 2500. The API itself imposes a maximum allowed value of 5000. If you set `max_limit` higher than 5000, it will be capped to the API's maximum. The `list()` method will continue to iterate through all objects until all results have been retrieved. Adjusting `max_limit` can help manage retrieval performance and memory usage when working with large datasets.

**Example:**

<div class="termy">

<!-- termynal -->

```python
# Initialize the AddressGroup object with a custom max_limit
# This will retrieve up to 4321 objects per API call, up to the API limit of 5000.
address_group_client = AddressGroup(api_client=client, max_limit=4321)

# Now when we call list(), it will use the specified max_limit for each request
# while auto-paginating through all available objects.
all_groups = address_group_client.list(folder='Texas')

# 'all_groups' contains all objects from 'Texas', fetched in chunks of up to 4321 at a time.
```

</div>

### Deleting Address Groups

<div class="termy">

<!-- termynal -->

```python
# Delete by ID
group_id = "123e4567-e89b-12d3-a456-426655440000"
address_groups.delete(group_id)
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
   "description": "Updated address groups",
   "sync": True,
   "timeout": 300  # 5 minute timeout
}

# Commit the changes
result = address_groups.commit(**commit_params)

print(f"Commit job ID: {result.job_id}")
```

</div>

### Monitoring Jobs

<div class="termy">

<!-- termynal -->

```python
# Get status of specific job
job_status = address_groups.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

# List recent jobs
recent_jobs = address_groups.list_jobs(limit=10)
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
      "static": ["server1", "server2"],
      "folder": "Texas",
      "description": "Test server group",
      "tag": ["Test"]
   }
   
   # Create the group
   new_group = address_groups.create(group_config)
   
   # Commit changes
   result = address_groups.commit(
      folders=["Texas"],
      description="Added test group",
      sync=True
   )
   
   # Check job status
   status = address_groups.get_job_status(result.job_id)

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

1. **Group Type Management**
    - Use static groups for explicit member lists
    - Use dynamic groups for tag-based filtering
    - Validate group type before creation
    - Consider member resolution time for dynamic groups

2. **Container Management**
    - Always specify exactly one container (folder, snippet, or device)
    - Use consistent container names across operations
    - Validate container existence before operations

3. **Error Handling**
    - Implement comprehensive error handling for all operations
    - Check job status after commits
    - Handle specific exceptions before generic ones
    - Log error details for troubleshooting

4. **Performance**
    - Use appropriate pagination for list operations
    - Cache frequently accessed groups
    - Implement proper retry mechanisms
    - Consider dynamic group evaluation impact

5. **Security**
    - Follow least privilege principle
    - Validate input data
    - Use secure connection settings
    - Implement proper authentication handling

## Full Script Examples

Refer to
the [address_group.py example](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/objects/address_group.py).

## Related Models

- [AddressGroupCreateModel](../../models/objects/address_group_models.md#Overview)
- [AddressGroupUpdateModel](../../models/objects/address_group_models.md#Overview)
- [AddressGroupResponseModel](../../models/objects/address_group_models.md#Overview)
