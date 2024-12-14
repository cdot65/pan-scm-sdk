# WildFire Antivirus Profile Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Profile Model Attributes](#profile-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating WildFire Profiles](#creating-wildfire-profiles)
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

The `WildfireAntivirusProfile` class provides functionality to manage WildFire antivirus profiles in Palo Alto Networks'
Strata Cloud Manager. This class inherits from `BaseObject` and provides methods for creating, retrieving, updating, and
deleting profiles that define malware analysis settings, file inspection rules, and threat detection configurations.

## Core Methods

| Method     | Description                    | Parameters                              | Return Type                            |
|------------|--------------------------------|-----------------------------------------|----------------------------------------|
| `create()` | Creates a new profile          | `data: Dict[str, Any]`                  | `WildfireAvProfileResponseModel`       |
| `get()`    | Retrieves a profile by ID      | `object_id: str`                        | `WildfireAvProfileResponseModel`       |
| `update()` | Updates an existing profile    | `profile: WildfireAvProfileUpdateModel` | `WildfireAvProfileResponseModel`       |
| `delete()` | Deletes a profile              | `object_id: str`                        | `None`                                 |
| `list()`   | Lists profiles with filtering  | `folder: str`, `**filters`              | `List[WildfireAvProfileResponseModel]` |
| `fetch()`  | Gets profile by name/container | `name: str`, `folder: str`              | `WildfireAvProfileResponseModel`       |

## Profile Model Attributes

| Attribute          | Type                  | Required | Description                                 |
|--------------------|-----------------------|----------|---------------------------------------------|
| `name`             | str                   | Yes      | Profile name (max 63 chars)                 |
| `id`               | UUID                  | Yes*     | Unique identifier (*response only)          |
| `description`      | str                   | No       | Profile description                         |
| `packet_capture`   | bool                  | No       | Enable packet capture                       |
| `rules`            | List[Rule]            | Yes      | List of analysis rules                      |
| `mlav_exception`   | List[MlavException]   | No       | MLAV exception entries                      |
| `threat_exception` | List[ThreatException] | No       | Threat exception entries                    |
| `folder`           | str                   | Yes**    | Folder location (**one container required)  |
| `snippet`          | str                   | Yes**    | Snippet location (**one container required) |
| `device`           | str                   | Yes**    | Device location (**one container required)  |

### Rule Attributes

| Attribute     | Type      | Required | Description                          |
|---------------|-----------|----------|--------------------------------------|
| `name`        | str       | Yes      | Rule name                            |
| `analysis`    | Analysis  | No       | Analysis type (public/private cloud) |
| `direction`   | Direction | Yes      | Traffic direction (up/down/both)     |
| `application` | List[str] | No       | List of applications (default: any)  |
| `file_type`   | List[str] | No       | List of file types (default: any)    |

## Exceptions

| Exception                    | HTTP Code | Description                    |
|------------------------------|-----------|--------------------------------|
| `InvalidObjectError`         | 400       | Invalid profile data or format |
| `MissingQueryParameterError` | 400       | Missing required parameters    |
| `NameNotUniqueError`         | 409       | Profile name already exists    |
| `ObjectNotPresentError`      | 404       | Profile not found              |
| `ReferenceNotZeroError`      | 409       | Profile still referenced       |
| `AuthenticationError`        | 401       | Authentication failed          |
| `ServerError`                | 500       | Internal server error          |

## Basic Configuration

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.security import WildfireAntivirusProfile

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize WildFire Profile object
wildfire_profiles = WildfireAntivirusProfile(client)
```

</div>

## Usage Examples

### Creating WildFire Profiles

<div class="termy">

<!-- termynal -->

```python
# Basic profile configuration
basic_profile = {
    "name": "basic-profile",
    "description": "Basic WildFire profile",
    "folder": "Texas",
    "rules": [
        {
            "name": "basic-rule",
            "direction": "both",
            "analysis": "public-cloud",
            "application": ["web-browsing"],
            "file_type": ["pdf", "pe"]
        }
    ]
}

# Create basic profile
basic_profile_obj = wildfire_profiles.create(basic_profile)

