# WildFire Antivirus Profile Configuration Object

Manages WildFire antivirus profiles for malware analysis and threat detection in Palo Alto Networks Strata Cloud Manager.

## Class Overview

The `WildfireAntivirusProfile` class inherits from `BaseObject` and provides CRUD operations for WildFire antivirus profiles that define malware analysis settings, file inspection rules, and threat detection configurations.

### Methods

| Method     | Description                    | Parameters                              | Return Type                            |
|------------|--------------------------------|-----------------------------------------|----------------------------------------|
| `create()` | Creates a new profile          | `data: Dict[str, Any]`                  | `WildfireAvProfileResponseModel`       |
| `get()`    | Retrieves a profile by ID      | `object_id: str`                        | `WildfireAvProfileResponseModel`       |
| `update()` | Updates an existing profile    | `profile: WildfireAvProfileUpdateModel` | `WildfireAvProfileResponseModel`       |
| `delete()` | Deletes a profile              | `object_id: str`                        | `None`                                 |
| `list()`   | Lists profiles with filtering  | `folder: str`, `**filters`              | `List[WildfireAvProfileResponseModel]` |
| `fetch()`  | Gets profile by name/container | `name: str`, `folder: str`              | `WildfireAvProfileResponseModel`       |

### Model Attributes

| Attribute          | Type                                 | Required | Default | Description                               |
|--------------------|--------------------------------------|----------|---------|-------------------------------------------|
| `name`             | str                                  | Yes      | None    | Profile name. Pattern: `^[a-zA-Z0-9._-]+$` |
| `id`               | UUID                                 | Yes*     | None    | Unique identifier (*response/update only) |
| `description`      | str                                  | No       | None    | Profile description                       |
| `packet_capture`   | bool                                 | No       | False   | Enable packet capture                     |
| `rules`            | List[WildfireAvRuleBase]             | Yes      | None    | List of analysis rules                    |
| `mlav_exception`   | List[WildfireAvMlavExceptionEntry]   | No       | None    | MLAV exception entries                    |
| `threat_exception` | List[WildfireAvThreatExceptionEntry] | No       | None    | Threat exception entries                  |
| `folder`           | str                                  | No**     | None    | Folder location. Max 64 chars             |
| `snippet`          | str                                  | No**     | None    | Snippet location. Max 64 chars            |
| `device`           | str                                  | No**     | None    | Device location. Max 64 chars             |

\* Only required for response and update models
\** Exactly one container (`folder`, `snippet`, or `device`) must be provided for create operations

#### Rule Attributes

| Attribute     | Type                 | Required | Default   | Description                      |
|---------------|----------------------|----------|-----------|----------------------------------|
| `name`        | str                  | Yes      | None      | Rule name                        |
| `analysis`    | WildfireAvAnalysis   | No       | None      | Analysis type (public/private)   |
| `direction`   | WildfireAvDirection  | Yes      | None      | Traffic direction                |
| `application` | List[str]            | No       | ["any"]   | List of applications             |
| `file_type`   | List[str]            | No       | ["any"]   | List of file types               |

### Exceptions

| Exception                    | HTTP Code | Description                    |
|------------------------------|-----------|--------------------------------|
| `InvalidObjectError`         | 400       | Invalid profile data or format |
| `MissingQueryParameterError` | 400       | Missing required parameters    |
| `NameNotUniqueError`         | 409       | Profile name already exists    |
| `ObjectNotPresentError`      | 404       | Profile not found              |
| `ReferenceNotZeroError`      | 409       | Profile still referenced       |
| `AuthenticationError`        | 401       | Authentication failed          |
| `ServerError`                | 500       | Internal server error          |

### Basic Configuration

```python
from scm.client import ScmClient

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

profiles = client.wildfire_antivirus_profile
```

## Methods

### List WildFire Antivirus Profiles

```python
filtered_profiles = client.wildfire_antivirus_profile.list(
    folder='Texas',
    rules=['basic-rule', 'upload-rule']
)

for profile in filtered_profiles:
    print(f"Name: {profile.name}")
    for rule in profile.rules:
        print(f"  Rule: {rule.name}, Direction: {rule.direction}")
```

**Filtering responses:**

```python
exact_profiles = client.wildfire_antivirus_profile.list(
    folder='Texas',
    exact_match=True
)

combined_filters = client.wildfire_antivirus_profile.list(
    folder='Texas',
    exact_match=True,
    exclude_folders=['All'],
    exclude_snippets=['default'],
    exclude_devices=['DeviceA']
)
```

**Controlling pagination with max_limit:**

```python
client.wildfire_antivirus_profile.max_limit = 4000

all_profiles = client.wildfire_antivirus_profile.list(folder='Texas')
```

### Fetch a WildFire Antivirus Profile

```python
profile = client.wildfire_antivirus_profile.fetch(name="basic-profile", folder="Texas")
print(f"Found profile: {profile.name}")
```

### Create a WildFire Antivirus Profile

```python
# Basic profile
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
basic_profile_obj = client.wildfire_antivirus_profile.create(basic_profile)

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
advanced_profile_obj = client.wildfire_antivirus_profile.create(advanced_profile)
```

### Update a WildFire Antivirus Profile

```python
existing_profile = client.wildfire_antivirus_profile.fetch(name="basic-profile", folder="Texas")

existing_profile.description = "Updated profile description"
existing_profile.packet_capture = True
existing_profile.rules.append({
    "name": "new-rule",
    "direction": "both",
    "analysis": "public-cloud",
    "application": ["any"],
    "file_type": ["any"]
})

updated_profile = client.wildfire_antivirus_profile.update(existing_profile)
```

### Delete a WildFire Antivirus Profile

```python
client.wildfire_antivirus_profile.delete("123e4567-e89b-12d3-a456-426655440000")
```

### Get a WildFire Antivirus Profile by ID

```python
profile_by_id = client.wildfire_antivirus_profile.get(profile.id)
print(f"Retrieved profile: {profile_by_id.name}")
print(f"Number of rules: {len(profile_by_id.rules)}")
```

## Use Cases

### Committing Changes

```python
result = client.commit(
    folders=["Texas"],
    description="Updated WildFire profiles",
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
    new_profile = client.wildfire_antivirus_profile.create(profile_config)
    result = client.commit(
        folders=["Texas"],
        description="Added test profile",
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

- [WildFire Antivirus Profile Models](../../models/security_services/wildfire_antivirus_profile_models.md#Overview)
- [Security Services Overview](index.md)
- [API Client](../../client.md)
- [Full Example Scripts](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/security/wildfire_antivirus_profile.py)
