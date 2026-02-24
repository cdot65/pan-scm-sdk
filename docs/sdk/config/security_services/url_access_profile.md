# URL Access Profile Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [URL Access Profile Model Attributes](#url-access-profile-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating URL Access Profiles](#creating-url-access-profiles)
    - [Retrieving Profiles](#retrieving-profiles)
    - [Updating Profiles](#updating-profiles)
    - [Listing Profiles](#listing-profiles)
    - [Filtering Responses](#filtering-responses)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Deleting Profiles](#deleting-profiles)
7. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Full Script Examples](#full-script-examples)
11. [Related Models](#related-models)

## Overview

The `URLAccessProfile` class provides functionality to manage URL access profiles in Palo Alto Networks' Strata
Cloud Manager. This class inherits from `BaseObject` and provides methods for creating, retrieving, updating, and
deleting profiles that define URL filtering policies to control access to websites based on URL categories via the
endpoint `/config/security/v1/url-access-profiles`.

## Core Methods

| Method     | Description                    | Parameters                                 | Return Type                           |
|------------|--------------------------------|--------------------------------------------|---------------------------------------|
| `create()` | Creates a new profile          | `data: Dict[str, Any]`                     | `URLAccessProfileResponseModel`       |
| `get()`    | Retrieves a profile by ID      | `object_id: str`                           | `URLAccessProfileResponseModel`       |
| `update()` | Updates an existing profile    | `profile: URLAccessProfileUpdateModel`     | `URLAccessProfileResponseModel`       |
| `delete()` | Deletes a profile              | `object_id: str`                           | `None`                                |
| `list()`   | Lists profiles with filtering  | `folder: str`, `**filters`                 | `List[URLAccessProfileResponseModel]` |
| `fetch()`  | Gets profile by name/container | `name: str`, `folder: str`                 | `URLAccessProfileResponseModel`       |

## URL Access Profile Model Attributes

| Attribute                | Type                     | Required | Default  | Description                                             |
|--------------------------|--------------------------|----------|----------|---------------------------------------------------------|
| `name`                   | str                      | Yes      | None     | Profile name                                            |
| `id`                     | UUID                     | Yes*     | None     | Unique identifier (*response/update only)               |
| `description`            | str                      | No       | None     | Profile description. Max 255 chars                      |
| `alert`                  | List[str]                | No       | None     | URL categories for alert action                         |
| `allow`                  | List[str]                | No       | None     | URL categories for allow action                         |
| `block`                  | List[str]                | No       | None     | URL categories for block action                         |
| `continue_`              | List[str]                | No       | None     | URL categories for continue action (alias: `continue`)  |
| `redirect`               | List[str]                | No       | None     | URL categories for redirect action                      |
| `cloud_inline_cat`       | bool                     | No       | None     | Enable cloud inline categorization                      |
| `local_inline_cat`       | bool                     | No       | None     | Enable local inline categorization                      |
| `credential_enforcement` | CredentialEnforcement    | No       | None     | Credential enforcement settings                         |
| `mlav_category_exception`| List[str]                | No       | None     | MLAV category exceptions                                |
| `log_container_page_only`| bool                     | No       | None     | Log container page only                                 |
| `log_http_hdr_referer`   | bool                     | No       | None     | Log HTTP header referer                                 |
| `log_http_hdr_user_agent`| bool                     | No       | None     | Log HTTP header user agent                              |
| `log_http_hdr_xff`       | bool                     | No       | None     | Log HTTP header X-Forwarded-For                         |
| `safe_search_enforcement`| bool                     | No       | None     | Enable safe search enforcement                          |
| `folder`                 | str                      | No**     | None     | Folder location. Max 64 chars                           |
| `snippet`                | str                      | No**     | None     | Snippet location. Max 64 chars                          |
| `device`                 | str                      | No**     | None     | Device location. Max 64 chars                           |

\* Only required for update and response models
\** Exactly one container (folder/snippet/device) must be provided for create operations

!!! note
    The `continue_` field uses a Python-safe name because `continue` is a reserved keyword. When passing data
    as a dictionary, you can use either `"continue_"` or `"continue"` (the field's alias) as the key.

## Exceptions

| Exception                    | HTTP Code | Description                     |
|------------------------------|-----------|---------------------------------|
| `InvalidObjectError`         | 400       | Invalid profile data or format  |
| `MissingQueryParameterError` | 400       | Missing required parameters     |
| `NameNotUniqueError`         | 409       | Profile name already exists     |
| `ObjectNotPresentError`      | 404       | Profile not found               |
| `ReferenceNotZeroError`      | 409       | Profile still referenced        |
| `AuthenticationError`        | 401       | Authentication failed           |
| `ServerError`                | 500       | Internal server error           |

## Basic Configuration

The URL Access Profile service can be accessed using the unified client interface (recommended):

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access URL access profiles directly through the client
profiles = client.url_access_profile
```

## Usage Examples

### Creating URL Access Profiles

```python
# Basic URL access profile with category actions
basic_profile = {
    "name": "basic-url-filtering",
    "description": "Basic URL filtering profile",
    "folder": "Texas",
    "alert": ["news", "entertainment"],
    "allow": ["business-and-economy", "technology"],
    "block": ["malware", "phishing", "command-and-control"]
}

# Create basic profile using the client
basic_profile_obj = client.url_access_profile.create(basic_profile)

# Profile with continue action (requires user confirmation)
continue_profile = {
    "name": "moderate-url-filtering",
    "description": "URL filtering with continue prompts",
    "folder": "Texas",
    "allow": ["business-and-economy"],
    "block": ["malware", "phishing"],
    "continue": ["streaming-media", "social-networking"],
    "alert": ["unknown"]
}

# Create profile with continue action
moderate_profile_obj = client.url_access_profile.create(continue_profile)

# Advanced profile with credential enforcement
advanced_profile = {
    "name": "advanced-url-filtering",
    "description": "Advanced URL filtering with credential enforcement",
    "folder": "Texas",
    "allow": ["business-and-economy", "technology"],
    "block": ["malware", "phishing", "command-and-control", "grayware"],
    "alert": ["unknown", "newly-registered-domain"],
    "cloud_inline_cat": True,
    "safe_search_enforcement": True,
    "log_http_hdr_xff": True,
    "log_http_hdr_user_agent": True,
    "log_http_hdr_referer": True,
    "credential_enforcement": {
        "mode": {
            "domain_credentials": {}
        },
        "block": ["malware", "phishing"],
        "alert": ["unknown"]
    }
}

# Create advanced profile
advanced_profile_obj = client.url_access_profile.create(advanced_profile)
```

### Retrieving Profiles

```python
# Fetch by name and folder
profile = client.url_access_profile.fetch(name="basic-url-filtering", folder="Texas")
print(f"Found profile: {profile.name}")

# Get by ID
profile_by_id = client.url_access_profile.get(profile.id)
print(f"Retrieved profile: {profile_by_id.name}")
print(f"Blocked categories: {profile_by_id.block}")
```

### Updating Profiles

```python
# Fetch existing profile
existing_profile = client.url_access_profile.fetch(name="basic-url-filtering", folder="Texas")

# Update attributes
existing_profile.description = "Updated URL filtering profile"
existing_profile.block = ["malware", "phishing", "command-and-control", "grayware"]
existing_profile.safe_search_enforcement = True

# Perform update
updated_profile = client.url_access_profile.update(existing_profile)
```

### Listing Profiles

```python
# List all URL access profiles in a folder
all_profiles = client.url_access_profile.list(
    folder='Texas'
)

# Process results
for profile in all_profiles:
    print(f"Name: {profile.name}")
    if profile.block:
        print(f"  Blocked categories: {len(profile.block)}")
    if profile.allow:
        print(f"  Allowed categories: {len(profile.allow)}")

# Define filter parameters as dictionary
list_params = {
    "folder": "Texas",
}

# List with filters as kwargs
filtered_profiles = client.url_access_profile.list(**list_params)
```

### Filtering Responses

The `list()` method supports additional parameters to refine your query results even further. You can leverage the
`exact_match`, `exclude_folders`, `exclude_snippets`, and `exclude_devices` parameters to control which objects are
included or excluded after the initial API response is fetched.

**Parameters:**

- `exact_match (bool)`: When `True`, only objects defined exactly in the specified container (`folder`, `snippet`, or `device`) are returned. Inherited or propagated objects are filtered out.
- `exclude_folders (List[str])`: Provide a list of folder names that you do not want included in the results.
- `exclude_snippets (List[str])`: Provide a list of snippet values to exclude from the results.
- `exclude_devices (List[str])`: Provide a list of device values to exclude from the results.

**Examples:**

```python
# Only return profiles defined exactly in 'Texas'
exact_profiles = client.url_access_profile.list(
   folder='Texas',
   exact_match=True
)

for profile in exact_profiles:
   print(f"Exact match: {profile.name} in {profile.folder}")

# Exclude all profiles from the 'All' folder
no_all_profiles = client.url_access_profile.list(
   folder='Texas',
   exclude_folders=['All']
)

for profile in no_all_profiles:
   assert profile.folder != 'All'
   print(f"Filtered out 'All': {profile.name}")

# Exclude profiles that come from 'default' snippet
no_default_snippet = client.url_access_profile.list(
   folder='Texas',
   exclude_snippets=['default']
)

for profile in no_default_snippet:
   assert profile.snippet != 'default'
   print(f"Filtered out 'default' snippet: {profile.name}")

# Exclude profiles associated with 'DeviceA'
no_deviceA = client.url_access_profile.list(
   folder='Texas',
   exclude_devices=['DeviceA']
)

for profile in no_deviceA:
   assert profile.device != 'DeviceA'
   print(f"Filtered out 'DeviceA': {profile.name}")

# Combine exact_match with multiple exclusions
combined_filters = client.url_access_profile.list(
   folder='Texas',
   exact_match=True,
   exclude_folders=['All'],
   exclude_snippets=['default'],
   exclude_devices=['DeviceA']
)

for profile in combined_filters:
   print(f"Combined filters result: {profile.name} in {profile.folder}")
```

### Controlling Pagination with max_limit

The SDK supports pagination through the `max_limit` parameter, which defines how many objects are retrieved per API call. By default, `max_limit` is set to 2500. The API itself imposes a maximum allowed value of 5000. If you set `max_limit` higher than 5000, it will be capped to the API's maximum. The `list()` method will continue to iterate through all objects until all results have been retrieved. Adjusting `max_limit` can help manage retrieval performance and memory usage when working with large datasets.

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Configure max_limit using the property setter
client.url_access_profile.max_limit = 4000

# List all profiles - auto-paginates through results
all_profiles = client.url_access_profile.list(folder='Texas')

# The profiles are fetched in chunks according to the max_limit setting.
```

### Deleting Profiles

```python
# Delete by ID
profile_id = "123e4567-e89b-12d3-a456-426655440000"
client.url_access_profile.delete(profile_id)
```

## Managing Configuration Changes

### Performing Commits

```python
# Prepare commit parameters
commit_params = {
    "folders": ["Texas"],
    "description": "Updated URL access profiles",
    "sync": True,
    "timeout": 300  # 5 minute timeout
}

# Commit the changes directly using the client
result = client.commit(**commit_params)

print(f"Commit job ID: {result.job_id}")
```

### Monitoring Jobs

```python
# Get status of specific job using the client
job_status = client.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

# List recent jobs using the client
recent_jobs = client.list_jobs(limit=10)
for job in recent_jobs.data:
    print(f"Job {job.id}: {job.type_str} - {job.status_str}")
```

## Error Handling

```python
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
    NameNotUniqueError,
    ObjectNotPresentError,
    ReferenceNotZeroError
)

try:
    # Create profile configuration
    profile_config = {
        "name": "test-url-filtering",
        "description": "Test URL filtering profile",
        "folder": "Texas",
        "block": ["malware", "phishing"],
        "alert": ["unknown"],
        "allow": ["business-and-economy"]
    }

    # Create the profile using the client
    new_profile = client.url_access_profile.create(profile_config)

    # Commit changes using the client
    result = client.commit(
        folders=["Texas"],
        description="Added URL access profile",
        sync=True
    )

    # Check job status using the client
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

1. **Category Configuration**
    - Block known malicious categories (malware, phishing, command-and-control)
    - Use alert for monitoring purposes on unknown or newly-registered domains
    - Apply continue action for categories requiring user acknowledgment
    - Document the rationale for category actions

2. **Credential Enforcement**
    - Enable credential enforcement to prevent credential theft via phishing
    - Configure appropriate mode (disabled, domain_credentials, ip_user, group_mapping)
    - Block credential submission on known malicious categories
    - Monitor alert categories for credential submission attempts

3. **Container Management**
    - Always specify exactly one container
    - Use consistent container names
    - Validate container existence
    - Group related profiles

4. **Client Usage**
    - Use the unified client interface (`client.url_access_profile`) for simpler code
    - Perform commits directly on the client (`client.commit()`)
    - Monitor jobs using client methods (`client.get_job_status()`, `client.list_jobs()`)
    - Initialize the client once and reuse across different object types

5. **Performance**
    - Use appropriate pagination
    - Cache frequently accessed profiles
    - Implement proper retry logic
    - Track job completion

6. **Logging and Monitoring**
    - Enable `log_http_hdr_xff` for X-Forwarded-For tracking
    - Enable `log_http_hdr_user_agent` to capture browser information
    - Enable `log_http_hdr_referer` to track referral sources
    - Use `log_container_page_only` to reduce log volume
    - Enable safe search enforcement for appropriate environments

## Full Script Examples

For examples related to URL access profiles, check the [examples directory](https://github.com/cdot65/pan-scm-sdk/tree/main/examples/scm/config/security_services/).

## Related Models

- [URLAccessProfileBaseModel](../../models/security_services/url_access_profile_models.md#Overview)
- [URLAccessProfileCreateModel](../../models/security_services/url_access_profile_models.md#Overview)
- [URLAccessProfileUpdateModel](../../models/security_services/url_access_profile_models.md#Overview)
- [URLAccessProfileResponseModel](../../models/security_services/url_access_profile_models.md#Overview)
- [CredentialEnforcement](../../models/security_services/url_access_profile_models.md#Overview)
- [CredentialEnforcementMode](../../models/security_services/url_access_profile_models.md#Overview)
