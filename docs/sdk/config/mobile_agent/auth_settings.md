# GlobalProtect Authentication Settings

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Authentication Settings Model Attributes](#authentication-settings-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating Authentication Settings](#creating-authentication-settings)
    - [Retrieving Authentication Settings](#retrieving-authentication-settings)
    - [Updating Authentication Settings](#updating-authentication-settings)
    - [Listing Authentication Settings](#listing-authentication-settings)
    - [Ordering Authentication Settings](#ordering-authentication-settings)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Deleting Authentication Settings](#deleting-authentication-settings)
7. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Full Script Examples](#full-script-examples)
11. [Related Models](#related-models)

## Overview

The `AuthSettings` class provides functionality to manage GlobalProtect authentication settings in Palo Alto Networks' Strata Cloud Manager. This
class inherits from `BaseObject` and provides methods for creating, retrieving, updating, deleting, and reordering authentication settings objects
for GlobalProtect mobile agent configurations.

## Core Methods

| Method      | Description                                | Parameters                         | Return Type                   |
|-------------|--------------------------------------------|------------------------------------|------------------------------ |
| `create()`  | Creates a new authentication settings      | `data: Dict[str, Any]`            | `AuthSettingsResponseModel`   |
| `get()`     | Retrieves settings by ID                   | `object_id: str`                  | `AuthSettingsResponseModel`   |
| `update()`  | Updates existing settings                  | `object_id: str, data: Dict[str, Any]` | `AuthSettingsResponseModel` |
| `delete()`  | Deletes authentication settings            | `object_id: str`                  | `None`                        |
| `list()`    | Lists settings with filtering              | `folder: str`, `**filters`        | `List[AuthSettingsResponseModel]` |
| `fetch()`   | Gets settings by name and folder           | `name: str`, `folder: str`        | `AuthSettingsResponseModel`   |
| `move()`    | Reorders authentication settings           | `move_data: Dict[str, Any]`       | `None`                        |

## Authentication Settings Model Attributes

| Attribute                               | Type               | Required     | Default | Description                                               |
|-----------------------------------------|--------------------|--------------|---------|-----------------------------------------------------------|
| `name`                                  | str                | Yes          | None    | Name of the authentication settings (max 63 chars)        |
| `authentication_profile`                | str                | Yes          | None    | Name of the authentication profile to use                  |
| `os`                                    | OperatingSystem    | No           | Any     | Target operating system                                   |
| `user_credential_or_client_cert_required` | bool             | No           | None    | Whether user credentials or client certificate is required |
| `folder`                                | str                | Yes*         | None    | Must be "Mobile Users" for all operations                 |

\* Required for create operations, optional for update

## Exceptions

| Exception                    | HTTP Code | Description                                   |
|------------------------------|-----------|-----------------------------------------------|
| `InvalidObjectError`         | 400       | Invalid settings data or format               |
| `MissingQueryParameterError` | 400       | Missing required parameters                   |
| `NameNotUniqueError`         | 409       | Authentication settings name already exists   |
| `ObjectNotPresentError`      | 404       | Authentication settings not found             |
| `AuthenticationError`        | 401       | Authentication failed                         |
| `ServerError`                | 500       | Internal server error                         |

## Basic Configuration

The AuthSettings service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

### Unified Client Interface (Recommended)

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the AuthSettings service directly through the client
# No need to create a separate AuthSettings instance
auth_settings = client.auth_setting
```

### Traditional Service Instantiation (Legacy)

```python
from scm.client import Scm
from scm.config.mobile_agent import AuthSettings

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize AuthSettings object explicitly
auth_settings = AuthSettings(client)
```

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

## Usage Examples

### Creating Authentication Settings

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Prepare authentication settings configuration
auth_settings_config = {
   "name": "windows_auth",
   "authentication_profile": "windows-sso-profile",
   "os": "Windows",
   "user_credential_or_client_cert_required": True,
   "folder": "Mobile Users"  # Must be "Mobile Users"
}

# Create the authentication settings
new_auth_settings = client.auth_setting.create(auth_settings_config)
print(f"Created authentication settings: {new_auth_settings.name}")

# Another example for a different operating system
ios_auth_config = {
   "name": "ios_auth",
   "authentication_profile": "mobile-cert-auth",
   "os": "iOS",
   "user_credential_or_client_cert_required": False,
   "folder": "Mobile Users"
}

# Create iOS authentication settings
ios_auth_settings = client.auth_setting.create(ios_auth_config)
```

### Retrieving Authentication Settings

```python
# Fetch by name and folder (folder must be "Mobile Users")
auth_settings = client.auth_setting.fetch(name="windows_auth", folder="Mobile Users")
print(f"Found authentication settings: {auth_settings.name}")

# Get by ID
auth_settings_by_id = client.auth_setting.get(auth_settings.id)
print(f"Retrieved authentication settings: {auth_settings_by_id.name}")
```

### Updating Authentication Settings

```python
# Fetch existing authentication settings
existing = client.auth_setting.fetch(name="windows_auth", folder="Mobile Users")

# Modify attributes using dot notation
existing.name = "windows_auth_updated"
existing.authentication_profile = "updated-profile"
existing.user_credential_or_client_cert_required = False

# Perform update
updated_settings = client.auth_setting.update(existing.id, existing.model_dump(exclude_unset=True))
print(f"Updated authentication settings: {updated_settings.name}")
```

### Listing Authentication Settings

```python
# List all authentication settings (always from "Mobile Users" folder)
all_settings = client.auth_setting.list()

# Process results
for setting in all_settings:
    print(f"Name: {setting.name}, OS: {setting.os}, Profile: {setting.authentication_profile}")
```

### Ordering Authentication Settings

The GlobalProtect authentication settings evaluation order is important, as settings are evaluated from top to bottom. The `move()` method allows you to reorder authentication settings in the configuration.

```python
# Move a settings entry to the top of the list
top_move_config = {
    "name": "windows_auth",
    "where": "top"
}
client.auth_setting.move(top_move_config)

# Move a settings entry to the bottom of the list
bottom_move_config = {
    "name": "android_auth",
    "where": "bottom"
}
client.auth_setting.move(bottom_move_config)

# Move a settings entry before another entry
before_move_config = {
    "name": "ios_auth",
    "where": "before",
    "destination": "android_auth"
}
client.auth_setting.move(before_move_config)

# Move a settings entry after another entry
after_move_config = {
    "name": "browser_auth",
    "where": "after",
    "destination": "ios_auth"
}
client.auth_setting.move(after_move_config)
```

### Controlling Pagination with max_limit

The SDK supports pagination through the `max_limit` parameter, which defines how many objects are retrieved per API call. By default, `max_limit` is set to 2500. The API itself imposes a maximum allowed value of 5000.

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
client.auth_setting.max_limit = 1000

# List all authentication settings
all_settings = client.auth_setting.list()
```

### Deleting Authentication Settings

```python
# Get the authentication settings
auth_settings = client.auth_setting.fetch(name="windows_auth", folder="Mobile Users")

# Delete the settings by ID
client.auth_setting.delete(auth_settings.id)
print(f"Deleted authentication settings: {auth_settings.name}")
```

## Managing Configuration Changes

### Performing Commits

```python
# Prepare commit parameters
commit_params = {
   "folders": ["Mobile Users"],
   "description": "Updated GlobalProtect authentication settings",
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
   ObjectNotPresentError
)

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

try:
   # Create authentication settings
   auth_settings_config = {
      "name": "windows_auth",
      "authentication_profile": "windows-sso-profile",
      "os": "Windows",
      "user_credential_or_client_cert_required": True,
      "folder": "Mobile Users"
   }

   new_auth_settings = client.auth_setting.create(auth_settings_config)

   # Commit changes
   result = client.commit(
      folders=["Mobile Users"],
      description="Added GlobalProtect authentication settings",
      sync=True
   )

   # Check job status
   status = client.get_job_status(result.job_id)

except InvalidObjectError as e:
   print(f"Invalid authentication settings data: {e.message}")
except NameNotUniqueError as e:
   print(f"Authentication settings name already exists: {e.message}")
except ObjectNotPresentError as e:
   print(f"Authentication settings not found: {e.message}")
except MissingQueryParameterError as e:
   print(f"Missing parameter: {e.message}")
```

## Best Practices

1. **Client Usage**
    - Use the unified client interface (`client.auth_setting`) for streamlined code
    - Create a single client instance and reuse it across your application
    - Perform commit operations directly on the client object (`client.commit()`)
    - For custom max_limit settings, create a dedicated service instance if needed

2. **Folder Management**
    - Always use "Mobile Users" as the folder for authentication settings
    - Remember that the folder is required for create operations

3. **Error Handling**
    - Implement comprehensive error handling for all operations
    - Check job status after commits
    - Handle specific exceptions before generic ones
    - Log error details for troubleshooting

4. **Authentication Order**
    - Consider the evaluation order of authentication settings
    - Use the move() method to ensure proper ordering of settings
    - Place more specific OS settings before more general ones

5. **Performance**
    - Reuse client instances
    - Implement proper retry mechanisms
    - Cache frequently accessed objects

6. **Security**
    - Follow the least privilege principle
    - Validate input data
    - Use secure connection settings
    - Implement proper authentication handling

## Full Script Examples

Refer to
the [auth_settings.py example](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/mobile_agent/auth_settings.py).

## Related Models

- [AuthSettingsBaseModel](../../models/mobile_agent/auth_settings_models.md#Overview)
- [AuthSettingsCreateModel](../../models/mobile_agent/auth_settings_models.md#Overview)
- [AuthSettingsUpdateModel](../../models/mobile_agent/auth_settings_models.md#Overview)
- [AuthSettingsResponseModel](../../models/mobile_agent/auth_settings_models.md#Overview)
- [AuthSettingsMoveModel](../../models/mobile_agent/auth_settings_models.md#Overview)
- [OperatingSystem](../../models/mobile_agent/auth_settings_models.md#Overview)
- [MovePosition](../../models/mobile_agent/auth_settings_models.md#Overview)
