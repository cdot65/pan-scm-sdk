# BGP Redistribution Profile Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [BGP Redistribution Profile Model Attributes](#bgp-redistribution-profile-model-attributes)
4. [IPv4 Redistribution Configuration](#ipv4-redistribution-configuration)
5. [Exceptions](#exceptions)
6. [Basic Configuration](#basic-configuration)
7. [Usage Examples](#usage-examples)
    - [Creating BGP Redistribution Profiles](#creating-bgp-redistribution-profiles)
    - [Retrieving BGP Redistribution Profiles](#retrieving-bgp-redistribution-profiles)
    - [Updating BGP Redistribution Profiles](#updating-bgp-redistribution-profiles)
    - [Listing BGP Redistribution Profiles](#listing-bgp-redistribution-profiles)
    - [Filtering Responses](#filtering-responses)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Deleting BGP Redistribution Profiles](#deleting-bgp-redistribution-profiles)
8. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
9. [Error Handling](#error-handling)
10. [Best Practices](#best-practices)
11. [Related Models](#related-models)

## Overview

The `BgpRedistributionProfile` class manages BGP redistribution profile objects in Palo Alto Networks' Strata Cloud Manager. It extends from `BaseObject` and offers methods to create, retrieve, update, list, fetch, and delete BGP redistribution profiles. These profiles define route redistribution settings between BGP and other routing protocols (static, OSPF, connected). Unlike mutual exclusion patterns, all three protocol redistributions (static, ospf, connected) can coexist within the same unicast configuration.

## Core Methods

| Method     | Description                                                           | Parameters                                                                                                                       | Return Type                                    |
|------------|-----------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------|
| `create()` | Creates a new BGP redistribution profile                              | `data: Dict[str, Any]`                                                                                                           | `BgpRedistributionProfileResponseModel`        |
| `get()`    | Retrieves a BGP redistribution profile by its unique ID               | `object_id: str`                                                                                                                 | `BgpRedistributionProfileResponseModel`        |
| `update()` | Updates an existing BGP redistribution profile                        | `profile: BgpRedistributionProfileUpdateModel`                                                                                   | `BgpRedistributionProfileResponseModel`        |
| `list()`   | Lists BGP redistribution profiles with optional filtering             | `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`, `exact_match: bool = False`, plus additional filters | `List[BgpRedistributionProfileResponseModel]`  |
| `fetch()`  | Fetches a single BGP redistribution profile by name within a container| `name: str`, `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`                                          | `BgpRedistributionProfileResponseModel`        |
| `delete()` | Deletes a BGP redistribution profile by its ID                        | `object_id: str`                                                                                                                 | `None`                                         |

## BGP Redistribution Profile Model Attributes

| Attribute | Type                    | Required | Default | Description                                         |
|-----------|-------------------------|----------|---------|-----------------------------------------------------|
| `name`    | str                     | Yes      | None    | Profile name                                        |
| `id`      | UUID                    | Yes*     | None    | Unique identifier (*response/update only)           |
| `ipv4`    | BgpRedistributionIpv4   | No       | None    | IPv4 redistribution configuration                   |
| `folder`  | str                     | No**     | None    | Folder location. Max 64 chars                       |
| `snippet` | str                     | No**     | None    | Snippet location. Max 64 chars                      |
| `device`  | str                     | No**     | None    | Device location. Max 64 chars                       |

\* Only required for update and response models
\** Exactly one container (folder/snippet/device) must be provided for create operations

## IPv4 Redistribution Configuration

The `ipv4` attribute wraps unicast redistribution settings for static, OSPF, and connected routes.

### BgpRedistributionIpv4

| Attribute | Type                       | Required | Description                         |
|-----------|----------------------------|----------|-------------------------------------|
| `unicast` | BgpRedistributionUnicast   | No       | Unicast redistribution config       |

### BgpRedistributionUnicast

| Attribute   | Type                        | Required | Description                          |
|-------------|-----------------------------|----------|--------------------------------------|
| `static`    | BgpRedistributionProtocol   | No       | Static route redistribution          |
| `ospf`      | BgpRedistributionProtocol   | No       | OSPF route redistribution            |
| `connected` | BgpRedistributionProtocol   | No       | Connected route redistribution       |

All three protocols can be configured simultaneously (they are not mutually exclusive).

### BgpRedistributionProtocol

| Attribute   | Type | Required | Description                              |
|-------------|------|----------|------------------------------------------|
| `enable`    | bool | No       | Enable redistribution for this protocol  |
| `metric`    | int  | No       | Metric value (1-65535)                   |
| `route_map` | str  | No       | Route map name to apply                  |

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

The BGP Redistribution Profile service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

### Unified Client Interface (Recommended)

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Access the BGP Redistribution Profile service directly through the client
bgp_redist_profiles = client.bgp_redistribution_profile
```

### Traditional Service Instantiation (Legacy)

```python
from scm.client import Scm
from scm.config.network import BgpRedistributionProfile

# Initialize client
client = Scm(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Initialize BgpRedistributionProfile object explicitly
bgp_redist_profiles = BgpRedistributionProfile(client)
```

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

## Usage Examples

### Creating BGP Redistribution Profiles

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Create a profile redistributing static routes into BGP
static_redist_data = {
   "name": "redist-static",
   "ipv4": {
      "unicast": {
         "static": {
            "enable": True,
            "metric": 100,
            "route_map": "static-to-bgp-map"
         }
      }
   },
   "folder": "Texas"
}

new_profile = client.bgp_redistribution_profile.create(static_redist_data)
print(f"Created redistribution profile with ID: {new_profile.id}")

# Create a profile redistributing multiple protocols
multi_redist_data = {
   "name": "redist-all-protocols",
   "ipv4": {
      "unicast": {
         "static": {
            "enable": True,
            "metric": 200
         },
         "ospf": {
            "enable": True,
            "metric": 150,
            "route_map": "ospf-to-bgp-map"
         },
         "connected": {
            "enable": True,
            "metric": 50
         }
      }
   },
   "folder": "Texas"
}

multi_profile = client.bgp_redistribution_profile.create(multi_redist_data)
print(f"Created multi-protocol redistribution profile with ID: {multi_profile.id}")

# Create a profile with only connected routes
connected_only_data = {
   "name": "redist-connected-only",
   "ipv4": {
      "unicast": {
         "connected": {
            "enable": True,
            "route_map": "connected-filter"
         }
      }
   },
   "folder": "Texas"
}

connected_profile = client.bgp_redistribution_profile.create(connected_only_data)
print(f"Created connected-only profile with ID: {connected_profile.id}")
```

### Retrieving BGP Redistribution Profiles

```python
# Fetch by name and folder
profile = client.bgp_redistribution_profile.fetch(
   name="redist-all-protocols",
   folder="Texas"
)
print(f"Found profile: {profile.name}")
if profile.ipv4 and profile.ipv4.unicast:
   unicast = profile.ipv4.unicast
   if unicast.static:
      print(f"  Static: enabled={unicast.static.enable}, metric={unicast.static.metric}")
   if unicast.ospf:
      print(f"  OSPF: enabled={unicast.ospf.enable}, metric={unicast.ospf.metric}")
   if unicast.connected:
      print(f"  Connected: enabled={unicast.connected.enable}, metric={unicast.connected.metric}")

# Get by ID
profile_by_id = client.bgp_redistribution_profile.get(profile.id)
print(f"Retrieved profile: {profile_by_id.name}")
```

### Updating BGP Redistribution Profiles

```python
# Fetch existing profile
existing_profile = client.bgp_redistribution_profile.fetch(
   name="redist-static",
   folder="Texas"
)

# Add OSPF redistribution
existing_profile.ipv4.unicast.ospf = {
   "enable": True,
   "metric": 300,
   "route_map": "ospf-redist-map"
}

# Perform update
updated_profile = client.bgp_redistribution_profile.update(existing_profile)
```

### Listing BGP Redistribution Profiles

```python
# List all redistribution profiles in a folder
profiles = client.bgp_redistribution_profile.list(
   folder="Texas"
)

# Process results
for profile in profiles:
   print(f"Name: {profile.name}")
   if profile.ipv4 and profile.ipv4.unicast:
      protocols = []
      if profile.ipv4.unicast.static:
         protocols.append("static")
      if profile.ipv4.unicast.ospf:
         protocols.append("ospf")
      if profile.ipv4.unicast.connected:
         protocols.append("connected")
      print(f"  Redistributing: {', '.join(protocols)}")
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
exact_profiles = client.bgp_redistribution_profile.list(
   folder='Texas',
   exact_match=True
)

for profile in exact_profiles:
   print(f"Exact match: {profile.name} in {profile.folder}")

# Exclude all profiles from the 'All' folder
no_all_profiles = client.bgp_redistribution_profile.list(
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
client.bgp_redistribution_profile.max_limit = 4000

# List all profiles - auto-paginates through results
all_profiles = client.bgp_redistribution_profile.list(folder='Texas')
```

### Deleting BGP Redistribution Profiles

```python
# Delete by ID
profile_id = "123e4567-e89b-12d3-a456-426655440000"
client.bgp_redistribution_profile.delete(profile_id)
```

## Managing Configuration Changes

### Performing Commits

```python
# Prepare commit parameters
commit_params = {
   "folders": ["Texas"],
   "description": "Updated BGP redistribution profile configurations",
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
   # Create BGP redistribution profile
   profile_config = {
      "name": "test-redistribution",
      "ipv4": {
         "unicast": {
            "connected": {
               "enable": True,
               "metric": 100
            }
         }
      },
      "folder": "Texas"
   }

   new_profile = client.bgp_redistribution_profile.create(profile_config)

   # Commit changes
   result = client.commit(
      folders=["Texas"],
      description="Added BGP redistribution profile",
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
   - Use the unified client interface (`client.bgp_redistribution_profile`) for streamlined code
   - Create a single client instance and reuse it across your application
   - Perform commit operations directly on the client object (`client.commit()`)

2. **Redistribution Configuration**
   - Always use route maps with redistribution to control which routes are redistributed
   - Set appropriate metric values to influence route preference
   - Enable only the protocols that need redistribution to avoid routing loops
   - All three protocols (static, ospf, connected) can coexist in the same profile

3. **Route Map Integration**
   - Create route maps before referencing them in redistribution profiles
   - Use route maps to filter specific prefixes during redistribution
   - Apply different metrics through route maps for granular control

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
   - Cache frequently accessed profile configurations
   - Implement proper retry mechanisms

## Related Models

- [BgpRedistributionProfileBaseModel](../../models/network/bgp_redistribution_profile_models.md#Overview)
- [BgpRedistributionProfileCreateModel](../../models/network/bgp_redistribution_profile_models.md#Overview)
- [BgpRedistributionProfileUpdateModel](../../models/network/bgp_redistribution_profile_models.md#Overview)
- [BgpRedistributionProfileResponseModel](../../models/network/bgp_redistribution_profile_models.md#Overview)
- [BgpRedistributionProtocol](../../models/network/bgp_redistribution_profile_models.md#Overview)
