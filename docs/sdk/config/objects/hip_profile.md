# HIP Profile Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [HIP Profile Model Attributes](#hip-profile-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating HIP Profiles](#creating-hip-profiles)
    - [Retrieving HIP Profiles](#retrieving-hip-profiles)
    - [Updating HIP Profiles](#updating-hip-profiles)
    - [Listing HIP Profiles](#listing-hip-profiles)
    - [Filtering Responses](#filtering-responses)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Deleting HIP Profiles](#deleting-hip-profiles)
7. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Full Script Examples](#full-script-examples)
11. [Related Models](#related-models)

## Overview

The `HIPProfile` class provides functionality to manage Host Information Profile (HIP) profiles in Palo Alto Networks' Strata
Cloud Manager. This class inherits from `BaseObject` and provides methods for creating, retrieving, updating, and deleting
HIP profiles. HIP profiles define security posture matching criteria that can be used in security policies to enforce endpoint compliance.

## Core Methods

| Method     | Description                       | Parameters                                                                     | Return Type                     |
|------------|-----------------------------------|--------------------------------------------------------------------------------|---------------------------------|
| `create()` | Creates a new HIP profile         | `data: Dict[str, Any]`                                                         | `HIPProfileResponseModel`       |
| `get()`    | Retrieves a HIP profile by ID     | `object_id: str`                                                               | `HIPProfileResponseModel`       |
| `update()` | Updates an existing HIP profile   | `hip_profile: HIPProfileUpdateModel`                                           | `HIPProfileResponseModel`       |
| `delete()` | Deletes a HIP profile             | `object_id: str`                                                               | `None`                          |
| `list()`   | Lists HIP profiles with filtering | `folder: str`, `snippet: str`, `device: str`, `exact_match: bool`, `**filters` | `List[HIPProfileResponseModel]` |
| `fetch()`  | Gets HIP profile by name          | `name: str`, `folder: str`, `snippet: str`, `device: str`                      | `HIPProfileResponseModel`       |

## HIP Profile Model Attributes

| Attribute          | Type                 | Required | Default | Description                                      |
|--------------------|----------------------|----------|---------|--------------------------------------------------|
| `name`             | str                  | Yes      | None    | Name of HIP profile (max 31 chars)               |
| `id`               | UUID                 | Yes*     | None    | Unique identifier (*response only)               |
| `description`      | str                  | No       | None    | Profile description (max 255 chars)              |
| `match`            | str                  | Yes      | None    | Match expression for the profile (max 2048 chars)|
| `folder`           | str                  | Yes**    | None    | Folder location (**one container required)       |
| `snippet`          | str                  | Yes**    | None    | Snippet location (**one container required)      |
| `device`           | str                  | Yes**    | None    | Device location (**one container required)       |

## Exceptions

| Exception                    | HTTP Code | Description                        |
|------------------------------|-----------|------------------------------------|
| `InvalidObjectError`         | 400       | Invalid HIP profile data or format |
| `MissingQueryParameterError` | 400       | Missing required parameters        |
| `NameNotUniqueError`         | 409       | HIP profile name already exists    |
| `ObjectNotPresentError`      | 404       | HIP profile not found              |
| `ReferenceNotZeroError`      | 409       | HIP profile still referenced       |
| `AuthenticationError`        | 401       | Authentication failed              |
| `ServerError`                | 500       | Internal server error              |

## Basic Configuration

```python
from scm.client import ScmClient

# Initialize client using the unified client approach
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the hip_profile module directly through the client
# client.hip_profile is automatically initialized for you
```

You can also use the traditional approach if preferred:

```python
from scm.client import Scm
from scm.config.objects import HIPProfile

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize HIPProfile object
hip_profiles = HIPProfile(client)
```

## Usage Examples

### Creating HIP Profiles

```python
# Basic HIP profile with simple match expression
basic_profile_config = {
    "name": "windows-workstations",
    "folder": "Shared",
    "description": "Windows workstations with basic security requirements",
    "match": '"is-win"'  # Single HIP object reference
}

# Create basic HIP profile
basic_profile = client.hip_profile.create(basic_profile_config)

# HIP profile with complex match expression using AND/OR logic
complex_profile_config = {
    "name": "secure-workstations",
    "folder": "Shared",
    "description": "Secured workstations with enhanced security posture",
    "match": '"is-win" and "is-firewall-enabled"'  # Combined match expression
}

# Create complex HIP profile
complex_profile = client.hip_profile.create(complex_profile_config)

# HIP profile with negative match expression
negative_profile_config = {
    "name": "non-windows-devices",
    "folder": "Shared",
    "description": "All devices except Windows workstations",
    "match": 'not ("is-win")'  # NOT operator in match expression
}

# Create negative match HIP profile
negative_profile = client.hip_profile.create(negative_profile_config)
```

### Retrieving HIP Profiles

```python
# Fetch by name and folder
hip_profile = client.hip_profile.fetch(name="windows-workstations", folder="Shared")
print(f"Found HIP profile: {hip_profile.name}")

# Get by ID
hip_by_id = client.hip_profile.get(hip_profile.id)
print(f"Retrieved HIP profile: {hip_by_id.name}")
print(f"Match expression: {hip_by_id.match}")
```

### Updating HIP Profiles

```python
# Fetch existing HIP profile
existing_profile = client.hip_profile.fetch(name="secure-workstations", folder="Shared")

# Modify attributes using dot notation
existing_profile.description = "Enhanced security requirements for workstations"
existing_profile.match = '"is-win" and "is-firewall-enabled" and "is-disk-encrypted"'

# Perform update
updated_profile = client.hip_profile.update(existing_profile)
print(f"Updated match expression: {updated_profile.match}")
```

### Listing HIP Profiles

```python
# List with direct filter parameters
filtered_profiles = client.hip_profile.list(
    folder='Shared'
)

# Process results
for profile in filtered_profiles:
    print(f"Name: {profile.name}")
    print(f"Match: {profile.match}")

# Define filter parameters as dictionary
list_params = {
    "folder": "Shared"
}

# List with filters as kwargs
filtered_profiles = client.hip_profile.list(**list_params)
```

### Filtering Responses

The `list()` method supports additional parameters to refine your query results even further. You can leverage the `exact_match`, `exclude_folders`, `exclude_snippets`, and `exclude_devices` parameters to control which objects are included or excluded after the initial API response is fetched.

**Parameters:**

- `exact_match (bool)`: When `True`, only objects defined exactly in the specified container (`folder`, `snippet`, or `device`) are returned. Inherited or propagated objects are filtered out.
- `exclude_folders (List[str])`: Provide a list of folder names that you do not want included in the results.
- `exclude_snippets (List[str])`: Provide a list of snippet values to exclude from the results.
- `exclude_devices (List[str])`: Provide a list of device values to exclude from the results.

**Examples:**

```python
# Only return HIP profiles defined exactly in 'Shared'
exact_profiles = client.hip_profile.list(
    folder='Shared',
    exact_match=True
)

for profile in exact_profiles:
    print(f"Exact match: {profile.name} in {profile.folder}")

# Exclude all HIP profiles from the 'All' folder
no_all_profiles = client.hip_profile.list(
    folder='Shared',
    exclude_folders=['All']
)

for profile in no_all_profiles:
    assert profile.folder != 'All'
    print(f"Filtered out 'All': {profile.name}")

# Exclude HIP profiles that come from 'default' snippet
no_default_snippet = client.hip_profile.list(
    folder='Shared',
    exclude_snippets=['default']
)

for profile in no_default_snippet:
    assert profile.snippet != 'default'
    print(f"Filtered out 'default' snippet: {profile.name}")

# Exclude HIP profiles associated with 'DeviceA'
no_deviceA = client.hip_profile.list(
    folder='Shared',
    exclude_devices=['DeviceA']
)

for profile in no_deviceA:
    assert profile.device != 'DeviceA'
    print(f"Filtered out 'DeviceA': {profile.name}")

# Combine exact_match with multiple exclusions
combined_filters = client.hip_profile.list(
    folder='Shared',
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

# Configure max_limit on the hip_profile service
client.hip_profile.max_limit = 4321

# List all HIP profiles - auto-paginates through results
all_profiles = client.hip_profile.list(folder='Shared')

# The list() method will retrieve up to 4321 objects per API call (max 5000)
# and auto-paginate through all available objects.
```

### Deleting HIP Profiles

```python
# Delete by ID
profile_id = "123e4567-e89b-12d3-a456-426655440000"
client.hip_profile.delete(profile_id)
```

## Managing Configuration Changes

### Performing Commits

```python
# Prepare commit parameters
commit_params = {
    "folders": ["Shared"],
    "description": "Updated HIP profiles",
    "sync": True,
    "timeout": 300  # 5 minute timeout
}

# Commit the changes
result = client.commit(**commit_params)

print(f"Commit job ID: {result.job_id}")
```

### Monitoring Jobs

```python
# Get status of specific job
job_status = client.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

# List recent jobs
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
    # Create HIP profile configuration
    hip_config = {
        "name": "test-hip-profile",
        "folder": "Shared",
        "description": "Test HIP profile",
        "match": '"is-win" or "is-mac"'
    }

    # Create the HIP profile using the unified client
    new_profile = client.hip_profile.create(hip_config)

    # Commit changes directly on the client
    result = client.commit(
        folders=["Shared"],
        description="Added test HIP profile",
        sync=True
    )

    # Check job status on the client
    status = client.get_job_status(result.job_id)

except InvalidObjectError as e:
    print(f"Invalid HIP profile data: {e.message}")
except NameNotUniqueError as e:
    print(f"HIP profile name already exists: {e.message}")
except ObjectNotPresentError as e:
    print(f"HIP profile not found: {e.message}")
except ReferenceNotZeroError as e:
    print(f"HIP profile still in use: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing parameter: {e.message}")
```

## Best Practices

1. **Client Usage**
    - Use the unified `ScmClient` approach for simpler code
    - Access HIP profile operations via `client.hip_profile` property
    - Perform commit operations directly on the client
    - Monitor jobs directly on the client
    - Set appropriate max_limit parameters for large datasets using `hip_profile_max_limit`

2. **Match Expression Syntax**
    - Use quoted object names in match expressions (e.g., `"is-win"`)
    - Combine expressions with boolean operators (`and`, `or`, `not`)
    - Group complex expressions with parentheses
    - Verify HIP objects exist before referencing them
    - Keep expressions simple and maintainable

3. **Container Management**
    - Always specify exactly one container (folder, snippet, or device)
    - Use consistent container names
    - Validate container existence
    - Group related HIP profiles
    - Consider inheritance patterns

4. **Performance**
    - Set appropriate max_limit values
    - Use pagination for large lists
    - Cache frequently accessed profiles
    - Implement proper retry logic
    - Monitor API response times

5. **Security**
    - Follow least privilege principle
    - Validate input data
    - Use secure connection settings
    - Implement proper authentication
    - Monitor security posture changes

6. **Error Handling**
    - Implement comprehensive error handling
    - Check job status after commits
    - Log error details
    - Handle specific exceptions
    - Validate match expressions before creation

## Full Script Examples

Refer to
the [hip_profile.py example](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/objects/hip_profile.py).

## Related Models

- [HIPProfileCreateModel](../../models/objects/hip_profile_models.md#Overview)
- [HIPProfileUpdateModel](../../models/objects/hip_profile_models.md#Overview)
- [HIPProfileResponseModel](../../models/objects/hip_profile_models.md#Overview)
