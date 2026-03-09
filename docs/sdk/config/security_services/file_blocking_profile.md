# File Blocking Profile Configuration Object

Manages file blocking profiles for controlling file transfers in Palo Alto Networks Strata Cloud Manager.

## Class Overview

The `FileBlockingProfile` class inherits from `BaseObject` and provides CRUD operations for file blocking profiles that define policies for controlling file transfers based on application, direction, and file type.

### Methods

| Method     | Description                    | Parameters                                    | Return Type                              |
|------------|--------------------------------|-----------------------------------------------|------------------------------------------|
| `create()` | Creates a new profile          | `data: Dict[str, Any]`                        | `FileBlockingProfileResponseModel`       |
| `get()`    | Retrieves a profile by ID      | `object_id: str`                              | `FileBlockingProfileResponseModel`       |
| `update()` | Updates an existing profile    | `profile: FileBlockingProfileUpdateModel`     | `FileBlockingProfileResponseModel`       |
| `delete()` | Deletes a profile              | `object_id: str`                              | `None`                                   |
| `list()`   | Lists profiles with filtering  | `folder: str`, `**filters`                    | `List[FileBlockingProfileResponseModel]` |
| `fetch()`  | Gets profile by name/container | `name: str`, `folder: str`                    | `FileBlockingProfileResponseModel`       |

### Model Attributes

| Attribute     | Type                   | Required | Default | Description                               |
|---------------|------------------------|----------|---------|-------------------------------------------|
| `name`        | str                    | Yes      | None    | Profile name                              |
| `id`          | UUID                   | Yes*     | None    | Unique identifier (*response/update only) |
| `description` | str                    | No       | None    | Profile description                       |
| `rules`       | List[FileBlockingRule] | No       | None    | List of file blocking rules               |
| `folder`      | str                    | No**     | None    | Folder location. Max 64 chars             |
| `snippet`     | str                    | No**     | None    | Snippet location. Max 64 chars            |
| `device`      | str                    | No**     | None    | Device location. Max 64 chars             |

\* Only required for update and response models
\** Exactly one container (`folder`, `snippet`, or `device`) must be provided for create operations

### Exceptions

| Exception                    | HTTP Code | Description                     |
|------------------------------|-----------|---------------------------------|
| `InvalidObjectError`         | 400       | Invalid profile data or format  |
| `MissingQueryParameterError` | 400       | Missing required parameters     |
| `NameNotUniqueError`         | 409       | Profile name already exists     |
| `ObjectNotPresentError`      | 404       | Profile not found               |
| `ReferenceNotZeroError`      | 409       | Profile still referenced        |
| `AuthenticationError`        | 401       | Authentication failed           |
| `ServerError`                | 500       | Internal server error           |

### Basic Configuration

```python
from scm.client import ScmClient

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

profiles = client.file_blocking_profile
```

## Methods

### List File Blocking Profiles

```python
filtered_profiles = client.file_blocking_profile.list(
    folder='Texas',
    rules=['block-dangerous']
)

for profile in filtered_profiles:
    print(f"Name: {profile.name}")
    if profile.rules:
        for rule in profile.rules:
            print(f"  - {rule.name}: {rule.action} ({rule.direction})")
```

**Filtering responses:**

```python
exact_profiles = client.file_blocking_profile.list(
    folder='Texas',
    exact_match=True
)

combined_filters = client.file_blocking_profile.list(
    folder='Texas',
    exact_match=True,
    exclude_folders=['All'],
    exclude_snippets=['default'],
    exclude_devices=['DeviceA']
)
```

**Controlling pagination with max_limit:**

```python
client.file_blocking_profile.max_limit = 4000

all_profiles = client.file_blocking_profile.list(folder='Texas')
```

### Fetch a File Blocking Profile

```python
profile = client.file_blocking_profile.fetch(name="basic-file-blocking", folder="Texas")
print(f"Found profile: {profile.name}")
```

### Create a File Blocking Profile

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
strict_profile_obj = client.file_blocking_profile.create(block_profile)
```

### Update a File Blocking Profile

```python
existing_profile = client.file_blocking_profile.fetch(name="basic-file-blocking", folder="Texas")

existing_profile.description = "Updated file blocking profile"
existing_profile.rules.append({
    "name": "block-scripts",
    "action": "block",
    "application": ["any"],
    "direction": "both",
    "file_type": ["js", "vbs", "ps1"]
})

updated_profile = client.file_blocking_profile.update(existing_profile)
```

### Delete a File Blocking Profile

```python
client.file_blocking_profile.delete("123e4567-e89b-12d3-a456-426655440000")
```

### Get a File Blocking Profile by ID

```python
profile_by_id = client.file_blocking_profile.get(profile.id)
print(f"Retrieved profile: {profile_by_id.name}")
print(f"Number of rules: {len(profile_by_id.rules)}")
```

## Use Cases

### Committing Changes

```python
result = client.commit(
    folders=["Texas"],
    description="Updated file blocking profiles",
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
    ObjectNotPresentError,
    ReferenceNotZeroError
)

try:
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
    new_profile = client.file_blocking_profile.create(profile_config)
    result = client.commit(
        folders=["Texas"],
        description="Added file blocking profile",
        sync=True
    )
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

## Related Topics

- [File Blocking Profile Models](../../models/security_services/file_blocking_profile_models.md#Overview)
- [Security Services Overview](index.md)
- [API Client](../../client.md)
- [Full Example Scripts](https://github.com/cdot65/pan-scm-sdk/tree/main/examples/scm/config/security_services/)
