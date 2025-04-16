# Anti-Spyware Profile Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Anti-Spyware Profile Model Attributes](#anti-spyware-profile-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating Anti-Spyware Profiles](#creating-anti-spyware-profiles)
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

The `AntiSpywareProfile` class provides functionality to manage anti-spyware profiles in Palo Alto Networks' Strata
Cloud Manager. This class inherits from `BaseObject` and provides methods for creating, retrieving, updating, and
deleting profiles that define threat detection and prevention settings for spyware, command-and-control traffic, and
other malicious activities.

## Core Methods

| Method     | Description                    | Parameters                               | Return Type                             |
|------------|--------------------------------|------------------------------------------|-----------------------------------------|
| `create()` | Creates a new profile          | `data: Dict[str, Any]`                   | `AntiSpywareProfileResponseModel`       |
| `get()`    | Retrieves a profile by ID      | `object_id: str`                         | `AntiSpywareProfileResponseModel`       |
| `update()` | Updates an existing profile    | `profile: AntiSpywareProfileUpdateModel` | `AntiSpywareProfileResponseModel`       |
| `delete()` | Deletes a profile              | `object_id: str`                         | `None`                                  |
| `list()`   | Lists profiles with filtering  | `folder: str`, `**filters`               | `List[AntiSpywareProfileResponseModel]` |
| `fetch()`  | Gets profile by name/container | `name: str`, `folder: str`               | `AntiSpywareProfileResponseModel`       |

## Anti-Spyware Profile Model Attributes

| Attribute                     | Type                  | Required | Description                                 |
|-------------------------------|-----------------------|----------|---------------------------------------------|
| `name`                        | str                   | Yes      | Profile name (max 63 chars)                 |
| `id`                          | UUID                  | Yes*     | Unique identifier (*response only)          |
| `description`                 | str                   | No       | Profile description                         |
| `cloud_inline_analysis`       | bool                  | No       | Enable cloud inline analysis                |
| `rules`                       | List[Rule]            | Yes      | List of anti-spyware rules                  |
| `threat_exception`            | List[ThreatException] | No       | List of threat exceptions                   |
| `mica_engine_spyware_enabled` | List[MicaEngine]      | No       | MICA engine spyware settings                |
| `inline_exception_edl_url`    | List[str]             | No       | Inline exception EDL URLs                   |
| `folder`                      | str                   | Yes**    | Folder location (**one container required)  |
| `snippet`                     | str                   | Yes**    | Snippet location (**one container required) |
| `device`                      | str                   | Yes**    | Device location (**one container required)  |

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

```python
from scm.client import Scm

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access anti-spyware profiles directly through the client
# No need to initialize a separate AntiSpywareProfile object
```

## Usage Examples

### Creating Anti-Spyware Profiles

```python
# Basic profile configuration
basic_profile = {
    "name": "basic-profile",
    "description": "Basic anti-spyware profile",
    "folder": "Texas",
    "rules": [
        {
            "name": "block-critical",
            "severity": ["critical"],
            "category": "spyware",
            "action": {
                "block_ip": {
                    "track_by": "source",
                    "duration": 300
                }
            }
        }
    ]
}

# Create basic profile using the client
basic_profile_obj = client.anti_spyware_profile.create(basic_profile)

# Advanced profile with MICA engine
advanced_profile = {
    "name": "advanced-profile",
    "description": "Advanced anti-spyware profile",
    "folder": "Texas",
    "cloud_inline_analysis": True,
    "mica_engine_spyware_enabled": [
        {
            "name": "HTTP Command and Control detector",
            "inline_policy_action": "alert"
        }
    ],
    "rules": [
        {
            "name": "critical-threats",
            "severity": ["critical", "high"],
            "category": "command-and-control",
            "action": {"reset_both": {}}
        },
        {
            "name": "medium-threats",
            "severity": ["medium"],
            "category": "spyware",
            "action": {"alert": {}}
        }
    ]
}

# Create advanced profile
advanced_profile_obj = client.anti_spyware_profile.create(advanced_profile)
```

### Retrieving Profiles

```python
# Fetch by name and folder
profile = client.anti_spyware_profile.fetch(name="basic-profile", folder="Texas")
print(f"Found profile: {profile.name}")

# Get by ID
profile_by_id = client.anti_spyware_profile.get(profile.id)
print(f"Retrieved profile: {profile_by_id.name}")
print(f"Number of rules: {len(profile_by_id.rules)}")
```

### Updating Profiles

```python
# Fetch existing profile
existing_profile = client.anti_spyware_profile.fetch(name="basic-profile", folder="Texas")

# Update attributes
existing_profile.description = "Updated basic profile"
existing_profile.cloud_inline_analysis = True

# Add new rule
existing_profile.rules.append({
    "name": "new-rule",
    "severity": ["high"],
    "category": "spyware",
    "action": {"alert": {}}
})

# Perform update
updated_profile = client.anti_spyware_profile.update(existing_profile)
```

### Listing Profiles

```python
# List with direct filter parameters
filtered_profiles = client.anti_spyware_profile.list(
    folder='Texas',
    rules=['block-critical']
)

# Process results
for profile in filtered_profiles:
    print(f"Name: {profile.name}")
    print(f"Rules: {len(profile.rules)}")
    for rule in profile.rules:
        print(f"  - {rule.name}: {rule.category}")

# Define filter parameters as dictionary
list_params = {
    "folder": "Texas",
    "rules": ["critical-threats", "medium-threats"]
}

# List with filters as kwargs
filtered_profiles = client.anti_spyware_profile.list(**list_params)
```

