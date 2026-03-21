# GlobalProtect Authentication Settings Configuration Object

Manages GlobalProtect authentication settings for controlling authentication methods by operating system in Palo Alto Networks Strata Cloud Manager.

## Class Overview

The `AuthSettings` class inherits from `BaseObject` and provides CRUD operations plus ordering for GlobalProtect authentication settings objects.

### Methods

| Method     | Description                          | Parameters                               | Return Type                       |
|------------|--------------------------------------|------------------------------------------|-----------------------------------|
| `create()` | Creates new authentication settings  | `data: Dict[str, Any]`                   | `AuthSettingsResponseModel`       |
| `get()`    | Retrieves settings by ID            | `object_id: str`                         | `AuthSettingsResponseModel`       |
| `update()` | Updates existing settings            | `object_id: str`, `data: Dict[str, Any]` | `AuthSettingsResponseModel`       |
| `delete()` | Deletes authentication settings      | `object_id: str`                         | `None`                            |
| `list()`   | Lists settings with filtering        | `folder: str`, `**filters`               | `List[AuthSettingsResponseModel]` |
| `fetch()`  | Gets settings by name and folder     | `name: str`, `folder: str`               | `AuthSettingsResponseModel`       |
| `move()`   | Reorders authentication settings     | `move_data: Dict[str, Any]`              | `None`                            |

### Model Attributes

| Attribute                                 | Type            | Required | Default | Description                                                |
|-------------------------------------------|-----------------|----------|---------|------------------------------------------------------------|
| `name`                                    | str             | Yes      | None    | Name of the authentication settings (max 63 chars)         |
| `authentication_profile`                  | str             | Yes      | None    | Name of the authentication profile to use                  |
| `os`                                      | OperatingSystem | No       | Any     | Target operating system                                    |
| `user_credential_or_client_cert_required` | bool            | No       | None    | Whether user credentials or client certificate is required |
| `folder`                                  | str             | Yes*     | None    | Must be "Mobile Users" for all operations                  |

\* Required for create operations

### Exceptions

| Exception                    | HTTP Code | Description                                 |
|------------------------------|-----------|---------------------------------------------|
| `InvalidObjectError`         | 400       | Invalid settings data or format             |
| `MissingQueryParameterError` | 400       | Missing required parameters                 |
| `NameNotUniqueError`         | 409       | Authentication settings name already exists |
| `ObjectNotPresentError`      | 404       | Authentication settings not found           |
| `AuthenticationError`        | 401       | Authentication failed                       |
| `ServerError`                | 500       | Internal server error                       |

### Basic Configuration

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

auth_settings = client.auth_setting
```

## Methods

### List Authentication Settings

```python
all_settings = client.auth_setting.list()

for setting in all_settings:
    print(f"Name: {setting.name}, OS: {setting.os}, Profile: {setting.authentication_profile}")
```

**Controlling pagination with max_limit:**

```python
client.auth_setting.max_limit = 1000

all_settings = client.auth_setting.list()
```

### Fetch Authentication Settings

```python
auth_settings = client.auth_setting.fetch(name="windows_auth", folder="Mobile Users")
print(f"Found authentication settings: {auth_settings.name}")
```

### Create Authentication Settings

```python
# Windows authentication settings
auth_settings_config = {
    "name": "windows_auth",
    "authentication_profile": "windows-sso-profile",
    "os": "Windows",
    "user_credential_or_client_cert_required": True,
    "folder": "Mobile Users"
}
new_auth_settings = client.auth_setting.create(auth_settings_config)

# iOS authentication settings
ios_auth_config = {
    "name": "ios_auth",
    "authentication_profile": "mobile-cert-auth",
    "os": "iOS",
    "user_credential_or_client_cert_required": False,
    "folder": "Mobile Users"
}
ios_auth_settings = client.auth_setting.create(ios_auth_config)
```

### Update Authentication Settings

```python
existing = client.auth_setting.fetch(name="windows_auth", folder="Mobile Users")

existing.name = "windows_auth_updated"
existing.authentication_profile = "updated-profile"
existing.user_credential_or_client_cert_required = False

updated_settings = client.auth_setting.update(existing.id, existing.model_dump(exclude_unset=True))
```

### Move Authentication Settings

Settings are evaluated top to bottom. Use `move()` to control evaluation order.

```python
# Move to top
client.auth_setting.move({"name": "windows_auth", "where": "top"})

# Move to bottom
client.auth_setting.move({"name": "android_auth", "where": "bottom"})

# Move before another entry
client.auth_setting.move({
    "name": "ios_auth",
    "where": "before",
    "destination": "android_auth"
})

# Move after another entry
client.auth_setting.move({
    "name": "browser_auth",
    "where": "after",
    "destination": "ios_auth"
})
```

### Delete Authentication Settings

```python
auth_settings = client.auth_setting.fetch(name="windows_auth", folder="Mobile Users")
client.auth_setting.delete(auth_settings.id)
```

### Get Authentication Settings by ID

```python
auth_settings_by_id = client.auth_setting.get(auth_settings.id)
print(f"Retrieved: {auth_settings_by_id.name}")
```

## Use Cases

### Committing Changes

```python
result = client.commit(
    folders=["Mobile Users"],
    description="Updated GlobalProtect authentication settings",
    sync=True,
    timeout=300
)
print(f"Commit job ID: {result.job_id}")
```

### Monitoring Jobs

```python
job_status = client.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

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
    ObjectNotPresentError
)

try:
    auth_settings_config = {
        "name": "windows_auth",
        "authentication_profile": "windows-sso-profile",
        "os": "Windows",
        "user_credential_or_client_cert_required": True,
        "folder": "Mobile Users"
    }
    new_auth_settings = client.auth_setting.create(auth_settings_config)
    result = client.commit(
        folders=["Mobile Users"],
        description="Added GlobalProtect authentication settings",
        sync=True
    )
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

## Related Topics

- [Authentication Settings Models](../../models/mobile_agent/auth_settings_models.md#Overview)
- [Mobile Agent Overview](index.md)
- [API Client](../../client.md)
- [Full Example Scripts](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/mobile_agent/auth_settings.py)
