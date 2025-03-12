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

The Address Group service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

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

# Access the AddressGroup service directly through the client
# No need to create a separate AddressGroup instance
address_groups = client.address_group
```

</div>

### Traditional Service Instantiation (Legacy)

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

# Initialize AddressGroup object explicitly
address_groups = AddressGroup(client)
```

</div>

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

## Usage Examples

### Creating Address Groups

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

# Static group configuration
static_config = {
   "name": "web_servers",
   "static": ["web-server1", "web-server2"],
   "description": "Web server group",
   "folder": "Texas",
   "tag": ["Production", "Web"]
}

# Create static group using the unified client interface
static_group = client.address_group.create(static_config)

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

# Create dynamic group using the unified client interface
dynamic_group = client.address_group.create(dynamic_config)
```

</div>

### Retrieving Address Groups

<div class="termy">

<!-- termynal -->

```python
# Fetch by name and folder using the unified client interface
group = client.address_group.fetch(name="web_servers", folder="Texas")
print(f"Found group: {group.name}")

# Get by ID using the unified client interface
group_by_id = client.address_group.get(group.id)
print(f"Retrieved group: {group_by_id.name}")
```

</div>

### Updating Address Groups

<div class="termy">

<!-- termynal -->

```python
# Fetch existing group using the unified client interface
existing_group = client.address_group.fetch(name="web_servers", folder="Texas")

# Update static members
existing_group.static = ["web-server1", "web-server2", "web-server3"]
existing_group.description = "Updated web server group"
existing_group.tag = ["Production", "Web", "Updated"]

# Perform update using the unified client interface
updated_group = client.address_group.update(existing_group)
```

</div>

### Listing Address Groups

<div class="termy">

<!-- termynal -->

```python
# List with direct filter parameters using the unified client interface
filtered_groups = client.address_group.list(
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

# List with filters as kwargs using the unified client interface
filtered_groups = client.address_group.list(**list_params)
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
exact_address_groups = client.address_group.list(
   folder='Texas',
   exact_match=True
)

for each in exact_address_groups:
   print(f"Exact match: {each.name} in {each.folder}")

# Exclude all address groups from the 'All' folder
no_all_address_groups = client.address_group.list(
   folder='Texas',
   exclude_folders=['All']
)

for each in no_all_address_groups:
   assert each.folder != 'All'
   print(f"Filtered out 'All': {each.name}")

# Exclude address groups that come from 'default' snippet
no_default_snippet = client.address_group.list(
   folder='Texas',
   exclude_snippets=['default']
)

for addr in no_default_snippet:
   assert addr.snippet != 'default'
   print(f"Filtered out 'default' snippet: {addr.name}")

# Exclude address groups associated with 'DeviceA'
no_deviceA = client.address_group.list(
   folder='Texas',
   exclude_devices=['DeviceA']
)

for each in no_deviceA:
   assert each.device != 'DeviceA'
   print(f"Filtered out 'DeviceA': {each.name}")

# Combine exact_match with multiple exclusions
combined_filters = client.address_group.list(
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
from scm.client import ScmClient
from scm.config.objects import AddressGroup

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Two options for setting max_limit:

# Option 1: Use the unified client interface but create a custom AddressGroup instance with max_limit
address_group_service = AddressGroup(client, max_limit=4321)
all_groups1 = address_group_service.list(folder='Texas')

# Option 2 (traditional approach): Create a dedicated AddressGroup instance
# This will retrieve up to 4321 objects per API call, up to the API limit of 5000.
all_groups2 = client.address_group.list(folder='Texas')

# Both options will auto-paginate through all available objects.
# 'all_groups' contains all objects from 'Texas', fetched in chunks according to the max_limit.
```

</div>

### Deleting Address Groups

<div class="termy">

<!-- termynal -->

```python
# Delete by ID using the unified client interface
group_id = "123e4567-e89b-12d3-a456-426655440000"
client.address_group.delete(group_id)
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

# Initialize client using ScmClient
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
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

   # Create the group using the unified client interface
   new_group = client.address_group.create(group_config)

   # Commit changes directly from the client
   result = client.commit(
      folders=["Texas"],
      description="Added test group",
      sync=True
   )

   # Check job status directly from the client
   status = client.get_job_status(result.job_id)

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

1. **Client Usage**
    - Use the unified client interface (`client.address_group`) for streamlined code
    - Create a single client instance and reuse it across your application
    - Perform commit operations directly on the client object (`client.commit()`)
    - For custom max_limit settings, create a dedicated service instance if needed

2. **Group Type Management**
    - Use static groups for explicit member lists
    - Use dynamic groups for tag-based filtering
    - Validate group type before creation
    - Consider member resolution time for dynamic groups

3. **Container Management**
    - Always specify exactly one container (folder, snippet, or device)
    - Use consistent container names across operations
    - Validate container existence before operations

4. **Error Handling**
    - Implement comprehensive error handling for all operations
    - Check job status after commits
    - Handle specific exceptions before generic ones
    - Log error details for troubleshooting

5. **Performance**
    - Use appropriate pagination for list operations
    - Cache frequently accessed groups
    - Implement proper retry mechanisms
    - Consider dynamic group evaluation impact

6. **Security**
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
