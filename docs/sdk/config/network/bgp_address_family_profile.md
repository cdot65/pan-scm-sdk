# BGP Address Family Profile Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [BGP Address Family Profile Model Attributes](#bgp-address-family-profile-model-attributes)
4. [IPv4 Unicast/Multicast Configuration](#ipv4-unicastmulticast-configuration)
5. [Exceptions](#exceptions)
6. [Basic Configuration](#basic-configuration)
7. [Usage Examples](#usage-examples)
    - [Creating BGP Address Family Profiles](#creating-bgp-address-family-profiles)
    - [Retrieving BGP Address Family Profiles](#retrieving-bgp-address-family-profiles)
    - [Updating BGP Address Family Profiles](#updating-bgp-address-family-profiles)
    - [Listing BGP Address Family Profiles](#listing-bgp-address-family-profiles)
    - [Filtering Responses](#filtering-responses)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Deleting BGP Address Family Profiles](#deleting-bgp-address-family-profiles)
8. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
9. [Error Handling](#error-handling)
10. [Best Practices](#best-practices)
11. [Related Models](#related-models)

## Overview

The `BgpAddressFamilyProfile` class manages BGP address family profile objects in Palo Alto Networks' Strata Cloud Manager. It extends from `BaseObject` and offers methods to create, retrieve, update, list, fetch, and delete BGP address family profiles. These profiles define IPv4 unicast and multicast settings for BGP peer groups, including add-path, allowas-in, maximum prefix limits, next-hop behavior, remove-private-AS, send-community, and ORF configuration.

## Core Methods

| Method     | Description                                                          | Parameters                                                                                                                       | Return Type                                  |
|------------|----------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------|
| `create()` | Creates a new BGP address family profile                             | `data: Dict[str, Any]`                                                                                                           | `BgpAddressFamilyProfileResponseModel`       |
| `get()`    | Retrieves a BGP address family profile by its unique ID              | `object_id: str`                                                                                                                 | `BgpAddressFamilyProfileResponseModel`       |
| `update()` | Updates an existing BGP address family profile                       | `profile: BgpAddressFamilyProfileUpdateModel`                                                                                    | `BgpAddressFamilyProfileResponseModel`       |
| `list()`   | Lists BGP address family profiles with optional filtering            | `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`, `exact_match: bool = False`, plus additional filters | `List[BgpAddressFamilyProfileResponseModel]` |
| `fetch()`  | Fetches a single BGP address family profile by name within a container | `name: str`, `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`                                        | `BgpAddressFamilyProfileResponseModel`       |
| `delete()` | Deletes a BGP address family profile by its ID                       | `object_id: str`                                                                                                                 | `None`                                       |

## BGP Address Family Profile Model Attributes

| Attribute  | Type                                          | Required | Default | Description                                         |
|------------|-----------------------------------------------|----------|---------|-----------------------------------------------------|
| `name`     | str                                           | Yes      | None    | Profile name                                        |
| `id`       | UUID                                          | Yes*     | None    | Unique identifier (*response/update only)           |
| `ipv4`     | BgpAddressFamilyProfileIpv4UnicastMulticast   | No       | None    | IPv4 address family configuration                   |
| `folder`   | str                                           | No**     | None    | Folder location. Max 64 chars                       |
| `snippet`  | str                                           | No**     | None    | Snippet location. Max 64 chars                      |
| `device`   | str                                           | No**     | None    | Device location. Max 64 chars                       |

\* Only required for update and response models
\** Exactly one container (folder/snippet/device) must be provided for create operations

## IPv4 Unicast/Multicast Configuration

The `ipv4` attribute wraps unicast and multicast address family settings. Both unicast and multicast share the same `BgpAddressFamily` model structure.

### BgpAddressFamilyProfileIpv4UnicastMulticast

| Attribute   | Type              | Required | Description                    |
|-------------|-------------------|----------|--------------------------------|
| `unicast`   | BgpAddressFamily  | No       | Unicast address family         |
| `multicast` | BgpAddressFamily  | No       | Multicast address family       |

### BgpAddressFamily

| Attribute                      | Type                              | Required | Description                                        |
|--------------------------------|-----------------------------------|----------|----------------------------------------------------|
| `enable`                       | bool                              | No       | Enable address family                              |
| `soft_reconfig_with_stored_info` | bool                            | No       | Soft reconfiguration with stored routes            |
| `add_path`                     | BgpAddressFamilyAddPath           | No       | Add-path configuration                             |
| `as_override`                  | bool                              | No       | Override ASNs in outbound updates                  |
| `route_reflector_client`       | bool                              | No       | Route reflector client                             |
| `default_originate`            | bool                              | No       | Originate default route                            |
| `default_originate_map`        | str                               | No       | Default originate route map                        |
| `allowas_in`                   | BgpAddressFamilyAllowasIn         | No       | Allow-AS-in configuration                          |
| `maximum_prefix`               | BgpAddressFamilyMaximumPrefix     | No       | Maximum prefix configuration                       |
| `next_hop`                     | BgpAddressFamilyNextHop           | No       | Next-hop configuration                             |
| `remove_private_AS`            | BgpAddressFamilyRemovePrivateAS   | No       | Remove private AS configuration                    |
| `send_community`               | BgpAddressFamilySendCommunity     | No       | Send community configuration                       |
| `orf`                          | BgpAddressFamilyOrf               | No       | ORF configuration                                  |

### BgpAddressFamilyAddPath

| Attribute            | Type | Required | Description                              |
|----------------------|------|----------|------------------------------------------|
| `tx_all_paths`       | bool | No       | Advertise all paths to peer              |
| `tx_bestpath_per_AS` | bool | No       | Advertise bestpath per neighboring AS    |

### BgpAddressFamilyAllowasIn (oneOf)

| Attribute    | Type | Required | Description                                 |
|--------------|------|----------|---------------------------------------------|
| `origin`     | dict | No       | Allow origin AS in path (mutually exclusive with occurrence) |
| `occurrence` | int  | No       | Number of times own AS can appear (1-10, mutually exclusive with origin) |

### BgpAddressFamilyMaximumPrefix

| Attribute      | Type                                  | Required | Description                |
|----------------|---------------------------------------|----------|----------------------------|
| `num_prefixes` | int                                   | No       | Maximum number of prefixes (1-4294967295) |
| `threshold`    | int                                   | No       | Threshold percentage (1-100) |
| `action`       | BgpAddressFamilyMaximumPrefixAction   | No       | Action on limit            |

### BgpAddressFamilyNextHop (oneOf)

| Attribute    | Type | Required | Description                                     |
|--------------|------|----------|-------------------------------------------------|
| `self`       | dict | No       | Set next-hop to self (mutually exclusive with self_force) |
| `self_force` | dict | No       | Force next-hop to self (mutually exclusive with self) |

### BgpAddressFamilySendCommunity (oneOf)

| Attribute   | Type | Required | Description                                      |
|-------------|------|----------|--------------------------------------------------|
| `all`       | dict | No       | Send all communities                             |
| `both`      | dict | No       | Send both standard and extended                  |
| `extended`  | dict | No       | Send extended communities                        |
| `large`     | dict | No       | Send large communities                           |
| `standard`  | dict | No       | Send standard communities                        |

Only one send community type may be set at a time.

### BgpAddressFamilyOrf

| Attribute        | Type | Required | Description                              |
|------------------|------|----------|------------------------------------------|
| `orf_prefix_list` | str | No       | ORF prefix list mode (none, both, receive, send) |

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

The BGP Address Family Profile service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

### Unified Client Interface (Recommended)

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Access the BGP Address Family Profile service directly through the client
bgp_af_profiles = client.bgp_address_family_profile
```

### Traditional Service Instantiation (Legacy)

```python
from scm.client import Scm
from scm.config.network import BgpAddressFamilyProfile

# Initialize client
client = Scm(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Initialize BgpAddressFamilyProfile object explicitly
bgp_af_profiles = BgpAddressFamilyProfile(client)
```

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

## Usage Examples

### Creating BGP Address Family Profiles

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Create a basic unicast profile with send-community
profile_data = {
   "name": "unicast-basic",
   "ipv4": {
      "unicast": {
         "enable": True,
         "send_community": {
            "all": {}
         },
         "next_hop": {
            "self": {}
         }
      }
   },
   "folder": "Texas"
}

new_profile = client.bgp_address_family_profile.create(profile_data)
print(f"Created profile with ID: {new_profile.id}")

# Create a profile with maximum prefix and allowas-in
advanced_profile_data = {
   "name": "unicast-advanced",
   "ipv4": {
      "unicast": {
         "enable": True,
         "maximum_prefix": {
            "num_prefixes": 10000,
            "threshold": 80,
            "action": {
               "restart": {
                  "interval": 120
               }
            }
         },
         "allowas_in": {
            "occurrence": 3
         },
         "remove_private_AS": {
            "all": {}
         },
         "soft_reconfig_with_stored_info": True
      }
   },
   "folder": "Texas"
}

advanced_profile = client.bgp_address_family_profile.create(advanced_profile_data)
print(f"Created advanced profile with ID: {advanced_profile.id}")

# Create a profile with both unicast and multicast
dual_profile_data = {
   "name": "dual-af-profile",
   "ipv4": {
      "unicast": {
         "enable": True,
         "send_community": {
            "standard": {}
         }
      },
      "multicast": {
         "enable": True,
         "default_originate": True
      }
   },
   "folder": "Texas"
}

dual_profile = client.bgp_address_family_profile.create(dual_profile_data)
print(f"Created dual AF profile with ID: {dual_profile.id}")
```

### Retrieving BGP Address Family Profiles

```python
# Fetch by name and folder
profile = client.bgp_address_family_profile.fetch(
   name="unicast-basic",
   folder="Texas"
)
print(f"Found profile: {profile.name}")

# Get by ID
profile_by_id = client.bgp_address_family_profile.get(profile.id)
print(f"Retrieved profile: {profile_by_id.name}")
```

### Updating BGP Address Family Profiles

```python
# Fetch existing profile
existing_profile = client.bgp_address_family_profile.fetch(
   name="unicast-basic",
   folder="Texas"
)

# Enable add-path
existing_profile.ipv4.unicast.add_path = {
   "tx_all_paths": True
}

# Perform update
updated_profile = client.bgp_address_family_profile.update(existing_profile)
```

### Listing BGP Address Family Profiles

```python
# List all profiles in a folder
profiles = client.bgp_address_family_profile.list(
   folder="Texas"
)

# Process results
for profile in profiles:
   print(f"Name: {profile.name}")
   if profile.ipv4 and profile.ipv4.unicast:
      print(f"  Unicast enabled: {profile.ipv4.unicast.enable}")
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
exact_profiles = client.bgp_address_family_profile.list(
   folder='Texas',
   exact_match=True
)

for profile in exact_profiles:
   print(f"Exact match: {profile.name} in {profile.folder}")

# Exclude all profiles from the 'All' folder
no_all_profiles = client.bgp_address_family_profile.list(
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
client.bgp_address_family_profile.max_limit = 4000

# List all profiles - auto-paginates through results
all_profiles = client.bgp_address_family_profile.list(folder='Texas')
```

### Deleting BGP Address Family Profiles

```python
# Delete by ID
profile_id = "123e4567-e89b-12d3-a456-426655440000"
client.bgp_address_family_profile.delete(profile_id)
```

## Managing Configuration Changes

### Performing Commits

```python
# Prepare commit parameters
commit_params = {
   "folders": ["Texas"],
   "description": "Updated BGP address family profile configurations",
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
   # Create BGP address family profile
   profile_config = {
      "name": "test-af-profile",
      "ipv4": {
         "unicast": {
            "enable": True
         }
      },
      "folder": "Texas"
   }

   new_profile = client.bgp_address_family_profile.create(profile_config)

   # Commit changes
   result = client.commit(
      folders=["Texas"],
      description="Added BGP address family profile",
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
   - Use the unified client interface (`client.bgp_address_family_profile`) for streamlined code
   - Create a single client instance and reuse it across your application
   - Perform commit operations directly on the client object (`client.commit()`)

2. **Address Family Configuration**
   - Enable only the address families (unicast/multicast) that are needed for your deployment
   - Configure maximum prefix limits to protect against route table overflow
   - Use `soft_reconfig_with_stored_info` to allow policy changes without resetting BGP sessions
   - Set appropriate `send_community` types based on your community usage

3. **Route Control**
   - Use `allowas_in` carefully and only when required for hub-and-spoke topologies
   - Configure `remove_private_AS` when advertising routes to external peers
   - Use `next_hop` self when acting as a route reflector or in iBGP scenarios
   - Set `as_override` only when necessary for overlapping AS environments

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

- [BgpAddressFamilyProfileBaseModel](../../models/network/bgp_address_family_profile_models.md#Overview)
- [BgpAddressFamilyProfileCreateModel](../../models/network/bgp_address_family_profile_models.md#Overview)
- [BgpAddressFamilyProfileUpdateModel](../../models/network/bgp_address_family_profile_models.md#Overview)
- [BgpAddressFamilyProfileResponseModel](../../models/network/bgp_address_family_profile_models.md#Overview)
- [BgpAddressFamily](../../models/network/bgp_address_family_profile_models.md#Overview)
