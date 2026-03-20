# DNS Security Profile Configuration Object

Manages DNS security profiles for protecting against DNS-based threats in Palo Alto Networks Strata Cloud Manager.

## Class Overview

The `DNSSecurityProfile` class inherits from `BaseObject` and provides CRUD operations for DNS security profiles that protect against DNS-based threats including botnet domains, malware, and phishing attempts.

### Methods

| Method     | Description                     | Parameters                               | Return Type                             |
|------------|---------------------------------|------------------------------------------|-----------------------------------------|
| `create()` | Creates a new profile           | `data: Dict[str, Any]`                   | `DNSSecurityProfileResponseModel`       |
| `get()`    | Retrieves a profile by ID       | `object_id: str`                         | `DNSSecurityProfileResponseModel`       |
| `update()` | Updates an existing profile     | `profile: DNSSecurityProfileUpdateModel` | `DNSSecurityProfileResponseModel`       |
| `delete()` | Deletes a profile               | `object_id: str`                         | `None`                                  |
| `list()`   | Lists profiles with filtering   | `folder: str`, `**filters`               | `List[DNSSecurityProfileResponseModel]` |
| `fetch()`  | Gets profile by name and folder | `name: str`, `folder: str`               | `DNSSecurityProfileResponseModel`       |

### Model Attributes

| Attribute        | Type              | Required | Default | Description                                                      |
|------------------|-------------------|----------|---------|------------------------------------------------------------------|
| `name`           | str               | Yes      | None    | Profile name. Pattern: `^[a-zA-Z0-9][a-zA-Z0-9_\-\.\s]*$`        |
| `id`             | UUID              | Yes*     | None    | Unique identifier (*response/update only)                        |
| `description`    | str               | No       | None    | Profile description                                              |
| `botnet_domains` | BotnetDomainsModel| No       | None    | Botnet domains configuration                                     |
| `folder`         | str               | No**     | None    | Folder location. Max 64 chars                                    |
| `snippet`        | str               | No**     | None    | Snippet location. Max 64 chars                                   |
| `device`         | str               | No**     | None    | Device location. Max 64 chars                                    |

\* Only required for response and update models
\** Exactly one container (`folder`, `snippet`, or `device`) must be provided for create operations

#### BotnetDomainsModel Attributes

| Attribute                 | Type                                | Required | Default | Description                    |
|---------------------------|-------------------------------------|----------|---------|--------------------------------|
| `dns_security_categories` | List[DNSSecurityCategoryEntryModel] | No       | None    | DNS security categories        |
| `lists`                   | List[ListEntryBaseModel]            | No       | None    | Lists of DNS domains           |
| `sinkhole`                | SinkholeSettingsModel               | No       | None    | DNS sinkhole settings          |
| `whitelist`               | List[WhitelistEntryModel]           | No       | None    | DNS security overrides         |

#### DNSSecurityCategoryEntryModel Attributes

| Attribute        | Type              | Required | Default   | Description                 |
|------------------|-------------------|----------|-----------|-----------------------------|
| `name`           | str               | Yes      | None      | DNS Security Category Name  |
| `action`         | ActionEnum        | No       | default   | Action to be taken          |
| `log_level`      | LogLevelEnum      | No       | default   | Log level                   |
| `packet_capture` | PacketCaptureEnum | No       | None      | Packet capture setting      |

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

profiles = client.dns_security_profile
```

## Methods

### List DNS Security Profiles

```python
filtered_profiles = client.dns_security_profile.list(
    folder='Texas',
    dns_security_categories=['pan-dns-sec-malware']
)

for profile in filtered_profiles:
    print(f"Name: {profile.name}")
    if profile.botnet_domains and profile.botnet_domains.dns_security_categories:
        for category in profile.botnet_domains.dns_security_categories:
            print(f"Category: {category.name}, Action: {category.action}")
```

**Filtering responses:**

```python
exact_profiles = client.dns_security_profile.list(
    folder='Texas',
    exact_match=True
)

combined_filters = client.dns_security_profile.list(
    folder='Texas',
    exact_match=True,
    exclude_folders=['All'],
    exclude_snippets=['default'],
    exclude_devices=['DeviceA']
)
```

**Controlling pagination with max_limit:**

```python
client.dns_security_profile.max_limit = 4000

all_profiles = client.dns_security_profile.list(folder='Texas')
```

### Fetch a DNS Security Profile

```python
profile = client.dns_security_profile.fetch(name="basic-profile", folder="Texas")
print(f"Found profile: {profile.name}")
```

### Create a DNS Security Profile

```python
# Basic profile with DNS security categories
basic_profile = {
    'name': 'basic-profile',
    'description': 'Basic DNS security profile',
    'botnet_domains': {
        'dns_security_categories': [
            {
                'name': 'pan-dns-sec-malware',
                'action': 'block',
                'log_level': 'high',
                'packet_capture': 'single-packet'
            }
        ]
    },
    'folder': 'Texas'
}
basic_profile_obj = client.dns_security_profile.create(basic_profile)

# Advanced profile with sinkhole and whitelist
advanced_profile = {
    'name': 'advanced-profile',
    'description': 'Advanced DNS security profile',
    'botnet_domains': {
        'dns_security_categories': [
            {
                'name': 'pan-dns-sec-malware',
                'action': 'sinkhole',
                'log_level': 'high'
            },
            {
                'name': 'pan-dns-sec-phishing',
                'action': 'block',
                'log_level': 'critical'
            }
        ],
        'sinkhole': {
            'ipv4_address': 'pan-sinkhole-default-ip',
            'ipv6_address': '::1'
        },
        'whitelist': [
            {
                'name': 'trusted.example.com',
                'description': 'Trusted domain'
            }
        ]
    },
    'folder': 'Texas'
}
advanced_profile_obj = client.dns_security_profile.create(advanced_profile)
```

### Update a DNS Security Profile

```python
existing_profile = client.dns_security_profile.fetch(name="basic-profile", folder="Texas")

existing_profile.description = "Updated DNS security profile"
existing_profile.botnet_domains.dns_security_categories.append({
    'name': 'pan-dns-sec-grayware',
    'action': 'block',
    'log_level': 'high'
})

updated_profile = client.dns_security_profile.update(existing_profile)
```

### Delete a DNS Security Profile

```python
client.dns_security_profile.delete("123e4567-e89b-12d3-a456-426655440000")
```

### Get a DNS Security Profile by ID

```python
profile_by_id = client.dns_security_profile.get(profile.id)
print(f"Retrieved profile: {profile_by_id.name}")
print(f"Categories: {profile_by_id.botnet_domains.dns_security_categories}")
```

## Use Cases

### Committing Changes

```python
result = client.commit(
    folders=["Texas"],
    description="Updated DNS security profiles",
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
        "description": "Test DNS security profile",
        "botnet_domains": {
            "dns_security_categories": [
                {
                    "name": "pan-dns-sec-malware",
                    "action": "block",
                    "log_level": "high"
                }
            ]
        },
        "folder": "Texas"
    }
    new_profile = client.dns_security_profile.create(profile_config)
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

- [DNS Security Profile Models](../../models/security_services/dns_security_profile_models.md#Overview)
- [Security Services Overview](index.md)
- [API Client](../../client.md)
- [Full Example Scripts](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/security/dns_security_profile.py)
