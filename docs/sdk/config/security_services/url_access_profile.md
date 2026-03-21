# URL Access Profile Configuration Object

Manages URL access profiles for controlling website access by category in Palo Alto Networks Strata Cloud Manager.

## Class Overview

The `URLAccessProfile` class inherits from `BaseObject` and provides CRUD operations for URL access profiles that define URL filtering policies to control access to websites based on URL categories.

### Methods

| Method     | Description                    | Parameters                                 | Return Type                           |
|------------|--------------------------------|--------------------------------------------|---------------------------------------|
| `create()` | Creates a new profile          | `data: Dict[str, Any]`                     | `URLAccessProfileResponseModel`       |
| `get()`    | Retrieves a profile by ID      | `object_id: str`                           | `URLAccessProfileResponseModel`       |
| `update()` | Updates an existing profile    | `profile: URLAccessProfileUpdateModel`     | `URLAccessProfileResponseModel`       |
| `delete()` | Deletes a profile              | `object_id: str`                           | `None`                                |
| `list()`   | Lists profiles with filtering  | `folder: str`, `**filters`                 | `List[URLAccessProfileResponseModel]` |
| `fetch()`  | Gets profile by name/container | `name: str`, `folder: str`                 | `URLAccessProfileResponseModel`       |

### Model Attributes

| Attribute                | Type                  | Required | Default  | Description                                             |
|--------------------------|-----------------------|----------|----------|---------------------------------------------------------|
| `name`                   | str                   | Yes      | None     | Profile name                                            |
| `id`                     | UUID                  | Yes*     | None     | Unique identifier (*response/update only)               |
| `description`            | str                   | No       | None     | Profile description. Max 255 chars                      |
| `alert`                  | List[str]             | No       | None     | URL categories for alert action                         |
| `allow`                  | List[str]             | No       | None     | URL categories for allow action                         |
| `block`                  | List[str]             | No       | None     | URL categories for block action                         |
| `continue_`              | List[str]             | No       | None     | URL categories for continue action (alias: `continue`)  |
| `redirect`               | List[str]             | No       | None     | URL categories for redirect action                      |
| `cloud_inline_cat`       | bool                  | No       | None     | Enable cloud inline categorization                      |
| `local_inline_cat`       | bool                  | No       | None     | Enable local inline categorization                      |
| `credential_enforcement` | CredentialEnforcement | No       | None     | Credential enforcement settings                         |
| `mlav_category_exception`| List[str]             | No       | None     | MLAV category exceptions                                |
| `log_container_page_only`| bool                  | No       | None     | Log container page only                                 |
| `log_http_hdr_referer`   | bool                  | No       | None     | Log HTTP header referer                                 |
| `log_http_hdr_user_agent`| bool                  | No       | None     | Log HTTP header user agent                              |
| `log_http_hdr_xff`       | bool                  | No       | None     | Log HTTP header X-Forwarded-For                         |
| `safe_search_enforcement`| bool                  | No       | None     | Enable safe search enforcement                          |
| `folder`                 | str                   | No**     | None     | Folder location. Max 64 chars                           |
| `snippet`                | str                   | No**     | None     | Snippet location. Max 64 chars                          |
| `device`                 | str                   | No**     | None     | Device location. Max 64 chars                           |

\* Only required for update and response models
\** Exactly one container (`folder`, `snippet`, or `device`) must be provided for create operations

!!! note
    The `continue_` field uses a Python-safe name because `continue` is a reserved keyword. When passing data as a dictionary, you can use either `"continue_"` or `"continue"` (the field's alias) as the key.

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
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

profiles = client.url_access_profile
```

## Methods

### List URL Access Profiles

```python
all_profiles = client.url_access_profile.list(folder='Texas')

for profile in all_profiles:
    print(f"Name: {profile.name}")
    if profile.block:
        print(f"  Blocked categories: {len(profile.block)}")
    if profile.allow:
        print(f"  Allowed categories: {len(profile.allow)}")
```

**Filtering responses:**

```python
exact_profiles = client.url_access_profile.list(
    folder='Texas',
    exact_match=True
)

combined_filters = client.url_access_profile.list(
    folder='Texas',
    exact_match=True,
    exclude_folders=['All'],
    exclude_snippets=['default'],
    exclude_devices=['DeviceA']
)
```

**Controlling pagination with max_limit:**

```python
client.url_access_profile.max_limit = 4000

all_profiles = client.url_access_profile.list(folder='Texas')
```

### Fetch a URL Access Profile

```python
profile = client.url_access_profile.fetch(name="basic-url-filtering", folder="Texas")
print(f"Found profile: {profile.name}")
```

### Create a URL Access Profile

```python
# Basic URL access profile with category actions
basic_profile = {
    "name": "basic-url-filtering",
    "description": "Basic URL filtering profile",
    "folder": "Texas",
    "alert": ["news", "entertainment"],
    "allow": ["business-and-economy", "technology"],
    "block": ["malware", "phishing", "command-and-control"]
}
basic_profile_obj = client.url_access_profile.create(basic_profile)

# Advanced profile with credential enforcement
advanced_profile = {
    "name": "advanced-url-filtering",
    "description": "Advanced URL filtering with credential enforcement",
    "folder": "Texas",
    "allow": ["business-and-economy", "technology"],
    "block": ["malware", "phishing", "command-and-control", "grayware"],
    "alert": ["unknown", "newly-registered-domain"],
    "cloud_inline_cat": True,
    "safe_search_enforcement": True,
    "log_http_hdr_xff": True,
    "log_http_hdr_user_agent": True,
    "log_http_hdr_referer": True,
    "credential_enforcement": {
        "mode": {
            "domain_credentials": {}
        },
        "block": ["malware", "phishing"],
        "alert": ["unknown"]
    }
}
advanced_profile_obj = client.url_access_profile.create(advanced_profile)
```

### Update a URL Access Profile

```python
existing_profile = client.url_access_profile.fetch(name="basic-url-filtering", folder="Texas")

existing_profile.description = "Updated URL filtering profile"
existing_profile.block = ["malware", "phishing", "command-and-control", "grayware"]
existing_profile.safe_search_enforcement = True

updated_profile = client.url_access_profile.update(existing_profile)
```

### Delete a URL Access Profile

```python
client.url_access_profile.delete("123e4567-e89b-12d3-a456-426655440000")
```

### Get a URL Access Profile by ID

```python
profile_by_id = client.url_access_profile.get(profile.id)
print(f"Retrieved profile: {profile_by_id.name}")
print(f"Blocked categories: {profile_by_id.block}")
```

## Use Cases

### Committing Changes

```python
result = client.commit(
    folders=["Texas"],
    description="Updated URL access profiles",
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
        "name": "test-url-filtering",
        "description": "Test URL filtering profile",
        "folder": "Texas",
        "block": ["malware", "phishing"],
        "alert": ["unknown"],
        "allow": ["business-and-economy"]
    }
    new_profile = client.url_access_profile.create(profile_config)
    result = client.commit(
        folders=["Texas"],
        description="Added URL access profile",
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

- [URL Access Profile Models](../../models/security_services/url_access_profile_models.md#Overview)
- [Security Services Overview](index.md)
- [API Client](../../client.md)
- [Full Example Scripts](https://github.com/cdot65/pan-scm-sdk/tree/main/examples/scm/config/security_services/)
