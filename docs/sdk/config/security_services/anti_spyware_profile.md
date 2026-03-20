# Anti-Spyware Profile Configuration Object

Manages anti-spyware profiles for threat detection and prevention in Palo Alto Networks Strata Cloud Manager.

## Class Overview

The `AntiSpywareProfile` class inherits from `BaseObject` and provides CRUD operations for anti-spyware profiles that define threat detection and prevention settings for spyware, command-and-control traffic, and other malicious activities.

### Methods

| Method     | Description                    | Parameters                               | Return Type                             |
|------------|--------------------------------|------------------------------------------|-----------------------------------------|
| `create()` | Creates a new profile          | `data: Dict[str, Any]`                   | `AntiSpywareProfileResponseModel`       |
| `get()`    | Retrieves a profile by ID      | `object_id: str`                         | `AntiSpywareProfileResponseModel`       |
| `update()` | Updates an existing profile    | `profile: AntiSpywareProfileUpdateModel` | `AntiSpywareProfileResponseModel`       |
| `delete()` | Deletes a profile              | `object_id: str`                         | `None`                                  |
| `list()`   | Lists profiles with filtering  | `folder: str`, `**filters`               | `List[AntiSpywareProfileResponseModel]` |
| `fetch()`  | Gets profile by name/container | `name: str`, `folder: str`               | `AntiSpywareProfileResponseModel`       |

### Model Attributes

| Attribute                     | Type                                       | Required | Default | Description                                                     |
|-------------------------------|--------------------------------------------|---------|---------|-----------------------------------------------------------------|
| `name`                        | str                                        | Yes      | None    | Profile name. Pattern: `^[a-zA-Z0-9][a-zA-Z0-9_\-. ]*$`         |
| `id`                          | UUID                                       | Yes*     | None    | Unique identifier (*response/update only)                       |
| `description`                 | str                                        | No       | None    | Profile description                                             |
| `cloud_inline_analysis`       | bool                                       | No       | False   | Enable cloud inline analysis                                    |
| `rules`                       | List[AntiSpywareRuleBaseModel]             | No       | None    | List of anti-spyware rules                                      |
| `threat_exception`            | List[AntiSpywareThreatExceptionBase]       | No       | None    | List of threat exceptions                                       |
| `mica_engine_spyware_enabled` | List[AntiSpywareMicaEngineSpywareEnabledEntry] | No   | None    | MICA engine spyware settings                                    |
| `inline_exception_edl_url`    | List[str]                                  | No       | None    | Inline exception EDL URLs                                       |
| `inline_exception_ip_address` | List[str]                                  | No       | None    | Inline exception IP addresses                                   |
| `folder`                      | str                                        | No**     | None    | Folder location. Max 64 chars                                   |
| `snippet`                     | str                                        | No**     | None    | Snippet location. Max 64 chars                                  |
| `device`                      | str                                        | No**     | None    | Device location. Max 64 chars                                   |

\* Only required for update and response models
\** Exactly one container (`folder`, `snippet`, or `device`) must be provided for create operations

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
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

profiles = client.anti_spyware_profile
```

## Methods

### List Anti-Spyware Profiles

```python
# List with direct filter parameters
filtered_profiles = client.anti_spyware_profile.list(
    folder='Texas',
    rules=['block-critical']
)

for profile in filtered_profiles:
    print(f"Name: {profile.name}")
    for rule in profile.rules:
        print(f"  - {rule.name}: {rule.category}")

# Define filter parameters as dictionary
list_params = {
    "folder": "Texas",
    "rules": ["critical-threats", "medium-threats"]
}
filtered_profiles = client.anti_spyware_profile.list(**list_params)
```

**Filtering responses:**

```python
# Only return profiles defined exactly in 'Texas'
exact_profiles = client.anti_spyware_profile.list(
    folder='Texas',
    exact_match=True
)

# Exclude all profiles from the 'All' folder
no_all_profiles = client.anti_spyware_profile.list(
    folder='Texas',
    exclude_folders=['All']
)

# Combine exact_match with multiple exclusions
combined_filters = client.anti_spyware_profile.list(
    folder='Texas',
    exact_match=True,
    exclude_folders=['All'],
    exclude_snippets=['default'],
    exclude_devices=['DeviceA']
)
```

**Controlling pagination with max_limit:**

```python
client.anti_spyware_profile.max_limit = 4000

all_profiles = client.anti_spyware_profile.list(folder='Texas')
```

### Fetch an Anti-Spyware Profile

```python
profile = client.anti_spyware_profile.fetch(name="basic-profile", folder="Texas")
print(f"Found profile: {profile.name}")
```

### Create an Anti-Spyware Profile

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
advanced_profile_obj = client.anti_spyware_profile.create(advanced_profile)
```

### Update an Anti-Spyware Profile

```python
existing_profile = client.anti_spyware_profile.fetch(name="basic-profile", folder="Texas")

existing_profile.description = "Updated basic profile"
existing_profile.cloud_inline_analysis = True
existing_profile.rules.append({
    "name": "new-rule",
    "severity": ["high"],
    "category": "spyware",
    "action": {"alert": {}}
})

updated_profile = client.anti_spyware_profile.update(existing_profile)
```

### Delete an Anti-Spyware Profile

```python
client.anti_spyware_profile.delete("123e4567-e89b-12d3-a456-426655440000")
```

### Get an Anti-Spyware Profile by ID

```python
profile_by_id = client.anti_spyware_profile.get(profile.id)
print(f"Retrieved profile: {profile_by_id.name}")
print(f"Number of rules: {len(profile_by_id.rules)}")
```

## Use Cases

### Committing Changes

```python
result = client.commit(
    folders=["Texas"],
    description="Updated anti-spyware profiles",
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
    new_profile = client.anti_spyware_profile.create(profile_config)
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

- [Anti-Spyware Profile Models](../../models/security_services/anti_spyware_profile_models.md#Overview)
- [Security Services Overview](index.md)
- [API Client](../../client.md)
- [Full Example Scripts](https://github.com/cdot65/pan-scm-sdk/tree/main/examples/scm/config/security_services/)