# Advanced profile with exceptions
advanced_profile = {
    "name": "advanced-profile",
    "description": "Advanced WildFire profile",
    "folder": "Texas",
    "packet_capture": True,
    "rules": [
        {
            "name": "upload-rule",
            "direction": "upload",
            "analysis": "private-cloud",
            "application": ["ftp", "sftp"],
            "file_type": ["any"]
        },
        {
            "name": "download-rule",
            "direction": "download",
            "analysis": "public-cloud",
            "application": ["web-browsing"],
            "file_type": ["pdf", "doc"]
        }
    ],
    "mlav_exception": [
        {
            "name": "exception1",
            "filename": "trusted.exe",
            "description": "Trusted application"
        }
    ]
}

# Create advanced profile
advanced_profile_obj = wildfire_profiles.create(advanced_profile)
```

</div>

### Retrieving Profiles

<div class="termy">

<!-- termynal -->

```python
# Fetch by name and folder
profile = wildfire_profiles.fetch(name="basic-profile", folder="Texas")
print(f"Found profile: {profile.name}")

# Get by ID
profile_by_id = wildfire_profiles.get(profile.id)
print(f"Retrieved profile: {profile_by_id.name}")
print(f"Number of rules: {len(profile_by_id.rules)}")
```

</div>

### Updating Profiles

<div class="termy">

<!-- termynal -->

```python
# Fetch existing profile
existing_profile = wildfire_profiles.fetch(name="basic-profile", folder="Texas")

# Update attributes
existing_profile.description = "Updated profile description"
existing_profile.packet_capture = True

# Add new rule
new_rule = {
    "name": "new-rule",
    "direction": "both",
    "analysis": "public-cloud",
    "application": ["any"],
    "file_type": ["any"]
}
existing_profile.rules.append(new_rule)

# Perform update
updated_profile = wildfire_profiles.update(existing_profile)
```

</div>

### Listing Profiles

<div class="termy">

<!-- termynal -->

```python
# List with direct filter parameters
filtered_profiles = wildfire_profiles.list(
    folder='Texas',
    rules=['basic-rule', 'upload-rule']
)

# Process results
for profile in filtered_profiles:
    print(f"Name: {profile.name}")
    for rule in profile.rules:
        print(f"  Rule: {rule.name}")
        print(f"  Direction: {rule.direction}")
        print(f"  Analysis: {rule.analysis}")

# Define filter parameters as dictionary
list_params = {
    "folder": "Texas",
    "rules": ["download-rule"]
}

# List with filters as kwargs
filtered_profiles = wildfire_profiles.list(**list_params)
```

</div>

### Filtering Responses

The `list()` method supports additional parameters to refine your query results even further. Alongside basic filters
(like `types`, `values`, and `tags`), you can leverage the `exact_match`, `exclude_folders`, `exclude_snippets`, and
`exclude_devices` parameters to control which objects are included or excluded after the initial API response is fetched.

**Parameters:**

- `exact_match (bool)`: When `True`, only objects defined exactly in the specified container (`folder`, `snippet`, or `device`) are returned.
- `exclude_folders (List[str])`: Provide a list of folder names to exclude.
- `exclude_snippets (List[str])`: Provide a list of snippet values to exclude.
- `exclude_devices (List[str])`: Provide a list of device values to exclude.

**Examples:**

<div class="termy">

<!-- termynal -->

```python
# Only return wildfire_antivirus defined exactly in 'Texas'
exact_wildfire_antivirus = wildfire_profiles.list(
    folder='Texas',
    exact_match=True
)

for app in exact_wildfire_antivirus:
    print(f"Exact match: {app.name} in {app.folder}")

# Exclude all wildfire_antivirus from the 'All' folder
no_all_wildfire_antivirus = wildfire_profiles.list(
    folder='Texas',
    exclude_folders=['All']
)

for app in no_all_wildfire_antivirus:
    assert app.folder != 'All'
    print(f"Filtered out 'All': {app.name}")

# Exclude wildfire_antivirus that come from 'default' snippet
no_default_snippet = wildfire_profiles.list(
    folder='Texas',
    exclude_snippets=['default']
)

for app in no_default_snippet:
    assert app.snippet != 'default'
    print(f"Filtered out 'default' snippet: {app.name}")

# Exclude wildfire_antivirus associated with 'DeviceA'
no_deviceA = wildfire_profiles.list(
    folder='Texas',
    exclude_devices=['DeviceA']
)

for app in no_deviceA:
    assert app.device != 'DeviceA'
    print(f"Filtered out 'DeviceA': {app.name}")

