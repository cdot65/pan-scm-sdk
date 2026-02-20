# BGP Filtering Profile Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [BGP Filtering Profile Model Attributes](#bgp-filtering-profile-model-attributes)
4. [IPv4 Filtering Configuration](#ipv4-filtering-configuration)
5. [Exceptions](#exceptions)
6. [Basic Configuration](#basic-configuration)
7. [Usage Examples](#usage-examples)
    - [Creating BGP Filtering Profiles](#creating-bgp-filtering-profiles)
    - [Retrieving BGP Filtering Profiles](#retrieving-bgp-filtering-profiles)
    - [Updating BGP Filtering Profiles](#updating-bgp-filtering-profiles)
    - [Listing BGP Filtering Profiles](#listing-bgp-filtering-profiles)
    - [Filtering Responses](#filtering-responses)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Deleting BGP Filtering Profiles](#deleting-bgp-filtering-profiles)
8. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
9. [Error Handling](#error-handling)
10. [Best Practices](#best-practices)
11. [Related Models](#related-models)

## Overview

The `BgpFilteringProfile` class manages BGP filtering profile objects in Palo Alto Networks' Strata Cloud Manager. It extends from `BaseObject` and offers methods to create, retrieve, update, list, fetch, and delete BGP filtering profiles. These profiles define route filtering for BGP peer groups using filter lists, network filters, route maps, conditional advertisements, and unsuppress maps. Unicast filtering uses `BgpFilter` directly, while multicast supports either inheriting from unicast or defining its own filter fields (mutually exclusive).

## Core Methods

| Method     | Description                                                        | Parameters                                                                                                                       | Return Type                               |
|------------|--------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------|
| `create()` | Creates a new BGP filtering profile                                | `data: Dict[str, Any]`                                                                                                           | `BgpFilteringProfileResponseModel`        |
| `get()`    | Retrieves a BGP filtering profile by its unique ID                 | `object_id: str`                                                                                                                 | `BgpFilteringProfileResponseModel`        |
| `update()` | Updates an existing BGP filtering profile                          | `profile: BgpFilteringProfileUpdateModel`                                                                                        | `BgpFilteringProfileResponseModel`        |
| `list()`   | Lists BGP filtering profiles with optional filtering               | `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`, `exact_match: bool = False`, plus additional filters | `List[BgpFilteringProfileResponseModel]`  |
| `fetch()`  | Fetches a single BGP filtering profile by name within a container  | `name: str`, `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`                                          | `BgpFilteringProfileResponseModel`        |
| `delete()` | Deletes a BGP filtering profile by its ID                          | `object_id: str`                                                                                                                 | `None`                                    |

## BGP Filtering Profile Model Attributes

| Attribute | Type                       | Required | Default | Description                                         |
|-----------|----------------------------|----------|---------|-----------------------------------------------------|
| `name`    | str                        | Yes      | None    | Profile name                                        |
| `id`      | UUID                       | Yes*     | None    | Unique identifier (*response/update only)           |
| `ipv4`    | BgpFilteringProfileIpv4    | No       | None    | IPv4 filtering configuration                        |
| `folder`  | str                        | No**     | None    | Folder location. Max 64 chars                       |
| `snippet` | str                        | No**     | None    | Snippet location. Max 64 chars                      |
| `device`  | str                        | No**     | None    | Device location. Max 64 chars                       |

\* Only required for update and response models
\** Exactly one container (folder/snippet/device) must be provided for create operations

## IPv4 Filtering Configuration

The `ipv4` attribute wraps unicast and multicast filtering configurations.

### BgpFilteringProfileIpv4

| Attribute   | Type                          | Required | Description                    |
|-------------|-------------------------------|----------|--------------------------------|
| `unicast`   | BgpFilter                     | No       | Unicast filtering              |
| `multicast` | BgpFilteringProfileMulticast   | No       | Multicast filtering            |

### BgpFilter (used by unicast)

| Attribute                   | Type                          | Required | Description                         |
|-----------------------------|-------------------------------|----------|-------------------------------------|
| `filter_list`               | BgpFilterList                 | No       | Filter list configuration           |
| `inbound_network_filters`   | BgpNetworkFilters             | No       | Inbound network filters             |
| `outbound_network_filters`  | BgpNetworkFilters             | No       | Outbound network filters            |
| `route_maps`                | BgpRouteMaps                  | No       | Route maps configuration            |
| `conditional_advertisement` | BgpConditionalAdvertisement   | No       | Conditional advertisement config    |
| `unsuppress_map`            | str                           | No       | Unsuppress map name                 |

### BgpFilteringProfileMulticast (oneOf: inherit or filter fields)

| Attribute                   | Type                          | Required | Description                                              |
|-----------------------------|-------------------------------|----------|----------------------------------------------------------|
| `inherit`                   | bool                          | No       | Inherit filtering from unicast (mutually exclusive with filter fields) |
| `filter_list`               | BgpFilterList                 | No       | Filter list (mutually exclusive with inherit)            |
| `inbound_network_filters`   | BgpNetworkFilters             | No       | Inbound network filters (mutually exclusive with inherit)|
| `outbound_network_filters`  | BgpNetworkFilters             | No       | Outbound network filters (mutually exclusive with inherit)|
| `route_maps`                | BgpRouteMaps                  | No       | Route maps (mutually exclusive with inherit)             |
| `conditional_advertisement` | BgpConditionalAdvertisement   | No       | Conditional advertisement (mutually exclusive with inherit)|
| `unsuppress_map`            | str                           | No       | Unsuppress map (mutually exclusive with inherit)         |

### BgpFilterList

| Attribute  | Type | Required | Description                |
|------------|------|----------|----------------------------|
| `inbound`  | str  | No       | Inbound filter list name   |
| `outbound` | str  | No       | Outbound filter list name  |

### BgpNetworkFilters

| Attribute        | Type | Required | Description            |
|------------------|------|----------|------------------------|
| `distribute_list` | str | No       | Distribute list name   |
| `prefix_list`    | str  | No       | Prefix list name       |

### BgpRouteMaps

| Attribute  | Type | Required | Description              |
|------------|------|----------|--------------------------|
| `inbound`  | str  | No       | Inbound route map name   |
| `outbound` | str  | No       | Outbound route map name  |

### BgpConditionalAdvertisement

| Attribute   | Type                                    | Required | Description          |
|-------------|-----------------------------------------|----------|----------------------|
| `exist`     | BgpConditionalAdvertisementCondition    | No       | Exist condition      |
| `non_exist` | BgpConditionalAdvertisementCondition    | No       | Non-exist condition  |

### BgpConditionalAdvertisementCondition

| Attribute       | Type | Required | Description           |
|-----------------|------|----------|-----------------------|
| `advertise_map` | str  | No       | Advertise map name    |

## Exceptions

| Exception                    | HTTP Code | Description                                                                   |
|------------------------------|-----------|-------------------------------------------------------------------------------|
| `InvalidObjectError`         | 400       | Thrown when provided data or parameters are invalid                           |
| `MissingQueryParameterError` | 400       | Thrown when required query parameters (e.g., `name` or `folder`) are missing  |
| `NameNotUniqueError`         | 409       | Profile name already exists                                                   |
| `ObjectNotPresentError`      | 404       | Profile not found                                                             |
| `ReferenceNotZeroError`      | 409       | Profile still referenced                                                      |
| `AuthenticationError`        | 401       | Authentication failed                                                         |
| `ServerError`                | 500       | Internal server error                                                         |

## Basic Configuration

The BGP Filtering Profile service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

### Unified Client Interface (Recommended)

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Access the BGP Filtering Profile service directly through the client
bgp_filtering_profiles = client.bgp_filtering_profile
```

### Traditional Service Instantiation (Legacy)

```python
from scm.client import Scm
from scm.config.network import BgpFilteringProfile

# Initialize client
client = Scm(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Initialize BgpFilteringProfile object explicitly
bgp_filtering_profiles = BgpFilteringProfile(client)
```

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

## Usage Examples

### Creating BGP Filtering Profiles

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Create a profile with unicast route maps
profile_data = {
   "name": "peer-group-filters",
   "ipv4": {
      "unicast": {
         "route_maps": {
            "inbound": "import-route-map",
            "outbound": "export-route-map"
         },
         "filter_list": {
            "inbound": "inbound-filter",
            "outbound": "outbound-filter"
         }
      }
   },
   "folder": "Texas"
}

new_profile = client.bgp_filtering_profile.create(profile_data)
print(f"Created filtering profile with ID: {new_profile.id}")

# Create a profile with network filters and conditional advertisement
advanced_profile_data = {
   "name": "advanced-filters",
   "ipv4": {
      "unicast": {
         "inbound_network_filters": {
            "prefix_list": "inbound-prefix-list"
         },
         "outbound_network_filters": {
            "distribute_list": "outbound-dist-list"
         },
         "conditional_advertisement": {
            "non_exist": {
               "advertise_map": "conditional-map"
            }
         }
      }
   },
   "folder": "Texas"
}

advanced_profile = client.bgp_filtering_profile.create(advanced_profile_data)
print(f"Created advanced filtering profile with ID: {advanced_profile.id}")

# Create a profile with multicast inheriting from unicast
inherit_profile_data = {
   "name": "inherit-multicast",
   "ipv4": {
      "unicast": {
         "route_maps": {
            "inbound": "unicast-import"
         }
      },
      "multicast": {
         "inherit": True
      }
   },
   "folder": "Texas"
}

inherit_profile = client.bgp_filtering_profile.create(inherit_profile_data)
print(f"Created inherit profile with ID: {inherit_profile.id}")
```

### Retrieving BGP Filtering Profiles

```python
# Fetch by name and folder
profile = client.bgp_filtering_profile.fetch(
   name="peer-group-filters",
   folder="Texas"
)
print(f"Found profile: {profile.name}")
if profile.ipv4 and profile.ipv4.unicast:
   if profile.ipv4.unicast.route_maps:
      print(f"  Inbound route map: {profile.ipv4.unicast.route_maps.inbound}")
      print(f"  Outbound route map: {profile.ipv4.unicast.route_maps.outbound}")

# Get by ID
profile_by_id = client.bgp_filtering_profile.get(profile.id)
print(f"Retrieved profile: {profile_by_id.name}")
```

### Updating BGP Filtering Profiles

```python
# Fetch existing profile
existing_profile = client.bgp_filtering_profile.fetch(
   name="peer-group-filters",
   folder="Texas"
)

# Add an unsuppress map
existing_profile.ipv4.unicast.unsuppress_map = "unsuppress-specific"

# Perform update
updated_profile = client.bgp_filtering_profile.update(existing_profile)
```

### Listing BGP Filtering Profiles

```python
# List all filtering profiles in a folder
profiles = client.bgp_filtering_profile.list(
   folder="Texas"
)

# Process results
for profile in profiles:
   print(f"Name: {profile.name}")
   if profile.ipv4 and profile.ipv4.unicast:
      print(f"  Has unicast filtering")
   if profile.ipv4 and profile.ipv4.multicast:
      print(f"  Has multicast filtering")
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
# Only return profiles defined exactly in 'Texas'
exact_profiles = client.bgp_filtering_profile.list(
   folder='Texas',
   exact_match=True
)

for profile in exact_profiles:
   print(f"Exact match: {profile.name} in {profile.folder}")

# Exclude all profiles from the 'All' folder
no_all_profiles = client.bgp_filtering_profile.list(
   folder='Texas',
   exclude_folders=['All']
)

for profile in no_all_profiles:
   assert profile.folder != 'All'
   print(f"Filtered out 'All': {profile.name}")
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
client.bgp_filtering_profile.max_limit = 4000

# List all profiles - auto-paginates through results
all_profiles = client.bgp_filtering_profile.list(folder='Texas')
```

### Deleting BGP Filtering Profiles

```python
# Delete by ID
profile_id = "123e4567-e89b-12d3-a456-426655440000"
client.bgp_filtering_profile.delete(profile_id)
```

## Managing Configuration Changes

### Performing Commits

```python
# Prepare commit parameters
commit_params = {
   "folders": ["Texas"],
   "description": "Updated BGP filtering profile configurations",
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
   # Create BGP filtering profile
   profile_config = {
      "name": "test-filtering",
      "ipv4": {
         "unicast": {
            "route_maps": {
               "inbound": "test-import-map"
            }
         }
      },
      "folder": "Texas"
   }

   new_profile = client.bgp_filtering_profile.create(profile_config)

   # Commit changes
   result = client.commit(
      folders=["Texas"],
      description="Added BGP filtering profile",
      sync=True
   )

   # Check job status
   status = client.get_job_status(result.job_id)

except InvalidObjectError as e:
   print(f"Invalid profile data: {e.message}")
except NameNotUniqueError as e:
   print(f"Profile name already exists: {e.message}")
except ObjectNotPresentError as e:
   print(f"Profile not found: {e.message}")
except ReferenceNotZeroError as e:
   print(f"Profile still in use: {e.message}")
except MissingQueryParameterError as e:
   print(f"Missing parameter: {e.message}")
```

## Best Practices

1. **Client Usage**
   - Use the unified client interface (`client.bgp_filtering_profile`) for streamlined code
   - Create a single client instance and reuse it across your application
   - Perform commit operations directly on the client object (`client.commit()`)

2. **Filtering Design**
   - Use route maps for complex policy decisions that require both matching and setting attributes
   - Use filter lists for simple AS-path based filtering
   - Use prefix lists in network filters for prefix-based filtering
   - Combine inbound and outbound filters for complete route control

3. **Multicast Configuration**
   - Use `inherit: true` for multicast when the same filtering as unicast is desired
   - When setting multicast-specific filters, do not set `inherit` (they are mutually exclusive)
   - Test multicast filter configurations separately from unicast

4. **Conditional Advertisement**
   - Use `exist` conditions to advertise routes only when a specific prefix exists
   - Use `non_exist` conditions to advertise routes only when a prefix is absent
   - Ensure referenced advertise maps are created before the filtering profile

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
   - Cache frequently accessed profile configurations
   - Implement proper retry mechanisms

## Related Models

- [BgpFilteringProfileBaseModel](../../models/network/bgp_filtering_profile_models.md#Overview)
- [BgpFilteringProfileCreateModel](../../models/network/bgp_filtering_profile_models.md#Overview)
- [BgpFilteringProfileUpdateModel](../../models/network/bgp_filtering_profile_models.md#Overview)
- [BgpFilteringProfileResponseModel](../../models/network/bgp_filtering_profile_models.md#Overview)
- [BgpFilter](../../models/network/bgp_filtering_profile_models.md#Overview)
- [BgpFilteringProfileMulticast](../../models/network/bgp_filtering_profile_models.md#Overview)
