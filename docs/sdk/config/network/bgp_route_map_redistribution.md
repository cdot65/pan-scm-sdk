# BGP Route Map Redistribution Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [BGP Route Map Redistribution Model Attributes](#bgp-route-map-redistribution-model-attributes)
4. [Source Protocol Configuration](#source-protocol-configuration)
5. [Exceptions](#exceptions)
6. [Basic Configuration](#basic-configuration)
7. [Usage Examples](#usage-examples)
    - [Creating BGP Route Map Redistributions](#creating-bgp-route-map-redistributions)
    - [Retrieving BGP Route Map Redistributions](#retrieving-bgp-route-map-redistributions)
    - [Updating BGP Route Map Redistributions](#updating-bgp-route-map-redistributions)
    - [Listing BGP Route Map Redistributions](#listing-bgp-route-map-redistributions)
    - [Filtering Responses](#filtering-responses)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Deleting BGP Route Map Redistributions](#deleting-bgp-route-map-redistributions)
8. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
9. [Error Handling](#error-handling)
10. [Best Practices](#best-practices)
11. [Related Models](#related-models)

## Overview

The `BgpRouteMapRedistribution` class manages BGP route map redistribution objects in Palo Alto Networks' Strata Cloud Manager. It extends from `BaseObject` and offers methods to create, retrieve, update, list, fetch, and delete BGP route map redistributions. This is the most complex routing model, using 2-level oneOf discrimination:

- **Level 1 (Source Protocol)**: `bgp`, `ospf`, or `connected_static` -- mutually exclusive
- **Level 2 (Target Protocol)**: Within each source, the target protocol is also mutually exclusive

This produces 7 possible crossover variants, each with variant-specific match and set fields:

| Source           | Target | Match Type  | Set Type   |
|------------------|--------|-------------|------------|
| bgp              | ospf   | BGP match   | OSPF set   |
| bgp              | rib    | BGP match   | RIB set    |
| ospf             | bgp    | Simple match| BGP set    |
| ospf             | rib    | Simple match| RIB set    |
| connected_static | bgp    | Simple match| BGP set    |
| connected_static | ospf   | Simple match| OSPF set   |
| connected_static | rib    | Simple match| RIB set    |

## Core Methods

| Method     | Description                                                                | Parameters                                                                                                                       | Return Type                                       |
|------------|----------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------|
| `create()` | Creates a new BGP route map redistribution                                 | `data: Dict[str, Any]`                                                                                                           | `BgpRouteMapRedistributionResponseModel`          |
| `get()`    | Retrieves a BGP route map redistribution by its unique ID                  | `object_id: str`                                                                                                                 | `BgpRouteMapRedistributionResponseModel`          |
| `update()` | Updates an existing BGP route map redistribution                           | `resource: BgpRouteMapRedistributionUpdateModel`                                                                                 | `BgpRouteMapRedistributionResponseModel`          |
| `list()`   | Lists BGP route map redistributions with optional filtering                | `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`, `exact_match: bool = False`, plus additional filters | `List[BgpRouteMapRedistributionResponseModel]`    |
| `fetch()`  | Fetches a single BGP route map redistribution by name within a container   | `name: str`, `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`                                          | `BgpRouteMapRedistributionResponseModel`          |
| `delete()` | Deletes a BGP route map redistribution by its ID                           | `object_id: str`                                                                                                                 | `None`                                            |

## BGP Route Map Redistribution Model Attributes

| Attribute          | Type                                          | Required | Default | Description                                         |
|--------------------|-----------------------------------------------|----------|---------|-----------------------------------------------------|
| `name`             | str                                           | Yes      | None    | Redistribution name                                 |
| `id`               | UUID                                          | Yes*     | None    | Unique identifier (*response/update only)           |
| `bgp`              | BgpRouteMapRedistBgpSource                    | No       | None    | BGP as source protocol (mutually exclusive)         |
| `ospf`             | BgpRouteMapRedistOspfSource                   | No       | None    | OSPF as source protocol (mutually exclusive)        |
| `connected_static` | BgpRouteMapRedistConnectedStaticSource        | No       | None    | Connected/Static as source (mutually exclusive)     |
| `folder`           | str                                           | No**     | None    | Folder location. Max 64 chars                       |
| `snippet`          | str                                           | No**     | None    | Snippet location. Max 64 chars                      |
| `device`           | str                                           | No**     | None    | Device location. Max 64 chars                       |

\* Only required for update and response models
\** Exactly one container (folder/snippet/device) must be provided for create operations

At most one source protocol (`bgp`, `ospf`, or `connected_static`) can be set per redistribution object.

## Source Protocol Configuration

### BgpRouteMapRedistBgpSource

BGP as source protocol. Targets are mutually exclusive.

| Attribute | Type                        | Required | Description                        |
|-----------|-----------------------------|----------|------------------------------------|
| `ospf`    | BgpRouteMapRedistBgpToOspf  | No       | Redistribute BGP routes to OSPF    |
| `rib`     | BgpRouteMapRedistBgpToRib   | No       | Redistribute BGP routes to RIB     |

### BgpRouteMapRedistOspfSource

OSPF as source protocol. Targets are mutually exclusive.

| Attribute | Type                         | Required | Description                        |
|-----------|------------------------------|----------|------------------------------------|
| `bgp`     | BgpRouteMapRedistOspfToBgp   | No       | Redistribute OSPF routes to BGP    |
| `rib`     | BgpRouteMapRedistOspfToRib   | No       | Redistribute OSPF routes to RIB    |

### BgpRouteMapRedistConnectedStaticSource

Connected/Static as source protocol. Targets are mutually exclusive.

| Attribute | Type                                  | Required | Description                                    |
|-----------|---------------------------------------|----------|------------------------------------------------|
| `bgp`     | BgpRouteMapRedistConnStaticToBgp      | No       | Redistribute connected/static routes to BGP    |
| `ospf`    | BgpRouteMapRedistConnStaticToOspf     | No       | Redistribute connected/static routes to OSPF   |
| `rib`     | BgpRouteMapRedistConnStaticToRib      | No       | Redistribute connected/static routes to RIB    |

### Route Map Entry (all target containers)

Each target container holds a `route_map` list of entries. The entry structure is the same across all variants:

| Attribute     | Type                | Required | Description                    |
|---------------|---------------------|----------|--------------------------------|
| `name`        | int                 | Yes      | Sequence number (1-65535)      |
| `description` | str                 | No       | Entry description              |
| `action`      | str                 | No       | Action: "permit" or "deny"     |
| `match`       | (variant-specific)  | No       | Match criteria                 |
| `set`         | (variant-specific)  | No       | Set actions                    |

### BGP Match (for BGP source variants)

| Attribute             | Type                            | Required | Description                     |
|-----------------------|---------------------------------|----------|---------------------------------|
| `as_path_access_list` | str                             | No       | AS path access list name        |
| `regular_community`   | str                             | No       | Regular community to match      |
| `large_community`     | str                             | No       | Large community to match        |
| `extended_community`  | str                             | No       | Extended community to match     |
| `interface`           | str                             | No       | Interface to match              |
| `tag`                 | int                             | No       | Tag value to match              |
| `local_preference`    | int                             | No       | Local preference to match       |
| `metric`              | int                             | No       | Metric to match                 |
| `origin`              | str                             | No       | Origin to match                 |
| `peer`                | str                             | No       | Peer type: "local" or "none"    |
| `ipv4`                | BgpRouteMapRedistBgpMatchIpv4   | No       | IPv4 match (address, next_hop, route_source) |

### Simple Match (for OSPF/connected_static source variants)

| Attribute   | Type                               | Required | Description                |
|-------------|-------------------------------------|----------|----------------------------|
| `interface` | str                                | No       | Interface to match         |
| `metric`    | int                                | No       | Metric to match            |
| `tag`       | int                                | No       | Tag to match               |
| `ipv4`      | BgpRouteMapRedistSimpleMatchIpv4   | No       | IPv4 match (address, next_hop) |

### BGP Set (when target is BGP)

Full BGP set fields including communities, AS-path, local preference, weight, etc.

| Attribute                    | Type                           | Required | Description                         |
|------------------------------|--------------------------------|----------|-------------------------------------|
| `atomic_aggregate`           | bool                           | No       | Set atomic aggregate                |
| `local_preference`           | int                            | No       | Local preference to set             |
| `tag`                        | int                            | No       | Tag to set                          |
| `metric`                     | BgpRouteMapRedistSetMetric     | No       | Metric action (set/add/substract)   |
| `weight`                     | int                            | No       | Weight to set                       |
| `origin`                     | str                            | No       | Origin to set                       |
| `aggregator`                 | BgpRouteMapRedistSetAggregator | No       | Aggregator config                   |
| `ipv4`                       | BgpRouteMapRedistSetIpv4       | No       | IPv4 set config                     |
| `aspath_exclude`             | str                            | No       | AS path to exclude                  |
| `aspath_prepend`             | str                            | No       | AS path to prepend                  |
| `regular_community`          | List[str]                      | No       | Communities to set                  |
| `overwrite_regular_community`| bool                           | No       | Overwrite communities               |
| `large_community`            | List[str]                      | No       | Large communities to set            |
| `overwrite_large_community`  | bool                           | No       | Overwrite large communities         |

### OSPF Set (when target is OSPF)

| Attribute     | Type                       | Required | Description                           |
|---------------|----------------------------|----------|---------------------------------------|
| `metric`      | BgpRouteMapRedistSetMetric | No       | Metric action (set/add/substract)     |
| `metric_type` | str                        | No       | OSPF metric type                      |
| `tag`         | int                        | No       | Tag to set                            |

### RIB Set (when target is RIB)

| Attribute | Type                       | Required | Description                |
|-----------|----------------------------|----------|----------------------------|
| `ipv4`    | BgpRouteMapRedistSetIpv4   | No       | IPv4 set (source_address)  |

## Exceptions

| Exception                    | HTTP Code | Description                                                                   |
|------------------------------|-----------|-------------------------------------------------------------------------------|
| `InvalidObjectError`         | 400       | Thrown when provided data or parameters are invalid                           |
| `MissingQueryParameterError` | 400       | Thrown when required query parameters (e.g., `name` or `folder`) are missing  |
| `NameNotUniqueError`         | 409       | Redistribution name already exists                                            |
| `ObjectNotPresentError`      | 404       | Redistribution not found                                                      |
| `ReferenceNotZeroError`      | 409       | Redistribution still referenced                                               |
| `AuthenticationError`        | 401       | Authentication failed                                                         |
| `ServerError`                | 500       | Internal server error                                                         |

## Basic Configuration

The BGP Route Map Redistribution service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

### Unified Client Interface (Recommended)

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Access the BGP Route Map Redistribution service directly through the client
bgp_route_map_redists = client.bgp_route_map_redistribution
```

### Traditional Service Instantiation (Legacy)

```python
from scm.client import Scm
from scm.config.network import BgpRouteMapRedistribution

# Initialize client
client = Scm(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Initialize BgpRouteMapRedistribution object explicitly
bgp_route_map_redists = BgpRouteMapRedistribution(client)
```

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

## Usage Examples

### Creating BGP Route Map Redistributions

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Create OSPF-to-BGP redistribution
ospf_to_bgp_data = {
   "name": "ospf-to-bgp-redist",
   "ospf": {
      "bgp": {
         "route_map": [
            {
               "name": 10,
               "description": "Redistribute OSPF internal routes to BGP",
               "action": "permit",
               "match": {
                  "tag": 100
               },
               "set": {
                  "local_preference": 200,
                  "regular_community": ["65000:100"],
                  "origin": "igp"
               }
            },
            {
               "name": 20,
               "action": "permit",
               "set": {
                  "local_preference": 100
               }
            }
         ]
      }
   },
   "folder": "Texas"
}

new_redist = client.bgp_route_map_redistribution.create(ospf_to_bgp_data)
print(f"Created OSPF-to-BGP redistribution with ID: {new_redist.id}")

# Create BGP-to-OSPF redistribution
bgp_to_ospf_data = {
   "name": "bgp-to-ospf-redist",
   "bgp": {
      "ospf": {
         "route_map": [
            {
               "name": 10,
               "description": "Redistribute specific BGP routes to OSPF",
               "action": "permit",
               "match": {
                  "as_path_access_list": "internal-as-paths",
                  "ipv4": {
                     "address": "bgp-prefixes-for-ospf"
                  }
               },
               "set": {
                  "metric": {
                     "action": "set",
                     "value": 500
                  },
                  "metric_type": "type-2",
                  "tag": 200
               }
            }
         ]
      }
   },
   "folder": "Texas"
}

bgp_ospf_redist = client.bgp_route_map_redistribution.create(bgp_to_ospf_data)
print(f"Created BGP-to-OSPF redistribution with ID: {bgp_ospf_redist.id}")

# Create connected/static-to-BGP redistribution
conn_to_bgp_data = {
   "name": "connected-to-bgp-redist",
   "connected_static": {
      "bgp": {
         "route_map": [
            {
               "name": 10,
               "description": "Redistribute connected interfaces to BGP",
               "action": "permit",
               "match": {
                  "interface": "ethernet1/1"
               },
               "set": {
                  "local_preference": 300,
                  "weight": 200,
                  "origin": "igp"
               }
            }
         ]
      }
   },
   "folder": "Texas"
}

conn_bgp_redist = client.bgp_route_map_redistribution.create(conn_to_bgp_data)
print(f"Created connected-to-BGP redistribution with ID: {conn_bgp_redist.id}")
```

### Retrieving BGP Route Map Redistributions

```python
# Fetch by name and folder
redist = client.bgp_route_map_redistribution.fetch(
   name="ospf-to-bgp-redist",
   folder="Texas"
)
print(f"Found redistribution: {redist.name}")

# Determine the source protocol
if redist.bgp:
   print("  Source: BGP")
elif redist.ospf:
   print("  Source: OSPF")
elif redist.connected_static:
   print("  Source: Connected/Static")

# Get by ID
redist_by_id = client.bgp_route_map_redistribution.get(redist.id)
print(f"Retrieved redistribution: {redist_by_id.name}")
```

### Updating BGP Route Map Redistributions

```python
# Fetch existing redistribution
existing_redist = client.bgp_route_map_redistribution.fetch(
   name="ospf-to-bgp-redist",
   folder="Texas"
)

# Add a deny entry for specific tags
existing_redist.ospf.bgp.route_map.insert(0, {
   "name": 5,
   "description": "Deny routes with tag 999",
   "action": "deny",
   "match": {
      "tag": 999
   }
})

# Perform update
updated_redist = client.bgp_route_map_redistribution.update(existing_redist)
```

### Listing BGP Route Map Redistributions

```python
# List all route map redistributions in a folder
redists = client.bgp_route_map_redistribution.list(
   folder="Texas"
)

# Process results
for redist in redists:
   source = "unknown"
   if redist.bgp:
      source = "bgp"
   elif redist.ospf:
      source = "ospf"
   elif redist.connected_static:
      source = "connected_static"
   print(f"Name: {redist.name} (source: {source})")
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
# Only return redistributions defined exactly in 'Texas'
exact_redists = client.bgp_route_map_redistribution.list(
   folder='Texas',
   exact_match=True
)

for redist in exact_redists:
   print(f"Exact match: {redist.name} in {redist.folder}")

# Exclude all redistributions from the 'All' folder
no_all_redists = client.bgp_route_map_redistribution.list(
   folder='Texas',
   exclude_folders=['All']
)

for redist in no_all_redists:
   assert redist.folder != 'All'
   print(f"Filtered out 'All': {redist.name}")
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
client.bgp_route_map_redistribution.max_limit = 4000

# List all redistributions - auto-paginates through results
all_redists = client.bgp_route_map_redistribution.list(folder='Texas')
```

### Deleting BGP Route Map Redistributions

```python
# Delete by ID
redist_id = "123e4567-e89b-12d3-a456-426655440000"
client.bgp_route_map_redistribution.delete(redist_id)
```

## Managing Configuration Changes

### Performing Commits

```python
# Prepare commit parameters
commit_params = {
   "folders": ["Texas"],
   "description": "Updated BGP route map redistribution configurations",
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
   # Create BGP route map redistribution
   redist_config = {
      "name": "test-redist",
      "connected_static": {
         "bgp": {
            "route_map": [
               {
                  "name": 10,
                  "action": "permit",
                  "set": {
                     "local_preference": 100
                  }
               }
            ]
         }
      },
      "folder": "Texas"
   }

   new_redist = client.bgp_route_map_redistribution.create(redist_config)

   # Commit changes
   result = client.commit(
      folders=["Texas"],
      description="Added BGP route map redistribution",
      sync=True
   )

   # Check job status
   status = client.get_job_status(result.job_id)

except InvalidObjectError as e:
   print(f"Invalid redistribution data: {e.message}")
except NameNotUniqueError as e:
   print(f"Redistribution name already exists: {e.message}")
except ObjectNotPresentError as e:
   print(f"Redistribution not found: {e.message}")
except ReferenceNotZeroError as e:
   print(f"Redistribution still in use: {e.message}")
except MissingQueryParameterError as e:
   print(f"Missing parameter: {e.message}")
```

## Best Practices

1. **Client Usage**
   - Use the unified client interface (`client.bgp_route_map_redistribution`) for streamlined code
   - Create a single client instance and reuse it across your application
   - Perform commit operations directly on the client object (`client.commit()`)

2. **Redistribution Design**
   - Only one source protocol (`bgp`, `ospf`, or `connected_static`) can be set per object
   - Only one target protocol can be set within each source
   - Create separate redistribution objects for different source-target combinations
   - Use descriptive names that indicate the source-target direction (e.g., "ospf-to-bgp-redist")

3. **Match and Set by Variant**
   - BGP source variants have richer match criteria (AS path, communities, local preference)
   - OSPF/connected_static source variants use simpler match criteria (interface, metric, tag)
   - Target BGP set actions include full BGP attributes (communities, AS-path, weight)
   - Target OSPF set actions are limited to metric, metric_type, and tag
   - Target RIB set actions are limited to IPv4 source_address

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
   - Cache frequently accessed redistribution configurations
   - Implement proper retry mechanisms

## Related Models

- [BgpRouteMapRedistributionBaseModel](../../models/network/bgp_route_map_redistribution_models.md#Overview)
- [BgpRouteMapRedistributionCreateModel](../../models/network/bgp_route_map_redistribution_models.md#Overview)
- [BgpRouteMapRedistributionUpdateModel](../../models/network/bgp_route_map_redistribution_models.md#Overview)
- [BgpRouteMapRedistributionResponseModel](../../models/network/bgp_route_map_redistribution_models.md#Overview)
- [BgpRouteMapRedistBgpSource](../../models/network/bgp_route_map_redistribution_models.md#Overview)
- [BgpRouteMapRedistOspfSource](../../models/network/bgp_route_map_redistribution_models.md#Overview)
- [BgpRouteMapRedistConnectedStaticSource](../../models/network/bgp_route_map_redistribution_models.md#Overview)
