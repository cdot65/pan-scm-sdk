# File Blocking Profile Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [File Blocking Profile Model Attributes](#file-blocking-profile-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating File Blocking Profiles](#creating-file-blocking-profiles)
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

The `FileBlockingProfile` class provides functionality to manage file blocking profiles in Palo Alto Networks' Strata
Cloud Manager. This class inherits from `BaseObject` and provides methods for creating, retrieving, updating, and
deleting profiles that define file blocking policies for controlling file transfers based on application, direction,
and file type via the endpoint `/config/security/v1/file-blocking-profiles`.

## Core Methods

| Method     | Description                    | Parameters                                    | Return Type                              |
|------------|--------------------------------|-----------------------------------------------|------------------------------------------|
| `create()` | Creates a new profile          | `data: Dict[str, Any]`                        | `FileBlockingProfileResponseModel`       |
| `get()`    | Retrieves a profile by ID      | `object_id: str`                              | `FileBlockingProfileResponseModel`       |
| `update()` | Updates an existing profile    | `profile: FileBlockingProfileUpdateModel`     | `FileBlockingProfileResponseModel`       |
| `delete()` | Deletes a profile              | `object_id: str`                              | `None`                                   |
| `list()`   | Lists profiles with filtering  | `folder: str`, `**filters`                    | `List[FileBlockingProfileResponseModel]` |
| `fetch()`  | Gets profile by name/container | `name: str`, `folder: str`                    | `FileBlockingProfileResponseModel`       |

## File Blocking Profile Model Attributes

| Attribute     | Type                       | Required | Default | Description                                             |
|---------------|----------------------------|----------|---------|---------------------------------------------------------|
| `name`        | str                        | Yes      | None    | Profile name                                            |
| `id`          | UUID                       | Yes*     | None    | Unique identifier (*response/update only)               |
| `description` | str                        | No       | None    | Profile description                                     |
| `rules`       | List[FileBlockingRule]     | No       | None    | List of file blocking rules                             |
| `folder`      | str                        | No**     | None    | Folder location. Max 64 chars                           |
| `snippet`     | str                        | No**     | None    | Snippet location. Max 64 chars                          |
| `device`      | str                        | No**     | None    | Device location. Max 64 chars                           |

\* Only required for update and response models
\** Exactly one container (folder/snippet/device) must be provided for create operations

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

The File Blocking Profile service can be accessed using the unified client interface (recommended):

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access file blocking profiles directly through the client
profiles = client.file_blocking_profile
```

## Usage Examples

### Creating File Blocking Profiles

```python
# Basic profile with an alert rule
basic_profile = {
    "name": "basic-file-blocking",
    "description": "Basic file blocking profile",
    "folder": "Texas",
    "rules": [
        {
            "name": "alert-executables",
            "action": "alert",
            "application": ["any"],
            "direction": "both",
            "file_type": ["exe", "dll"]
        }
    ]
}

# Create basic profile using the client
basic_profile_obj = client.file_blocking_profile.create(basic_profile)

# Profile with blocking rule
block_profile = {
    "name": "strict-file-blocking",
    "description": "Strict file blocking profile",
    "folder": "Texas",
    "rules": [
        {
            "name": "block-dangerous",
            "action": "block",
            "application": ["web-browsing", "ftp"],
            "direction": "download",
            "file_type": ["exe", "bat", "cmd", "msi"]
        },
        {
            "name": "alert-documents",
            "action": "alert",
            "application": ["any"],
            "direction": "upload",
            "file_type": ["doc", "pdf", "xls"]
        }
    ]
}

# Create strict profile
strict_profile_obj = client.file_blocking_profile.create(block_profile)

# Profile with continue action
continue_profile = {
    "name": "continue-file-blocking",
    "description": "File blocking profile with continue action",
    "folder": "Texas",
    "rules": [
        {
            "name": "continue-archives",
            "action": "continue",
            "application": ["any"],
            "direction": "download",
            "file_type": ["tar", "gz", "zip"]
        }
    ]
}

# Create continue profile
continue_profile_obj = client.file_blocking_profile.create(continue_profile)
```

### Retrieving Profiles

```python
# Fetch by name and folder
profile = client.file_blocking_profile.fetch(name="basic-file-blocking", folder="Texas")
print(f"Found profile: {profile.name}")

# Get by ID
profile_by_id = client.file_blocking_profile.get(profile.id)
print(f"Retrieved profile: {profile_by_id.name}")
print(f"Number of rules: {len(profile_by_id.rules)}")
```

### Updating Profiles

```python
# Fetch existing profile
existing_profile = client.file_blocking_profile.fetch(name="basic-file-blocking", folder="Texas")

# Update attributes
existing_profile.description = "Updated file blocking profile"

# Add new rule
existing_profile.rules.append({
    "name": "block-scripts",
    "action": "block",
    "application": ["any"],
    "direction": "both",
    "file_type": ["js", "vbs", "ps1"]
})

# Perform update
updated_profile = client.file_blocking_profile.update(existing_profile)
```

### Listing Profiles

```python
# List with direct filter parameters
filtered_profiles = client.file_blocking_profile.list(
    folder='Texas',
    rules=['block-dangerous']
)

# Process results
for profile in filtered_profiles:
    print(f"Name: {profile.name}")
    if profile.rules:
        print(f"Rules: {len(profile.rules)}")
        for rule in profile.rules:
            print(f"  - {rule.name}: {rule.action} ({rule.direction})")

