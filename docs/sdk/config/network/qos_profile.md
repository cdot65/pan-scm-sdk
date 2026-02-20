# QoS Profile Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [QoS Profile Model Attributes](#qos-profile-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating QoS Profiles](#creating-qos-profiles)
    - [Retrieving QoS Profiles](#retrieving-qos-profiles)
    - [Updating QoS Profiles](#updating-qos-profiles)
    - [Listing QoS Profiles](#listing-qos-profiles)
    - [Filtering Responses](#filtering-responses)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Deleting QoS Profiles](#deleting-qos-profiles)
7. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Related Models](#related-models)

## Overview

The `QosProfile` class manages QoS profile objects in Palo Alto Networks' Strata Cloud Manager. It extends from `BaseObject` and offers methods to create, retrieve, update, list, fetch, and delete QoS profiles. These profiles define aggregate bandwidth settings and class bandwidth type configurations used to enforce Quality of Service policies on network traffic.

## Core Methods

| Method     | Description                                                | Parameters                                                                                                                       | Return Type                      |
|------------|------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|----------------------------------|
| `create()` | Creates a new QoS profile                                  | `data: Dict[str, Any]`                                                                                                           | `QosProfileResponseModel`        |
| `get()`    | Retrieves a QoS profile by its unique ID                   | `object_id: str`                                                                                                                 | `QosProfileResponseModel`        |
| `update()` | Updates an existing QoS profile                            | `profile: QosProfileUpdateModel`                                                                                                 | `QosProfileResponseModel`        |
| `list()`   | Lists QoS profiles with optional filtering                 | `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`, `exact_match: bool = False`, plus additional filters | `List[QosProfileResponseModel]`  |
| `fetch()`  | Fetches a single QoS profile by name within a container    | `name: str`, `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`                                          | `QosProfileResponseModel`        |
| `delete()` | Deletes a QoS profile by its ID                            | `object_id: str`                                                                                                                 | `None`                           |

## QoS Profile Model Attributes

| Attribute              | Type              | Required | Default | Description                                                       |
|------------------------|-------------------|----------|---------|-------------------------------------------------------------------|
| `name`                 | str               | Yes      | None    | Profile name. Max 31 chars. Pattern: `[0-9a-zA-Z._-]`            |
| `id`                   | UUID              | Yes*     | None    | Unique identifier (*response/update only)                         |
| `aggregate_bandwidth`  | Dict[str, Any]    | No       | None    | Aggregate bandwidth settings (egress_max, egress_guaranteed)      |
| `class_bandwidth_type` | Dict[str, Any]    | No       | None    | Class bandwidth type configuration (mbps or percentage)           |
| `folder`               | str               | No**     | None    | Folder location. Max 64 chars                                     |
| `snippet`              | str               | No**     | None    | Snippet location. Max 64 chars                                    |
| `device`               | str               | No**     | None    | Device location. Max 64 chars                                     |

\* Only required for update and response models
\** Exactly one container (folder/snippet/device) must be provided for create operations

## Exceptions

| Exception                    | HTTP Code | Description                                                                   |
|------------------------------|-----------|-------------------------------------------------------------------------------|
| `InvalidObjectError`         | 400       | Thrown when provided data or parameters are invalid                           |
| `MissingQueryParameterError` | 400       | Thrown when required query parameters (e.g., `name` or `folder`) are missing  |
| `NameNotUniqueError`         | 409       | Profile name already exists                                                   |
| `ObjectNotPresentError`      | 404       | Profile not found                                                             |
| `ReferenceNotZeroError`      | 409       | Profile still referenced by other objects                                     |
| `AuthenticationError`        | 401       | Authentication failed                                                         |
| `ServerError`                | 500       | Internal server error                                                         |

## Basic Configuration

The QoS Profile service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

### Unified Client Interface (Recommended)

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Access the QoS Profile service directly through the client
qos_profiles = client.qos_profile
```

### Traditional Service Instantiation (Legacy)

```python
from scm.client import Scm
from scm.config.network import QosProfile

# Initialize client
client = Scm(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Initialize QosProfile object explicitly
qos_profiles = QosProfile(client)
```

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

## Usage Examples

### Creating QoS Profiles

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Create a QoS profile with aggregate bandwidth settings
profile_data = {
   "name": "high-priority-qos",
   "aggregate_bandwidth": {
      "egress_max": 1000,
      "egress_guaranteed": 500
   },
   "folder": "Texas"
}

new_profile = client.qos_profile.create(profile_data)
print(f"Created QoS profile with ID: {new_profile.id}")

# Create a profile with class bandwidth type (percentage-based)
class_profile = {
   "name": "class-based-qos",
   "aggregate_bandwidth": {
      "egress_max": 2000,
      "egress_guaranteed": 1000
   },
   "class_bandwidth_type": {
      "percentage": {
         "class1": 30,
         "class2": 20,
         "class3": 15,
         "class4": 10
      }
   },
   "folder": "Texas"
}

class_qos = client.qos_profile.create(class_profile)
print(f"Created class-based QoS profile with ID: {class_qos.id}")
```

### Retrieving QoS Profiles

```python
# Fetch by name and folder
profile = client.qos_profile.fetch(
   name="high-priority-qos",
   folder="Texas"
)
print(f"Found profile: {profile.name}")

# Get by ID
profile_by_id = client.qos_profile.get(profile.id)
print(f"Retrieved profile: {profile_by_id.name}")
```

### Updating QoS Profiles

```python
# Fetch existing profile
existing_profile = client.qos_profile.fetch(
   name="high-priority-qos",
   folder="Texas"
)

# Modify the aggregate bandwidth settings
existing_profile.aggregate_bandwidth = {
   "egress_max": 1500,
   "egress_guaranteed": 750
}

# Perform update
updated_profile = client.qos_profile.update(existing_profile)
```

### Listing QoS Profiles

```python
# List all QoS profiles in a folder
profiles = client.qos_profile.list(
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
exact_profiles = client.qos_profile.list(
   folder='Texas',
   exact_match=True
)

for profile in exact_profiles:
   print(f"Exact match: {profile.name} in {profile.folder}")

# Exclude all profiles from the 'All' folder
no_all_profiles = client.qos_profile.list(
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
client.qos_profile.max_limit = 4000

# List all profiles - auto-paginates through results
all_profiles = client.qos_profile.list(folder='Texas')
```

### Deleting QoS Profiles

```python
# Delete by ID
profile_id = "123e4567-e89b-12d3-a456-426655440000"
client.qos_profile.delete(profile_id)
```

## Managing Configuration Changes

### Performing Commits

```python
# Prepare commit parameters
commit_params = {
   "folders": ["Texas"],
   "description": "Updated QoS profile configurations",
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
   # Create QoS profile
   profile_config = {
      "name": "test-qos-profile",
      "aggregate_bandwidth": {
         "egress_max": 1000,
         "egress_guaranteed": 500
      },
      "folder": "Texas"
   }

   new_profile = client.qos_profile.create(profile_config)

   # Commit changes
   result = client.commit(
      folders=["Texas"],
      description="Added QoS profile",
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
   - Use the unified client interface (`client.qos_profile`) for streamlined code
   - Create a single client instance and reuse it across your application
   - Perform commit operations directly on the client object (`client.commit()`)

2. **QoS Profile Configuration**
   - Define clear aggregate bandwidth limits appropriate for your network capacity
   - Use percentage-based class bandwidth allocation for proportional traffic distribution
   - Ensure egress_guaranteed values do not exceed egress_max limits
   - Create separate profiles for different traffic classes or priority levels

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

6. **Bandwidth Planning**
   - Plan QoS profiles based on actual traffic patterns and requirements
   - Monitor bandwidth utilization and adjust profiles as needed
   - Document the purpose of each QoS profile for operational clarity

## Related Models

- [QosProfileBaseModel](../../models/network/qos_profile_models.md#Overview)
- [QosProfileCreateModel](../../models/network/qos_profile_models.md#Overview)
- [QosProfileUpdateModel](../../models/network/qos_profile_models.md#Overview)
- [QosProfileResponseModel](../../models/network/qos_profile_models.md#Overview)
