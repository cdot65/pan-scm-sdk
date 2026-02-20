# BGP Auth Profile Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [BGP Auth Profile Model Attributes](#bgp-auth-profile-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating BGP Auth Profiles](#creating-bgp-auth-profiles)
    - [Retrieving BGP Auth Profiles](#retrieving-bgp-auth-profiles)
    - [Updating BGP Auth Profiles](#updating-bgp-auth-profiles)
    - [Listing BGP Auth Profiles](#listing-bgp-auth-profiles)
    - [Filtering Responses](#filtering-responses)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Deleting BGP Auth Profiles](#deleting-bgp-auth-profiles)
7. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Related Models](#related-models)

## Overview

The `BgpAuthProfile` class manages BGP authentication profile objects in Palo Alto Networks' Strata Cloud Manager. It extends from `BaseObject` and offers methods to create, retrieve, update, list, fetch, and delete BGP authentication profiles. These profiles provide MD5 authentication for BGP sessions, defining a shared secret used to authenticate BGP messages between peers.

## Core Methods

| Method     | Description                                                    | Parameters                                                                                                                       | Return Type                        |
|------------|----------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|------------------------------------|
| `create()` | Creates a new BGP auth profile                                 | `data: Dict[str, Any]`                                                                                                           | `BgpAuthProfileResponseModel`      |
| `get()`    | Retrieves a BGP auth profile by its unique ID                  | `object_id: str`                                                                                                                 | `BgpAuthProfileResponseModel`      |
| `update()` | Updates an existing BGP auth profile                           | `profile: BgpAuthProfileUpdateModel`                                                                                             | `BgpAuthProfileResponseModel`      |
| `list()`   | Lists BGP auth profiles with optional filtering                | `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`, `exact_match: bool = False`, plus additional filters | `List[BgpAuthProfileResponseModel]`|
| `fetch()`  | Fetches a single BGP auth profile by name within a container   | `name: str`, `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`                                          | `BgpAuthProfileResponseModel`      |
| `delete()` | Deletes a BGP auth profile by its ID                           | `object_id: str`                                                                                                                 | `None`                             |

## BGP Auth Profile Model Attributes

| Attribute | Type | Required | Default | Description                                         |
|-----------|------|----------|---------|-----------------------------------------------------|
| `name`    | str  | Yes      | None    | Profile name                                        |
| `id`      | UUID | Yes*     | None    | Unique identifier (*response/update only)           |
| `secret`  | str  | No       | None    | BGP authentication key (MD5 shared secret)          |
| `folder`  | str  | No**     | None    | Folder location. Max 64 chars                       |
| `snippet` | str  | No**     | None    | Snippet location. Max 64 chars                      |
| `device`  | str  | No**     | None    | Device location. Max 64 chars                       |

\* Only required for update and response models
\** Exactly one container (folder/snippet/device) must be provided for create operations

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

The BGP Auth Profile service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

### Unified Client Interface (Recommended)

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Access the BGP Auth Profile service directly through the client
bgp_auth_profiles = client.bgp_auth_profile
```

### Traditional Service Instantiation (Legacy)

```python
from scm.client import Scm
from scm.config.network import BgpAuthProfile

# Initialize client
client = Scm(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Initialize BgpAuthProfile object explicitly
bgp_auth_profiles = BgpAuthProfile(client)
```

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

## Usage Examples

### Creating BGP Auth Profiles

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Create a BGP auth profile with MD5 secret
profile_data = {
   "name": "bgp-peer-auth",
   "secret": "my-md5-secret-key",
   "folder": "Texas"
}

new_profile = client.bgp_auth_profile.create(profile_data)
print(f"Created BGP auth profile with ID: {new_profile.id}")

# Create another profile for a different peer group
peer_group_profile = {
   "name": "upstream-peer-auth",
   "secret": "upstream-secret-2024",
   "folder": "Texas"
}

upstream_profile = client.bgp_auth_profile.create(peer_group_profile)
print(f"Created upstream auth profile with ID: {upstream_profile.id}")
```

### Retrieving BGP Auth Profiles

```python
# Fetch by name and folder
profile = client.bgp_auth_profile.fetch(
   name="bgp-peer-auth",
   folder="Texas"
)
print(f"Found profile: {profile.name}")

# Get by ID
profile_by_id = client.bgp_auth_profile.get(profile.id)
print(f"Retrieved profile: {profile_by_id.name}")
```

### Updating BGP Auth Profiles

```python
# Fetch existing profile
existing_profile = client.bgp_auth_profile.fetch(
   name="bgp-peer-auth",
   folder="Texas"
)

# Rotate the authentication secret
existing_profile.secret = "new-rotated-secret-key"

# Perform update
updated_profile = client.bgp_auth_profile.update(existing_profile)
```

### Listing BGP Auth Profiles

```python
# List all BGP auth profiles in a folder
profiles = client.bgp_auth_profile.list(
   folder="Texas"
)

# Process results
for profile in profiles:
   print(f"Name: {profile.name}")
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
exact_profiles = client.bgp_auth_profile.list(
   folder='Texas',
   exact_match=True
)

for profile in exact_profiles:
   print(f"Exact match: {profile.name} in {profile.folder}")

# Exclude all profiles from the 'All' folder
no_all_profiles = client.bgp_auth_profile.list(
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
client.bgp_auth_profile.max_limit = 4000

# List all profiles - auto-paginates through results
all_profiles = client.bgp_auth_profile.list(folder='Texas')
```

### Deleting BGP Auth Profiles

```python
# Delete by ID
profile_id = "123e4567-e89b-12d3-a456-426655440000"
client.bgp_auth_profile.delete(profile_id)
```

## Managing Configuration Changes

### Performing Commits

```python
# Prepare commit parameters
commit_params = {
   "folders": ["Texas"],
   "description": "Updated BGP auth profile configurations",
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
   # Create BGP auth profile
   profile_config = {
      "name": "test-auth-profile",
      "secret": "test-secret-key",
      "folder": "Texas"
   }

   new_profile = client.bgp_auth_profile.create(profile_config)

   # Commit changes
   result = client.commit(
      folders=["Texas"],
      description="Added BGP auth profile",
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
   - Use the unified client interface (`client.bgp_auth_profile`) for streamlined code
   - Create a single client instance and reuse it across your application
   - Perform commit operations directly on the client object (`client.commit()`)

2. **Authentication Configuration**
   - Use strong, randomly generated secrets for BGP MD5 authentication
   - Rotate authentication keys periodically according to your security policy
   - Ensure the same secret is configured on both sides of the BGP peering
   - Create separate auth profiles for different peer groups for key isolation

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
   - Cache frequently accessed profile configurations
   - Implement proper retry mechanisms

6. **Security**
   - Never log or expose authentication secrets in plain text
   - Store secrets securely and inject them at runtime
   - Use different auth profiles for different trust domains

## Related Models

- [BgpAuthProfileBaseModel](../../models/network/bgp_auth_profile_models.md#Overview)
- [BgpAuthProfileCreateModel](../../models/network/bgp_auth_profile_models.md#Overview)
- [BgpAuthProfileUpdateModel](../../models/network/bgp_auth_profile_models.md#Overview)
- [BgpAuthProfileResponseModel](../../models/network/bgp_auth_profile_models.md#Overview)