# Define filter parameters as dictionary
list_params = {
    "folder": "Texas",
    "rules": ["alert-executables", "block-scripts"]
}

# List with filters as kwargs
filtered_profiles = client.file_blocking_profile.list(**list_params)
```

### Filtering Responses

The `list()` method supports additional parameters to refine your query results even further. Alongside basic filters
(like `rules`), you can leverage the `exact_match`, `exclude_folders`, `exclude_snippets`, and
`exclude_devices` parameters to control which objects are included or excluded after the initial API response is fetched.

**Parameters:**

- `exact_match (bool)`: When `True`, only objects defined exactly in the specified container (`folder`, `snippet`, or `device`) are returned. Inherited or propagated objects are filtered out.
- `exclude_folders (List[str])`: Provide a list of folder names that you do not want included in the results.
- `exclude_snippets (List[str])`: Provide a list of snippet values to exclude from the results.
- `exclude_devices (List[str])`: Provide a list of device values to exclude from the results.

**Examples:**

```python
# Only return profiles defined exactly in 'Texas'
exact_profiles = client.file_blocking_profile.list(
   folder='Texas',
   exact_match=True
)

for profile in exact_profiles:
   print(f"Exact match: {profile.name} in {profile.folder}")

# Exclude all profiles from the 'All' folder
no_all_profiles = client.file_blocking_profile.list(
   folder='Texas',
   exclude_folders=['All']
)

for profile in no_all_profiles:
   assert profile.folder != 'All'
   print(f"Filtered out 'All': {profile.name}")

# Exclude profiles that come from 'default' snippet
no_default_snippet = client.file_blocking_profile.list(
   folder='Texas',
   exclude_snippets=['default']
)

for profile in no_default_snippet:
   assert profile.snippet != 'default'
   print(f"Filtered out 'default' snippet: {profile.name}")

# Exclude profiles associated with 'DeviceA'
no_deviceA = client.file_blocking_profile.list(
   folder='Texas',
   exclude_devices=['DeviceA']
)

for profile in no_deviceA:
   assert profile.device != 'DeviceA'
   print(f"Filtered out 'DeviceA': {profile.name}")

# Combine exact_match with multiple exclusions
combined_filters = client.file_blocking_profile.list(
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
client.file_blocking_profile.max_limit = 4000

# List all profiles - auto-paginates through results
all_profiles = client.file_blocking_profile.list(folder='Texas')

# The profiles are fetched in chunks according to the max_limit setting.
```

### Deleting Profiles

```python
# Delete by ID
profile_id = "123e4567-e89b-12d3-a456-426655440000"
client.file_blocking_profile.delete(profile_id)
```

## Managing Configuration Changes

### Performing Commits

```python
# Prepare commit parameters
commit_params = {
    "folders": ["Texas"],
    "description": "Updated file blocking profiles",
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
        "name": "test-file-blocking",
        "description": "Test file blocking profile",
        "folder": "Texas",
        "rules": [
            {
                "name": "block-exe",
                "action": "block",
                "application": ["any"],
                "direction": "both",
                "file_type": ["exe"]
            }
        ]
    }

    # Create the profile using the client
    new_profile = client.file_blocking_profile.create(profile_config)

    # Commit changes using the client
    result = client.commit(
        folders=["Texas"],
        description="Added file blocking profile",
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

1. **Rule Configuration**
    - Use descriptive rule names that indicate the purpose
    - Set appropriate actions (alert, block, continue) based on risk level
    - Be specific with file types rather than using broad wildcards
    - Document rule purposes with profile descriptions
    - Review rule effectiveness periodically

2. **Container Management**
    - Always specify exactly one container
    - Use consistent container names
    - Validate container existence
    - Group related profiles

3. **Client Usage**
    - Use the unified client interface (`client.file_blocking_profile`) for simpler code
    - Perform commits directly on the client (`client.commit()`)
    - Monitor jobs using client methods (`client.get_job_status()`, `client.list_jobs()`)
    - Initialize the client once and reuse across different object types

4. **Performance**
    - Use appropriate pagination
    - Cache frequently accessed profiles
    - Implement proper retry logic
    - Track job completion

5. **Security**
    - Block dangerous file types (executables, scripts) by default
    - Use continue action for files that require user confirmation
    - Monitor alert actions to identify potential threats
    - Review and update file type lists regularly
    - Document modifications

## Full Script Examples

For examples related to file blocking profiles, check the [examples directory](https://github.com/cdot65/pan-scm-sdk/tree/main/examples/scm/config/security_services/).

## Related Models

- [FileBlockingProfileBaseModel](../../models/security_services/file_blocking_profile_models.md#Overview)
- [FileBlockingProfileCreateModel](../../models/security_services/file_blocking_profile_models.md#Overview)
- [FileBlockingProfileUpdateModel](../../models/security_services/file_blocking_profile_models.md#Overview)
- [FileBlockingProfileResponseModel](../../models/security_services/file_blocking_profile_models.md#Overview)
- [FileBlockingRule](../../models/security_services/file_blocking_profile_models.md#Overview)
- [FileBlockingAction](../../models/security_services/file_blocking_profile_models.md#Overview)
- [FileBlockingDirection](../../models/security_services/file_blocking_profile_models.md#Overview)