# Combine exact_match with multiple exclusions
combined_filters = wildfire_profiles.list(
    folder='Texas',
    exact_match=True,
    exclude_folders=['All'],
    exclude_snippets=['default'],
    exclude_devices=['DeviceA']
)

for app in combined_filters:
    print(f"Combined filters result: {app.name} in {app.folder}")
```

</div>

### Controlling Pagination with max_limit

The SDK supports pagination through the `max_limit` parameter, which defines how many objects are retrieved per API call. By default, `max_limit` is set to 2500. The API itself imposes a maximum allowed value of 5000. If you set `max_limit` higher than 5000, it will be capped to the API's maximum. The `list()` method will continue to iterate through all objects until all results have been retrieved. Adjusting `max_limit` can help manage retrieval performance and memory usage when working with large datasets.

<div class="termy">

<!-- termynal -->

```python
# Initialize the WildfireAntivirusProfile object with a custom max_limit
# This will retrieve up to 4321 objects per API call, up to the API limit of 5000.
profile_client = WildfireAntivirusProfile(api_client=client, max_limit=4321)

# Now when we call list(), it will use the specified max_limit for each request
# while auto-paginating through all available objects.
all_profiles = profile_client.list(folder='Texas')

# 'all_profiles' contains all objects from 'Texas', fetched in chunks of up to 4321 at a time.
```

</div>

### Deleting Profiles

<div class="termy">

<!-- termynal -->

```python
# Delete by ID
profile_id = "123e4567-e89b-12d3-a456-426655440000"
wildfire_profiles.delete(profile_id)
```

</div>

## Managing Configuration Changes

### Performing Commits

<div class="termy">

<!-- termynal -->

```python
# Prepare commit parameters
commit_params = {
    "folders": ["Texas"],
    "description": "Updated WildFire profiles",
    "sync": True,
    "timeout": 300  # 5 minute timeout
}

# Commit the changes
result = wildfire_profiles.commit(**commit_params)

print(f"Commit job ID: {result.job_id}")
```

</div>

### Monitoring Jobs

<div class="termy">

<!-- termynal -->

```python
# Get status of specific job
job_status = wildfire_profiles.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

# List recent jobs
recent_jobs = wildfire_profiles.list_jobs(limit=10)
for job in recent_jobs.data:
    print(f"Job {job.id}: {job.type_str} - {job.status_str}")
```

</div>

## Error Handling

<div class="termy">

<!-- termynal -->

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
        "name": "test-profile",
        "folder": "Texas",
        "description": "Test WildFire profile",
        "rules": [
            {
                "name": "test-rule",
                "direction": "both",
                "analysis": "public-cloud",
                "application": ["web-browsing"],
                "file_type": ["pdf", "pe"]
            }
        ]
    }

    # Create the profile
    new_profile = wildfire_profiles.create(profile_config)

    # Commit changes
    result = wildfire_profiles.commit(
        folders=["Texas"],
        description="Added test profile",
        sync=True
    )

    # Check job status
    status = wildfire_profiles.get_job_status(result.job_id)

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

</div>

## Best Practices

1. **Rule Configuration**
    - Use descriptive rule names
    - Start with least privileged access
    - Consider performance impact
    - Document exceptions thoroughly
    - Review file type coverage

2. **Container Management**
    - Always specify exactly one container (folder, snippet, or device)
    - Use consistent container names
    - Validate container existence
    - Group related profiles

3. **Exception Handling**
    - Document all exceptions
    - Review MLAV exceptions regularly
    - Monitor threat exceptions
    - Update exception documentation
    - Implement proper logging

4. **Performance**
    - Minimize rule complexity
    - Use appropriate file types
    - Monitor packet capture impact
    - Implement caching
    - Consider analysis location

5. **Security**
    - Follow least privilege
    - Document all changes
    - Review profile access
    - Monitor analysis results
    - Regular security reviews

## Full Script Examples

Refer to
the [wildfire_antivirus_profile.py example](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/security/wildfire_antivirus_profile.py).

## Related Models

- [WildfireAvProfileCreateModel](../../models/security_services/wildfire_antivirus_profile_models.md#Overview)
- [WildfireAvProfileUpdateModel](../../models/security_services/wildfire_antivirus_profile_models.md#Overview)
- [WildfireAvProfileResponseModel](../../models/security_services/wildfire_antivirus_profile_models.md#Overview)
