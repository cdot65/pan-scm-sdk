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

| Method     | Description                       | Parameters                           | Return Type                     |
|------------|-----------------------------------|--------------------------------------|---------------------------------|
| `create()` | Creates a new HIP profile         | `data: Dict[str, Any]`               | `HIPProfileResponseModel`       |
| `get()`    | Retrieves a HIP profile by ID     | `object_id: str`                     | `HIPProfileResponseModel`       |
| `update()` | Updates an existing HIP profile   | `hip_profile: HIPProfileUpdateModel` | `HIPProfileResponseModel`       |
| `delete()` | Deletes a HIP profile             | `object_id: str`                     | `None`                          |
| `list()`   | Lists HIP profiles with filtering | `folder: str`, `**filters`           | `List[HIPProfileResponseModel]` |
| `fetch()`  | Gets HIP profile by name          | `name: str`, `folder: str`           | `HIPProfileResponseModel`       |

## HIP Profile Model Attributes

| Attribute          | Type                 | Required | Description                                 |
|--------------------|----------------------|----------|---------------------------------------------|
| `name`             | str                  | Yes      | Name of HIP profile (max 31 chars)          |
| `id`               | UUID                 | Yes*     | Unique identifier (*response only)          |
| `description`      | str                  | No       | Profile description (max 255 chars)         |
| `match`            | str                  | Yes      | Match expression for the profile            |
| `folder`           | str                  | Yes**    | Folder location (**one container required)  |
| `snippet`          | str                  | Yes**    | Snippet location (**one container required) |
| `device`           | str                  | Yes**    | Device location (**one container required)  |

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

<div class="termy">

<!-- termynal -->

```python
from scm.client import ScmClient

# Initialize client using the unified client approach
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
    hip_profile_max_limit=5000  # Optional: set custom max_limit
)

# Access the hip_profile module directly through the client
# client.hip_profile is automatically initialized for you
```

</div>

You can also use the traditional approach if preferred:

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.objects import HIPProfile

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize HIPProfile with custom max_limit
hip_profiles = HIPProfile(client, max_limit=5000)
```

</div>

## Usage Examples

### Creating HIP Profiles

<div class="termy">

<!-- termynal -->

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

</div>

### Retrieving HIP Profiles

<div class="termy">

<!-- termynal -->

```python
# Fetch by name and folder
hip_profile = client.hip_profile.fetch(name="windows-workstations", folder="Shared")
print(f"Found HIP profile: {hip_profile.name}")

# Get by ID
hip_by_id = client.hip_profile.get(hip_profile.id)
print(f"Retrieved HIP profile: {hip_by_id.name}")
print(f"Match expression: {hip_by_id.match}")
```

</div>

### Updating HIP Profiles

<div class="termy">

<!-- termynal -->

```python
# Fetch existing HIP profile
existing_profile = client.hip_profile.fetch(name="secure-workstations", folder="Shared")

# Create update model with modified match expression
from scm.models.objects import HIPProfileUpdateModel

update_model = HIPProfileUpdateModel(
    id=existing_profile.id,
    name=existing_profile.name,
    description="Enhanced security requirements for workstations",
    match='"is-win" and "is-firewall-enabled" and "is-disk-encrypted"'
)

# Perform update
updated_profile = client.hip_profile.update(update_model)
print(f"Updated match expression: {updated_profile.match}")
```

</div>

### Listing HIP Profiles

<div class="termy">

<!-- termynal -->

```python
# List with direct filter parameters
filtered_profiles = client.hip_profile.list(
    folder='Shared',
    exact_match=True
)

# Process results
for profile in filtered_profiles:
    print(f"Name: {profile.name}")
    print(f"Match: {profile.match}")

# Define filter parameters as dictionary
list_params = {
    "folder": "Shared",
    "exclude_folders": ["Test", "Development"]
}

# List with filters as kwargs
filtered_profiles = client.hip_profile.list(**list_params)
```

</div>

### Deleting HIP Profiles

<div class="termy">

<!-- termynal -->

```python
# Delete by ID
profile_id = "123e4567-e89b-12d3-a456-426655440000"
client.hip_profile.delete(profile_id)
```

</div>

## Managing Configuration Changes

### Performing Commits

<div class="termy">

<!-- termynal -->

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

</div>

### Monitoring Jobs

<div class="termy">

<!-- termynal -->

```python
# Get status of specific job
job_status = client.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

# List recent jobs
recent_jobs = client.list_jobs(limit=10)
for job in recent_jobs.data:
    print(f"Job {job.id}: {job.type_str} - {job.status_str}")
```

</div>

## Error Handling

<div class="termy">

<!-- termynal -->

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

</div>

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
