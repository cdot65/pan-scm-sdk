# BGP Route Map Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [BGP Route Map Model Attributes](#bgp-route-map-model-attributes)
4. [Route Map Entry Configuration](#route-map-entry-configuration)
5. [Exceptions](#exceptions)
6. [Basic Configuration](#basic-configuration)
7. [Usage Examples](#usage-examples)
    - [Creating BGP Route Maps](#creating-bgp-route-maps)
    - [Retrieving BGP Route Maps](#retrieving-bgp-route-maps)
    - [Updating BGP Route Maps](#updating-bgp-route-maps)
    - [Listing BGP Route Maps](#listing-bgp-route-maps)
    - [Filtering Responses](#filtering-responses)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Deleting BGP Route Maps](#deleting-bgp-route-maps)
8. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
9. [Error Handling](#error-handling)
10. [Best Practices](#best-practices)
11. [Related Models](#related-models)

## Overview

The `BgpRouteMap` class manages BGP route map objects in Palo Alto Networks' Strata Cloud Manager. It extends from `BaseObject` and offers methods to create, retrieve, update, list, fetch, and delete BGP route maps. Route maps provide import/export policy control for BGP, defining ordered entries with match criteria and set actions. Each entry has a sequence number, a permit/deny action, optional match conditions, and optional set modifications.

!!! note
    The API uses the spelling `substract` (not `subtract`) for the metric action type. This typo is preserved in the SDK to match the API exactly.

## Core Methods

| Method     | Description                                                  | Parameters                                                                                                                       | Return Type                        |
|------------|--------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|------------------------------------|
| `create()` | Creates a new BGP route map                                  | `data: Dict[str, Any]`                                                                                                           | `BgpRouteMapResponseModel`         |
| `get()`    | Retrieves a BGP route map by its unique ID                   | `object_id: str`                                                                                                                 | `BgpRouteMapResponseModel`         |
| `update()` | Updates an existing BGP route map                            | `route_map: BgpRouteMapUpdateModel`                                                                                              | `BgpRouteMapResponseModel`         |
| `list()`   | Lists BGP route maps with optional filtering                 | `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`, `exact_match: bool = False`, plus additional filters | `List[BgpRouteMapResponseModel]`   |
| `fetch()`  | Fetches a single BGP route map by name within a container    | `name: str`, `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`                                          | `BgpRouteMapResponseModel`         |
| `delete()` | Deletes a BGP route map by its ID                            | `object_id: str`                                                                                                                 | `None`                             |

## BGP Route Map Model Attributes

| Attribute   | Type                     | Required | Default | Description                                         |
|-------------|--------------------------|----------|---------|-----------------------------------------------------|
| `name`      | str                      | Yes      | None    | Route map name                                      |
| `id`        | UUID                     | Yes*     | None    | Unique identifier (*response/update only)           |
| `route_map` | List[BgpRouteMapEntry]   | No       | None    | List of route map entries                           |
| `folder`    | str                      | No**     | None    | Folder location. Max 64 chars                       |
| `snippet`   | str                      | No**     | None    | Snippet location. Max 64 chars                      |
| `device`    | str                      | No**     | None    | Device location. Max 64 chars                       |

\* Only required for update and response models
\** Exactly one container (folder/snippet/device) must be provided for create operations

## Route Map Entry Configuration

The `route_map` attribute holds a list of entries, each with a sequence number, action, match criteria, and set actions.

### BgpRouteMapEntry

| Attribute     | Type             | Required | Description                              |
|---------------|------------------|----------|------------------------------------------|
| `name`        | int              | Yes      | Sequence number (1-65535)                |
| `description` | str              | No       | Entry description                        |
| `action`      | str              | No       | Action: "permit" or "deny"               |
| `match`       | BgpRouteMapMatch | No       | Match criteria                           |
| `set`         | BgpRouteMapSet   | No       | Set actions                              |

### BgpRouteMapMatch

| Attribute             | Type                  | Required | Description                        |
|-----------------------|-----------------------|----------|------------------------------------|
| `as_path_access_list` | str                   | No       | AS path access list name           |
| `interface`           | str                   | No       | Interface name to match            |
| `regular_community`   | str                   | No       | Regular community to match         |
| `origin`              | str                   | No       | Origin to match                    |
| `large_community`     | str                   | No       | Large community to match           |
| `tag`                 | int                   | No       | Tag value to match                 |
| `extended_community`  | str                   | No       | Extended community to match        |
| `local_preference`    | int                   | No       | Local preference to match          |
| `metric`              | int                   | No       | Metric value to match              |
| `peer`                | str                   | No       | Peer type: "local" or "none"       |
| `ipv4`                | BgpRouteMapMatchIpv4  | No       | IPv4 match criteria                |

### BgpRouteMapMatchIpv4

| Attribute      | Type | Required | Description                        |
|----------------|------|----------|------------------------------------|
| `address`      | str  | No       | IPv4 address prefix list to match  |
| `next_hop`     | str  | No       | IPv4 next-hop prefix list to match |
| `route_source` | str  | No       | IPv4 route source to match         |

### BgpRouteMapSet

| Attribute                    | Type                      | Required | Description                           |
|------------------------------|---------------------------|----------|---------------------------------------|
| `atomic_aggregate`           | bool                      | No       | Set atomic aggregate                  |
| `local_preference`           | int                       | No       | Local preference value to set         |
| `tag`                        | int                       | No       | Tag value to set                      |
| `metric`                     | BgpRouteMapSetMetric      | No       | Metric action                         |
| `weight`                     | int                       | No       | Weight value to set                   |
| `origin`                     | str                       | No       | Origin: "none", "egp", "igp", "incomplete" |
| `remove_regular_community`   | str                       | No       | Regular community to remove           |
| `remove_large_community`     | str                       | No       | Large community to remove             |
| `originator_id`              | str                       | No       | Originator ID to set                  |
| `aggregator`                 | BgpRouteMapSetAggregator  | No       | Aggregator configuration              |
| `ipv4`                       | BgpRouteMapSetIpv4        | No       | IPv4 set configuration                |
| `aspath_exclude`             | str                       | No       | AS path to exclude                    |
| `aspath_prepend`             | str                       | No       | AS path to prepend                    |
| `regular_community`          | List[str]                 | No       | Regular communities to set            |
| `overwrite_regular_community`| bool                      | No       | Overwrite existing communities        |
| `large_community`            | List[str]                 | No       | Large communities to set              |
| `overwrite_large_community`  | bool                      | No       | Overwrite existing large communities  |

### BgpRouteMapSetMetric

| Attribute | Type | Required | Description                                              |
|-----------|------|----------|----------------------------------------------------------|
| `action`  | str  | No       | Metric action: "set", "add", or "substract" (API spelling) |
| `value`   | int  | No       | Metric value                                             |

### BgpRouteMapSetAggregator

| Attribute   | Type | Required | Description              |
|-------------|------|----------|--------------------------|
| `as`        | int  | No       | Aggregator AS number     |
| `router_id` | str | No       | Aggregator router ID     |

### BgpRouteMapSetIpv4

| Attribute        | Type | Required | Description              |
|------------------|------|----------|--------------------------|
| `source_address` | str  | No       | Source address to set     |
| `next_hop`       | str  | No       | Next-hop address to set   |

## Exceptions

| Exception                    | HTTP Code | Description                                                                   |
|------------------------------|-----------|-------------------------------------------------------------------------------|
| `InvalidObjectError`         | 400       | Thrown when provided data or parameters are invalid                           |
| `MissingQueryParameterError` | 400       | Thrown when required query parameters (e.g., `name` or `folder`) are missing  |
| `NameNotUniqueError`         | 409       | Route map name already exists                                                 |
| `ObjectNotPresentError`      | 404       | Route map not found                                                           |
| `ReferenceNotZeroError`      | 409       | Route map still referenced                                                    |
| `AuthenticationError`        | 401       | Authentication failed                                                         |
| `ServerError`                | 500       | Internal server error                                                         |

## Basic Configuration

The BGP Route Map service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

### Unified Client Interface (Recommended)

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Access the BGP Route Map service directly through the client
bgp_route_maps = client.bgp_route_map
```

### Traditional Service Instantiation (Legacy)

```python
from scm.client import Scm
from scm.config.network import BgpRouteMap

# Initialize client
client = Scm(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Initialize BgpRouteMap object explicitly
bgp_route_maps = BgpRouteMap(client)
```

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

## Usage Examples

### Creating BGP Route Maps

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Create a route map for inbound policy
inbound_map_data = {
   "name": "inbound-policy",
   "route_map": [
      {
         "name": 10,
         "description": "Accept internal prefixes with higher local-pref",
         "action": "permit",
         "match": {
            "ipv4": {
               "address": "internal-prefixes"
            }
         },
         "set": {
            "local_preference": 200,
            "weight": 100
         }
      },
      {
         "name": 20,
         "description": "Accept all other routes with default local-pref",
         "action": "permit",
         "set": {
            "local_preference": 100
         }
      }
   ],
   "folder": "Texas"
}

new_map = client.bgp_route_map.create(inbound_map_data)
print(f"Created route map with ID: {new_map.id}")

# Create a route map with community manipulation
community_map_data = {
   "name": "set-communities",
   "route_map": [
      {
         "name": 10,
         "action": "permit",
         "match": {
            "as_path_access_list": "customer-as-paths"
         },
         "set": {
            "regular_community": ["65000:100", "65000:200"],
            "overwrite_regular_community": True
         }
      }
   ],
   "folder": "Texas"
}

community_map = client.bgp_route_map.create(community_map_data)
print(f"Created community route map with ID: {community_map.id}")

# Create a route map with AS path prepending
prepend_map_data = {
   "name": "as-prepend-outbound",
   "route_map": [
      {
         "name": 10,
         "description": "Prepend AS path to de-prefer this path",
         "action": "permit",
         "match": {
            "ipv4": {
               "address": "backup-prefixes"
            }
         },
         "set": {
            "aspath_prepend": "65000 65000 65000",
            "metric": {
               "action": "set",
               "value": 200
            }
         }
      },
      {
         "name": 100,
         "action": "permit"
      }
   ],
   "folder": "Texas"
}

prepend_map = client.bgp_route_map.create(prepend_map_data)
print(f"Created AS-prepend route map with ID: {prepend_map.id}")
```

### Retrieving BGP Route Maps

```python
# Fetch by name and folder
route_map = client.bgp_route_map.fetch(
   name="inbound-policy",
   folder="Texas"
)
print(f"Found route map: {route_map.name}")
if route_map.route_map:
   for entry in route_map.route_map:
      print(f"  Seq {entry.name}: {entry.action}")
      if entry.description:
         print(f"    Description: {entry.description}")

# Get by ID
route_map_by_id = client.bgp_route_map.get(route_map.id)
print(f"Retrieved route map: {route_map_by_id.name}")
```

### Updating BGP Route Maps

```python
# Fetch existing route map
existing_map = client.bgp_route_map.fetch(
   name="inbound-policy",
   folder="Texas"
)

# Add a deny entry for bogon prefixes at the beginning
existing_map.route_map.insert(0, {
   "name": 5,
   "description": "Deny bogon prefixes",
   "action": "deny",
   "match": {
      "ipv4": {
         "address": "bogon-prefixes"
      }
   }
})

# Perform update
updated_map = client.bgp_route_map.update(existing_map)
```

### Listing BGP Route Maps

```python
# List all route maps in a folder
route_maps = client.bgp_route_map.list(
   folder="Texas"
)

# Process results
for rm in route_maps:
   entry_count = len(rm.route_map) if rm.route_map else 0
   print(f"Name: {rm.name} ({entry_count} entries)")
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
# Only return route maps defined exactly in 'Texas'
exact_maps = client.bgp_route_map.list(
   folder='Texas',
   exact_match=True
)

for rm in exact_maps:
   print(f"Exact match: {rm.name} in {rm.folder}")

# Exclude all route maps from the 'All' folder
no_all_maps = client.bgp_route_map.list(
   folder='Texas',
   exclude_folders=['All']
)

for rm in no_all_maps:
   assert rm.folder != 'All'
   print(f"Filtered out 'All': {rm.name}")
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
client.bgp_route_map.max_limit = 4000

# List all route maps - auto-paginates through results
all_maps = client.bgp_route_map.list(folder='Texas')
```

### Deleting BGP Route Maps

```python
# Delete by ID
route_map_id = "123e4567-e89b-12d3-a456-426655440000"
client.bgp_route_map.delete(route_map_id)
```

## Managing Configuration Changes

### Performing Commits

```python
# Prepare commit parameters
commit_params = {
   "folders": ["Texas"],
   "description": "Updated BGP route map configurations",
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
   # Create BGP route map
   map_config = {
      "name": "test-route-map",
      "route_map": [
         {
            "name": 10,
            "action": "permit",
            "set": {
               "local_preference": 150
            }
         }
      ],
      "folder": "Texas"
   }

   new_map = client.bgp_route_map.create(map_config)

   # Commit changes
   result = client.commit(
      folders=["Texas"],
      description="Added BGP route map",
      sync=True
   )

   # Check job status
   status = client.get_job_status(result.job_id)

except InvalidObjectError as e:
   print(f"Invalid route map data: {e.message}")
except NameNotUniqueError as e:
   print(f"Route map name already exists: {e.message}")
except ObjectNotPresentError as e:
   print(f"Route map not found: {e.message}")
except ReferenceNotZeroError as e:
   print(f"Route map still in use: {e.message}")
except MissingQueryParameterError as e:
   print(f"Missing parameter: {e.message}")
```

## Best Practices

1. **Client Usage**
   - Use the unified client interface (`client.bgp_route_map`) for streamlined code
   - Create a single client instance and reuse it across your application
   - Perform commit operations directly on the client object (`client.commit()`)

2. **Route Map Design**
   - Use sequence numbers with gaps (10, 20, 30) to allow future insertions
   - Always include a final permit-all or deny-all entry for explicit behavior
   - Place more specific matches before general ones in the sequence
   - Use descriptions on entries to document the policy intent

3. **Match and Set Actions**
   - Combine multiple match criteria to create precise filters
   - Use AS path prepending carefully as it affects convergence time
   - Set local preference for inbound policy to prefer specific paths
   - Use communities to tag routes for downstream policy decisions

4. **API Quirks**
   - The metric action uses `substract` (not `subtract`) to match the API spelling
   - The `as` field in aggregator uses `as_` in Python (aliased to `as` for serialization)

5. **Container Management**
   - Always specify exactly one container (folder, snippet, or device)
   - Use consistent container names across operations
   - Validate container existence before operations

6. **Error Handling**
   - Implement comprehensive error handling for all operations
   - Check job status after commits
   - Handle specific exceptions before generic ones
   - Log error details for troubleshooting

7. **Performance**
   - Use appropriate pagination for list operations
   - Cache frequently accessed route map configurations
   - Implement proper retry mechanisms

## Related Models

- [BgpRouteMapBaseModel](../../models/network/bgp_route_map_models.md#Overview)
- [BgpRouteMapCreateModel](../../models/network/bgp_route_map_models.md#Overview)
- [BgpRouteMapUpdateModel](../../models/network/bgp_route_map_models.md#Overview)
- [BgpRouteMapResponseModel](../../models/network/bgp_route_map_models.md#Overview)
- [BgpRouteMapEntry](../../models/network/bgp_route_map_models.md#Overview)
- [BgpRouteMapMatch](../../models/network/bgp_route_map_models.md#Overview)
- [BgpRouteMapSet](../../models/network/bgp_route_map_models.md#Overview)
