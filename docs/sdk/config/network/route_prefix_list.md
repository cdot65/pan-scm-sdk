# Route Prefix List Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Route Prefix List Model Attributes](#route-prefix-list-model-attributes)
4. [IPv4 Prefix List Configuration](#ipv4-prefix-list-configuration)
5. [Exceptions](#exceptions)
6. [Basic Configuration](#basic-configuration)
7. [Usage Examples](#usage-examples)
    - [Creating Route Prefix Lists](#creating-route-prefix-lists)
    - [Retrieving Route Prefix Lists](#retrieving-route-prefix-lists)
    - [Updating Route Prefix Lists](#updating-route-prefix-lists)
    - [Listing Route Prefix Lists](#listing-route-prefix-lists)
    - [Filtering Responses](#filtering-responses)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Deleting Route Prefix Lists](#deleting-route-prefix-lists)
8. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
9. [Error Handling](#error-handling)
10. [Best Practices](#best-practices)
11. [Related Models](#related-models)

## Overview

The `RoutePrefixList` class manages route prefix list objects in Palo Alto Networks' Strata Cloud Manager. It extends from `BaseObject` and offers methods to create, retrieve, update, list, fetch, and delete route prefix lists. These lists define prefix-based permit or deny rules with optional greater-than-or-equal (ge) and less-than-or-equal (le) prefix length qualifiers, used for route filtering in BGP and OSPF configurations.

## Core Methods

| Method     | Description                                                     | Parameters                                                                                                                       | Return Type                          |
|------------|-----------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|--------------------------------------|
| `create()` | Creates a new route prefix list                                 | `data: Dict[str, Any]`                                                                                                           | `RoutePrefixListResponseModel`       |
| `get()`    | Retrieves a route prefix list by its unique ID                  | `object_id: str`                                                                                                                 | `RoutePrefixListResponseModel`       |
| `update()` | Updates an existing route prefix list                           | `resource: RoutePrefixListUpdateModel`                                                                                           | `RoutePrefixListResponseModel`       |
| `list()`   | Lists route prefix lists with optional filtering                | `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`, `exact_match: bool = False`, plus additional filters | `List[RoutePrefixListResponseModel]` |
| `fetch()`  | Fetches a single route prefix list by name within a container   | `name: str`, `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`                                          | `RoutePrefixListResponseModel`       |
| `delete()` | Deletes a route prefix list by its ID                           | `object_id: str`                                                                                                                 | `None`                               |

## Route Prefix List Model Attributes

| Attribute     | Type                  | Required | Default | Description                                         |
|---------------|-----------------------|----------|---------|-----------------------------------------------------|
| `name`        | str                   | Yes      | None    | Filter prefix list name                             |
| `id`          | UUID                  | Yes*     | None    | Unique identifier (*response/update only)           |
| `description` | str                   | No       | None    | Description                                         |
| `ipv4`        | RoutePrefixListIpv4   | No       | None    | IPv4 prefix list configuration                      |
| `folder`      | str                   | No**     | None    | Folder location. Max 64 chars                       |
| `snippet`     | str                   | No**     | None    | Snippet location. Max 64 chars                      |
| `device`      | str                   | No**     | None    | Device location. Max 64 chars                       |

\* Only required for update and response models
\** Exactly one container (folder/snippet/device) must be provided for create operations

## IPv4 Prefix List Configuration

The `ipv4` attribute wraps prefix list entries that define permit/deny rules based on network prefixes.

### RoutePrefixListIpv4

| Attribute    | Type                           | Required | Description              |
|--------------|--------------------------------|----------|--------------------------|
| `ipv4_entry` | List[RoutePrefixListIpv4Entry] | No       | IPv4 prefix list entries |

### RoutePrefixListIpv4Entry

| Attribute | Type                  | Required | Description                      |
|-----------|-----------------------|----------|----------------------------------|
| `name`    | int                   | No       | Sequence number (1-65535)        |
| `action`  | str                   | No       | Action: "deny" or "permit"       |
| `prefix`  | RoutePrefixListPrefix | No       | Prefix configuration             |

### RoutePrefixListPrefix (oneOf)

| Attribute | Type                        | Required | Description                                       |
|-----------|-----------------------------|----------|---------------------------------------------------|
| `network` | str                         | No       | Network "any" to match all (mutually exclusive with entry) |
| `entry`   | RoutePrefixListPrefixEntry  | No       | Prefix entry with network and ge/le (mutually exclusive with network) |

### RoutePrefixListPrefixEntry

| Attribute                | Type | Required | Description                              |
|--------------------------|------|----------|------------------------------------------|
| `network`                | str  | No       | Network address (e.g., "10.0.0.0/8")    |
| `greater_than_or_equal`  | int  | No       | Greater than or equal prefix length (0-32) |
| `less_than_or_equal`     | int  | No       | Less than or equal prefix length (0-32)  |

## Exceptions

| Exception                    | HTTP Code | Description                                                                   |
|------------------------------|-----------|-------------------------------------------------------------------------------|
| `InvalidObjectError`         | 400       | Thrown when provided data or parameters are invalid                           |
| `MissingQueryParameterError` | 400       | Thrown when required query parameters (e.g., `name` or `folder`) are missing  |
| `NameNotUniqueError`         | 409       | Prefix list name already exists                                               |
| `ObjectNotPresentError`      | 404       | Prefix list not found                                                         |
| `ReferenceNotZeroError`      | 409       | Prefix list still referenced                                                  |
| `AuthenticationError`        | 401       | Authentication failed                                                         |
| `ServerError`                | 500       | Internal server error                                                         |

## Basic Configuration

The Route Prefix List service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

### Unified Client Interface (Recommended)

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Access the Route Prefix List service directly through the client
route_prefix_lists = client.route_prefix_list
```

### Traditional Service Instantiation (Legacy)

```python
from scm.client import Scm
from scm.config.network import RoutePrefixList

# Initialize client
client = Scm(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Initialize RoutePrefixList object explicitly
route_prefix_lists = RoutePrefixList(client)
```

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

## Usage Examples

### Creating Route Prefix Lists

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Create a prefix list for internal routes
prefix_list_data = {
   "name": "internal-prefixes",
   "description": "Match internal network prefixes",
   "ipv4": {
      "ipv4_entry": [
         {
            "name": 10,
            "action": "permit",
            "prefix": {
               "entry": {
                  "network": "10.0.0.0/8",
                  "greater_than_or_equal": 16,
                  "less_than_or_equal": 24
               }
            }
         },
         {
            "name": 20,
            "action": "permit",
            "prefix": {
               "entry": {
                  "network": "172.16.0.0/12",
                  "greater_than_or_equal": 16,
                  "less_than_or_equal": 24
               }
            }
         }
      ]
   },
   "folder": "Texas"
}

new_prefix_list = client.route_prefix_list.create(prefix_list_data)
print(f"Created prefix list with ID: {new_prefix_list.id}")

# Create a prefix list matching any prefix
any_prefix_data = {
   "name": "match-any",
   "description": "Match any prefix",
   "ipv4": {
      "ipv4_entry": [
         {
            "name": 10,
            "action": "permit",
            "prefix": {
               "network": "any"
            }
         }
      ]
   },
   "folder": "Texas"
}

any_prefix = client.route_prefix_list.create(any_prefix_data)
print(f"Created match-any prefix list with ID: {any_prefix.id}")

# Create a default route only prefix list
default_only_data = {
   "name": "default-route-only",
   "description": "Match only the default route",
   "ipv4": {
      "ipv4_entry": [
         {
            "name": 10,
            "action": "permit",
            "prefix": {
               "entry": {
                  "network": "0.0.0.0/0"
               }
            }
         }
      ]
   },
   "folder": "Texas"
}

default_only = client.route_prefix_list.create(default_only_data)
print(f"Created default-only prefix list with ID: {default_only.id}")
```

### Retrieving Route Prefix Lists

```python
# Fetch by name and folder
prefix_list = client.route_prefix_list.fetch(
   name="internal-prefixes",
   folder="Texas"
)
print(f"Found prefix list: {prefix_list.name}")
if prefix_list.ipv4 and prefix_list.ipv4.ipv4_entry:
   for entry in prefix_list.ipv4.ipv4_entry:
      print(f"  Seq {entry.name}: {entry.action}")

# Get by ID
prefix_list_by_id = client.route_prefix_list.get(prefix_list.id)
print(f"Retrieved prefix list: {prefix_list_by_id.name}")
```

### Updating Route Prefix Lists

```python
# Fetch existing prefix list
existing_list = client.route_prefix_list.fetch(
   name="internal-prefixes",
   folder="Texas"
)

# Add a new entry for 192.168.0.0/16
existing_list.ipv4.ipv4_entry.append({
   "name": 30,
   "action": "permit",
   "prefix": {
      "entry": {
         "network": "192.168.0.0/16",
         "greater_than_or_equal": 24,
         "less_than_or_equal": 28
      }
   }
})

# Perform update
updated_list = client.route_prefix_list.update(existing_list)
```

### Listing Route Prefix Lists

```python
# List all route prefix lists in a folder
prefix_lists = client.route_prefix_list.list(
   folder="Texas"
)

# Process results
for pl in prefix_lists:
   print(f"Name: {pl.name}")
   if pl.description:
      print(f"  Description: {pl.description}")
```

### Filtering Responses

The `list()` method supports additional parameters to refine your query results even further. Alongside basic filters,
you can leverage the `exact_match`, `exclude_folders`, `exclude_snippets`, and `exclude_devices` parameters to control
which objects are included or excluded after the initial API response is fetched.

**Parameters:**

- `exact_match (bool)`: When `True`, only objects defined exactly in the specified container (`folder`, `snippet`, or `device`) are returned. Inherited or propagated objects are filtered out.
- `exclude_folders (List[str])`: Provide a list of folder names that you do not want included in the results.
- `exclude_snippets (List[str])`: Provide a list of snippet values to exclude from the results.
- `exclude_devices (List[str])`: Provide a list of device values to exclude from the results.

**Examples:**

```python
# Only return prefix lists defined exactly in 'Texas'
exact_lists = client.route_prefix_list.list(
   folder='Texas',
   exact_match=True
)

for pl in exact_lists:
   print(f"Exact match: {pl.name} in {pl.folder}")

# Exclude all prefix lists from the 'All' folder
no_all_lists = client.route_prefix_list.list(
   folder='Texas',
   exclude_folders=['All']
)

for pl in no_all_lists:
   assert pl.folder != 'All'
   print(f"Filtered out 'All': {pl.name}")
```

### Controlling Pagination with max_limit

The SDK supports pagination through the `max_limit` parameter, which defines how many objects are retrieved per API call. By default, `max_limit` is set to 2500. The API itself imposes a maximum allowed value of 5000. If you set `max_limit` higher than 5000, it will be capped to the API's maximum. The `list()` method will continue to iterate through all objects until all results have been retrieved. Adjusting `max_limit` can help manage retrieval performance and memory usage when working with large datasets.

**Example:**

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Configure max_limit using the property setter
client.route_prefix_list.max_limit = 4000

# List all prefix lists - auto-paginates through results
all_lists = client.route_prefix_list.list(folder='Texas')
```

### Deleting Route Prefix Lists

```python
# Delete by ID
prefix_list_id = "123e4567-e89b-12d3-a456-426655440000"
client.route_prefix_list.delete(prefix_list_id)
```

## Managing Configuration Changes

### Performing Commits

```python
# Prepare commit parameters
commit_params = {
   "folders": ["Texas"],
   "description": "Updated route prefix list configurations",
   "sync": True,
   "timeout": 300  # 5 minute timeout
}

# Commit the changes directly on the client
result = client.commit(**commit_params)

print(f"Commit job ID: {result.job_id}")
```

### Monitoring Jobs

```python
# Get status of specific job directly from the client
job_status = client.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

# List recent jobs directly from the client
recent_jobs = client.list_jobs(limit=10)
for job in recent_jobs.data:
   print(f"Job {job.id}: {job.type_str} - {job.status_str}")
```

## Error Handling

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
   # Create route prefix list
   prefix_config = {
      "name": "test-prefix-list",
      "ipv4": {
         "ipv4_entry": [
            {
               "name": 10,
               "action": "permit",
               "prefix": {
                  "entry": {
                     "network": "10.0.0.0/8",
                     "less_than_or_equal": 24
                  }
               }
            }
         ]
      },
      "folder": "Texas"
   }

   new_list = client.route_prefix_list.create(prefix_config)

   # Commit changes
   result = client.commit(
      folders=["Texas"],
      description="Added route prefix list",
      sync=True
   )

   # Check job status
   status = client.get_job_status(result.job_id)

except InvalidObjectError as e:
   print(f"Invalid prefix list data: {e.message}")
except NameNotUniqueError as e:
   print(f"Prefix list name already exists: {e.message}")
except ObjectNotPresentError as e:
   print(f"Prefix list not found: {e.message}")
except ReferenceNotZeroError as e:
   print(f"Prefix list still in use: {e.message}")
except MissingQueryParameterError as e:
   print(f"Missing parameter: {e.message}")
```

## Best Practices

1. **Client Usage**
   - Use the unified client interface (`client.route_prefix_list`) for streamlined code
   - Create a single client instance and reuse it across your application
   - Perform commit operations directly on the client object (`client.commit()`)

2. **Prefix List Design**
   - Use consistent sequence numbering with gaps (10, 20, 30) to allow future insertions
   - Leverage `ge` and `le` qualifiers to match prefix length ranges efficiently
   - Use `network: "any"` to match all prefixes when needed
   - Create separate prefix lists for different filtering purposes

3. **Prefix Matching**
   - Without `ge`/`le`, only exact prefix length matches are returned
   - Use `ge` to match prefixes with length >= the specified value
   - Use `le` to match prefixes with length <= the specified value
   - Combine `ge` and `le` to match a range of prefix lengths

4. **Container Management**
   - Always specify exactly one container (folder, snippet, or device)
   - Use consistent container names across operations
   - Validate container existence before operations

5. **Error Handling**
   - Implement comprehensive error handling for all operations
   - Check job status after commits
   - Handle specific exceptions before generic ones
   - Log error details for troubleshooting

6. **Performance**
   - Use appropriate pagination for list operations
   - Cache frequently accessed prefix list configurations
   - Implement proper retry mechanisms

## Related Models

- [RoutePrefixListBaseModel](../../models/network/route_prefix_list_models.md#Overview)
- [RoutePrefixListCreateModel](../../models/network/route_prefix_list_models.md#Overview)
- [RoutePrefixListUpdateModel](../../models/network/route_prefix_list_models.md#Overview)
- [RoutePrefixListResponseModel](../../models/network/route_prefix_list_models.md#Overview)
- [RoutePrefixListIpv4Entry](../../models/network/route_prefix_list_models.md#Overview)
- [RoutePrefixListPrefix](../../models/network/route_prefix_list_models.md#Overview)