### Filtering Responses

The `list()` method supports additional parameters to refine your query results even further. Alongside basic filters
(like `types`, `values`, and `tags`), you can leverage the `exact_match`, `exclude_folders`, `exclude_snippets`, and
`exclude_devices` parameters to control which objects are included or excluded after the initial API response is fetched.

**Parameters:**

- `exact_match (bool)`: When `True`, only objects defined exactly in the specified container (`folder`, `snippet`, or `device`) are returned. Inherited or propagated objects are filtered out.
- `exclude_folders (List[str])`: Provide a list of folder names that you do not want included in the results.
- `exclude_snippets (List[str])`: Provide a list of snippet values to exclude from the results.
- `exclude_devices (List[str])`: Provide a list of device values to exclude from the results.

**Examples:**

```python
# Only return anti_spyware_profiles defined exactly in 'Texas'
exact_anti_spyware_profiles = profiles.list(
   folder='Texas',
   exact_match=True
)

for app in exact_anti_spyware_profiles:
   print(f"Exact match: {app.name} in {app.folder}")

# Exclude all anti_spyware_profiles from the 'All' folder
no_all_anti_spyware_profiles = profiles.list(
   folder='Texas',
   exclude_folders=['All']
)

for app in no_all_anti_spyware_profiles:
   assert app.folder != 'All'
   print(f"Filtered out 'All': {app.name}")

# Exclude anti_spyware_profiles that come from 'default' snippet
no_default_snippet = profiles.list(
   folder='Texas',
   exclude_snippets=['default']
)

for app in no_default_snippet:
   assert app.snippet != 'default'
   print(f"Filtered out 'default' snippet: {app.name}")

# Exclude anti_spyware_profiles associated with 'DeviceA'
no_deviceA = profiles.list(
   folder='Texas',
   exclude_devices=['DeviceA']
)

for app in no_deviceA:
   assert app.device != 'DeviceA'
   print(f"Filtered out 'DeviceA': {app.name}")

# Combine exact_match with multiple exclusions
combined_filters = profiles.list(
   folder='Texas',
   exact_match=True,
   exclude_folders=['All'],
   exclude_snippets=['default'],
   exclude_devices=['DeviceA']
)

for app in combined_filters:
   print(f"Combined filters result: {app.name} in {app.folder}")
```

### Controlling Pagination with max_limit

The SDK supports pagination through the `max_limit` parameter, which defines how many objects are retrieved per API call. By default, `max_limit` is set to 2500. The API itself imposes a maximum allowed value of 5000. If you set `max_limit` higher than 5000, it will be capped to the API's maximum. The `list()` method will continue to iterate through all objects until all results have been retrieved. Adjusting `max_limit` can help manage retrieval performance and memory usage when working with large datasets.

```python
# Initialize the client with a custom max_limit for anti-spyware profiles
# This will retrieve up to 4321 objects per API call, up to the API limit of 5000.
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
    anti_spyware_profile_max_limit=4321
)

# Now when we call list(), it will use the specified max_limit for each request
# while auto-paginating through all available objects.
all_profiles = client.anti_spyware_profile.list(folder='Texas')

# 'all_profiles' contains all objects from 'Texas', fetched in chunks of up to 4321 at a time.
```

### Deleting Profiles

```python
# Delete by ID
profile_id = "123e4567-e89b-12d3-a456-426655440000"
client.anti_spyware_profile.delete(profile_id)
```

## Managing Configuration Changes

### Performing Commits

```python
# Prepare commit parameters
commit_params = {
    "folders": ["Texas"],
    "description": "Updated anti-spyware profiles",
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
        "name": "test-profile",
        "description": "Test anti-spyware profile",
        "folder": "Texas",
        "rules": [
            {
                "name": "test-rule",
                "severity": ["critical"],
                "category": "spyware",
                "action": {"alert": {}}
            }
        ]
    }

    # Create the profile using the client
    new_profile = client.anti_spyware_profile.create(profile_config)

    # Commit changes using the client
    result = client.commit(
        folders=["Texas"],
        description="Added test profile",
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
    - Use descriptive rule names
    - Set appropriate severity levels
    - Configure actions based on threat level
    - Document rule purposes
    - Review rule effectiveness

2. **Container Management**
    - Always specify exactly one container
    - Use consistent container names
    - Validate container existence
    - Group related profiles

3. **Client Usage**
    - Use the unified client interface (`client.anti_spyware_profile`) for simpler code
    - Perform commits directly on the client (`client.commit()`)
    - Monitor jobs using client methods (`client.get_job_status()`, `client.list_jobs()`)
    - Initialize the client once and reuse across different object types

4. **Performance**
    - Use appropriate pagination
    - Cache frequently accessed profiles
    - Monitor cloud analysis impact
    - Implement proper retry logic
    - Track job completion

5. **Security**
    - Follow least privilege principle
    - Validate input data
    - Monitor profile changes
    - Review audit logs
    - Document modifications

## Full Script Examples

For examples related to anti-spyware profiles, check the [examples directory](https://github.com/cdot65/pan-scm-sdk/tree/main/examples/scm/config/security_services/).

## Related Models

- [AntiSpywareProfileCreateModel](../../models/security_services/anti_spyware_profile_models.md)
- [AntiSpywareProfileUpdateModel](../../models/security_services/anti_spyware_profile_models.md)
- [AntiSpywareProfileResponseModel](../../models/security_services/anti_spyware_profile_models.md)
