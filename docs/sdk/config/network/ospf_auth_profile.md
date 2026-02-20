# OSPF Auth Profile Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [OSPF Auth Profile Model Attributes](#ospf-auth-profile-model-attributes)
4. [MD5 Key Configuration](#md5-key-configuration)
5. [Exceptions](#exceptions)
6. [Basic Configuration](#basic-configuration)
7. [Usage Examples](#usage-examples)
    - [Creating OSPF Auth Profiles](#creating-ospf-auth-profiles)
    - [Retrieving OSPF Auth Profiles](#retrieving-ospf-auth-profiles)
    - [Updating OSPF Auth Profiles](#updating-ospf-auth-profiles)
    - [Listing OSPF Auth Profiles](#listing-ospf-auth-profiles)
    - [Filtering Responses](#filtering-responses)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Deleting OSPF Auth Profiles](#deleting-ospf-auth-profiles)
8. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
9. [Error Handling](#error-handling)
10. [Best Practices](#best-practices)
11. [Related Models](#related-models)

## Overview

The `OspfAuthProfile` class manages OSPF authentication profile objects in Palo Alto Networks' Strata Cloud Manager. It extends from `BaseObject` and offers methods to create, retrieve, update, list, fetch, and delete OSPF authentication profiles. These profiles support two mutually exclusive authentication types: simple password authentication or MD5 key-based authentication with multiple key entries.

## Core Methods

| Method     | Description                                                      | Parameters                                                                                                                       | Return Type                          |
|------------|------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|--------------------------------------|
| `create()` | Creates a new OSPF auth profile                                  | `data: Dict[str, Any]`                                                                                                           | `OspfAuthProfileResponseModel`       |
| `get()`    | Retrieves an OSPF auth profile by its unique ID                  | `object_id: str`                                                                                                                 | `OspfAuthProfileResponseModel`       |
| `update()` | Updates an existing OSPF auth profile                            | `profile: OspfAuthProfileUpdateModel`                                                                                            | `OspfAuthProfileResponseModel`       |
| `list()`   | Lists OSPF auth profiles with optional filtering                 | `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`, `exact_match: bool = False`, plus additional filters | `List[OspfAuthProfileResponseModel]` |
| `fetch()`  | Fetches a single OSPF auth profile by name within a container    | `name: str`, `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`                                          | `OspfAuthProfileResponseModel`       |
| `delete()` | Deletes an OSPF auth profile by its ID                           | `object_id: str`                                                                                                                 | `None`                               |

## OSPF Auth Profile Model Attributes

| Attribute  | Type                      | Required | Default | Description                                         |
|------------|---------------------------|----------|---------|-----------------------------------------------------|
| `name`     | str                       | Yes      | None    | Profile name                                        |
| `id`       | UUID                      | Yes*     | None    | Unique identifier (*response/update only)           |
| `password` | str                       | No       | None    | Simple password authentication (mutually exclusive with md5) |
| `md5`      | List[OspfAuthProfileMd5Key] | No     | None    | MD5 authentication keys (mutually exclusive with password) |
| `folder`   | str                       | No**     | None    | Folder location. Max 64 chars                       |
| `snippet`  | str                       | No**     | None    | Snippet location. Max 64 chars                      |
| `device`   | str                       | No**     | None    | Device location. Max 64 chars                       |

\* Only required for update and response models
\** Exactly one container (folder/snippet/device) must be provided for create operations

## MD5 Key Configuration

The `md5` attribute accepts a list of MD5 key entries for key-based authentication. Multiple keys can be configured for hitless key rotation.

### OspfAuthProfileMd5Key (input)

| Attribute   | Type | Required | Description                              |
|-------------|------|----------|------------------------------------------|
| `name`      | int  | No       | Key ID (1-255)                           |
| `key`       | str  | No       | MD5 hash value. Max 16 chars             |
| `preferred` | bool | No       | Whether this is the preferred key        |

### OspfAuthProfileMd5KeyResponse (response)

| Attribute   | Type | Required | Description                              |
|-------------|------|----------|------------------------------------------|
| `name`      | int  | No       | Key ID (1-255)                           |
| `key`       | str  | No       | MD5 hash (API returns encrypted value)   |
| `preferred` | bool | No       | Whether this is the preferred key        |

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

The OSPF Auth Profile service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

### Unified Client Interface (Recommended)

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Access the OSPF Auth Profile service directly through the client
ospf_auth_profiles = client.ospf_auth_profile
```

### Traditional Service Instantiation (Legacy)

```python
from scm.client import Scm
from scm.config.network import OspfAuthProfile

# Initialize client
client = Scm(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Initialize OspfAuthProfile object explicitly
ospf_auth_profiles = OspfAuthProfile(client)
```

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

## Usage Examples

### Creating OSPF Auth Profiles

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Create an OSPF auth profile with simple password
password_profile = {
   "name": "ospf-simple-auth",
   "password": "my-ospf-password",
   "folder": "Texas"
}

new_profile = client.ospf_auth_profile.create(password_profile)
print(f"Created OSPF auth profile with ID: {new_profile.id}")

# Create an OSPF auth profile with MD5 keys
md5_profile = {
   "name": "ospf-md5-auth",
   "md5": [
      {
         "name": 1,
         "key": "md5-key-primary",
         "preferred": True
      },
      {
         "name": 2,
         "key": "md5-key-backup",
         "preferred": False
      }
   ],
   "folder": "Texas"
}

md5_auth = client.ospf_auth_profile.create(md5_profile)
print(f"Created MD5 auth profile with ID: {md5_auth.id}")
```

### Retrieving OSPF Auth Profiles

```python
# Fetch by name and folder
profile = client.ospf_auth_profile.fetch(
   name="ospf-md5-auth",
   folder="Texas"
)
print(f"Found profile: {profile.name}")
if profile.md5:
   for key in profile.md5:
      print(f"  Key ID: {key.name}, Preferred: {key.preferred}")

# Get by ID
profile_by_id = client.ospf_auth_profile.get(profile.id)
print(f"Retrieved profile: {profile_by_id.name}")
```

### Updating OSPF Auth Profiles

```python
# Fetch existing profile
existing_profile = client.ospf_auth_profile.fetch(
   name="ospf-simple-auth",
   folder="Texas"
)

# Change from password to MD5 authentication
existing_profile.password = None
existing_profile.md5 = [
   {
      "name": 1,
      "key": "new-md5-key",
      "preferred": True
   }
]

# Perform update
updated_profile = client.ospf_auth_profile.update(existing_profile)
```

### Listing OSPF Auth Profiles

```python
# List all OSPF auth profiles in a folder
profiles = client.ospf_auth_profile.list(
   folder="Texas"
)

# Process results
for profile in profiles:
   print(f"Name: {profile.name}")
   if profile.password:
      print(f"  Auth type: Simple password")
   elif profile.md5:
      print(f"  Auth type: MD5 ({len(profile.md5)} keys)")
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
exact_profiles = client.ospf_auth_profile.list(
   folder='Texas',
   exact_match=True
)

for profile in exact_profiles:
   print(f"Exact match: {profile.name} in {profile.folder}")

# Exclude all profiles from the 'All' folder
no_all_profiles = client.ospf_auth_profile.list(
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
client.ospf_auth_profile.max_limit = 4000

# List all profiles - auto-paginates through results
all_profiles = client.ospf_auth_profile.list(folder='Texas')
```

### Deleting OSPF Auth Profiles

```python
# Delete by ID
profile_id = "123e4567-e89b-12d3-a456-426655440000"
client.ospf_auth_profile.delete(profile_id)
```

## Managing Configuration Changes

### Performing Commits

```python
# Prepare commit parameters
commit_params = {
   "folders": ["Texas"],
   "description": "Updated OSPF auth profile configurations",
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
   # Create OSPF auth profile
   profile_config = {
      "name": "test-ospf-auth",
      "md5": [
         {
            "name": 1,
            "key": "test-key",
            "preferred": True
         }
      ],
      "folder": "Texas"
   }

   new_profile = client.ospf_auth_profile.create(profile_config)

   # Commit changes
   result = client.commit(
      folders=["Texas"],
      description="Added OSPF auth profile",
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
   - Use the unified client interface (`client.ospf_auth_profile`) for streamlined code
   - Create a single client instance and reuse it across your application
   - Perform commit operations directly on the client object (`client.commit()`)

2. **Authentication Configuration**
   - Prefer MD5 authentication over simple password for stronger security
   - Configure multiple MD5 keys to enable hitless key rotation
   - Mark only one key as `preferred` at a time
   - Remember that `password` and `md5` are mutually exclusive

3. **Key Management**
   - Plan key rotations by adding a new key before removing the old one
   - Use key IDs (1-255) consistently across OSPF neighbors
   - Keep MD5 key strings to 16 characters or fewer
   - Ensure matching key IDs and secrets on both sides of an OSPF adjacency

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

- [OspfAuthProfileBaseModel](../../models/network/ospf_auth_profile_models.md#Overview)
- [OspfAuthProfileCreateModel](../../models/network/ospf_auth_profile_models.md#Overview)
- [OspfAuthProfileUpdateModel](../../models/network/ospf_auth_profile_models.md#Overview)
- [OspfAuthProfileResponseModel](../../models/network/ospf_auth_profile_models.md#Overview)
- [OspfAuthProfileMd5Key](../../models/network/ospf_auth_profile_models.md#Overview)
- [OspfAuthProfileMd5KeyResponse](../../models/network/ospf_auth_profile_models.md#Overview)
