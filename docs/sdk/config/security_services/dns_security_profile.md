# DNS Security Profile Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [DNS Security Profile Model Attributes](#dns-security-profile-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating DNS Security Profiles](#creating-dns-security-profiles)
    - [Retrieving DNS Security Profiles](#retrieving-dns-security-profiles)
    - [Updating DNS Security Profiles](#updating-dns-security-profiles)
    - [Listing DNS Security Profiles](#listing-dns-security-profiles)
    - [Filtering Responses](#filtering-responses)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Deleting DNS Security Profiles](#deleting-dns-security-profiles)
7. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Full Script Examples](#full-script-examples)
11. [Related Models](#related-models)

## Overview

The `DNSSecurityProfile` class provides functionality to manage DNS Security profiles in Palo Alto Networks' Strata
Cloud Manager. This class inherits from `BaseObject` and provides methods for creating, retrieving, updating, and
deleting profiles that protect against DNS-based threats including botnet domains, malware, and phishing attempts.

## Core Methods

| Method     | Description                     | Parameters                               | Return Type                             |
|------------|---------------------------------|------------------------------------------|-----------------------------------------|
| `create()` | Creates a new profile           | `data: Dict[str, Any]`                   | `DNSSecurityProfileResponseModel`       |
| `get()`    | Retrieves a profile by ID       | `object_id: str`                         | `DNSSecurityProfileResponseModel`       |
| `update()` | Updates an existing profile     | `profile: DNSSecurityProfileUpdateModel` | `DNSSecurityProfileResponseModel`       |
| `delete()` | Deletes a profile               | `object_id: str`                         | `None`                                  |
| `list()`   | Lists profiles with filtering   | `folder: str`, `**filters`               | `List[DNSSecurityProfileResponseModel]` |
| `fetch()`  | Gets profile by name and folder | `name: str`, `folder: str`               | `DNSSecurityProfileResponseModel`       |

## DNS Security Profile Model Attributes

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
\** Exactly one container (folder/snippet/device) must be provided for create operations

### BotnetDomainsModel Attributes

| Attribute                 | Type                              | Required | Default | Description                    |
|---------------------------|-----------------------------------|----------|---------|--------------------------------|
| `dns_security_categories` | List[DNSSecurityCategoryEntryModel] | No     | None    | DNS security categories        |
| `lists`                   | List[ListEntryBaseModel]          | No       | None    | Lists of DNS domains           |
| `sinkhole`                | SinkholeSettingsModel             | No       | None    | DNS sinkhole settings          |
| `whitelist`               | List[WhitelistEntryModel]         | No       | None    | DNS security overrides         |

### DNSSecurityCategoryEntryModel Attributes

| Attribute        | Type              | Required | Default   | Description                 |
|------------------|-------------------|----------|-----------|-----------------------------|
| `name`           | str               | Yes      | None      | DNS Security Category Name  |
| `action`         | ActionEnum        | No       | default   | Action to be taken          |
| `log_level`      | LogLevelEnum      | No       | default   | Log level                   |
| `packet_capture` | PacketCaptureEnum | No       | None      | Packet capture setting      |

### SinkholeSettingsModel Attributes

| Attribute      | Type            | Required | Default | Description               |
|----------------|-----------------|----------|---------|---------------------------|
| `ipv4_address` | IPv4AddressEnum | Yes      | None    | IPv4 address for sinkhole |
| `ipv6_address` | IPv6AddressEnum | Yes      | None    | IPv6 address for sinkhole |

### WhitelistEntryModel Attributes

| Attribute     | Type | Required | Default | Description                        |
|---------------|------|----------|---------|------------------------------------|
| `name`        | str  | Yes      | None    | DNS domain or FQDN to be whitelisted |
| `description` | str  | No       | None    | Description                        |

## Exceptions

| Exception                    | HTTP Code | Description                    |
|------------------------------|-----------|--------------------------------|
| `InvalidObjectError`         | 400       | Invalid profile data or format |
| `MissingQueryParameterError` | 400       | Missing required parameters    |
| `NameNotUniqueError`         | 409       | Profile name already exists    |
| `ObjectNotPresentError`      | 404       | Profile not found              |
| `ReferenceNotZeroError`      | 409       | Profile still referenced       |
| `AuthenticationError`        | 401       | Authentication failed          |
| `ServerError`                | 500       | Internal server error          |

## Basic Configuration

The DNS Security Profile service can be accessed using the unified client interface (recommended):

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access DNS security profiles directly through the client
profiles = client.dns_security_profile
```

## Usage Examples

### Creating DNS Security Profiles

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

# Create basic profile using the client
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

# Create advanced profile
advanced_profile_obj = client.dns_security_profile.create(advanced_profile)
```

### Retrieving DNS Security Profiles

```python
# Fetch by name and folder
profile = client.dns_security_profile.fetch(name="basic-profile", folder="Texas")
print(f"Found profile: {profile.name}")

# Get by ID
profile_by_id = client.dns_security_profile.get(profile.id)
print(f"Retrieved profile: {profile_by_id.name}")
print(f"Categories: {profile_by_id.botnet_domains.dns_security_categories}")
```

### Updating DNS Security Profiles

```python
# Fetch existing profile
existing_profile = client.dns_security_profile.fetch(name="basic-profile", folder="Texas")

# Update description and categories
existing_profile.description = "Updated DNS security profile"
existing_profile.botnet_domains.dns_security_categories.append({
    'name': 'pan-dns-sec-grayware',
    'action': 'block',
    'log_level': 'high'
})

# Perform update
updated_profile = client.dns_security_profile.update(existing_profile)
```

### Listing DNS Security Profiles

```python
# List with direct filter parameters
filtered_profiles = client.dns_security_profile.list(
    folder='Texas',
    dns_security_categories=['pan-dns-sec-malware']
)

# Process results
for profile in filtered_profiles:
    print(f"Name: {profile.name}")
    if profile.botnet_domains and profile.botnet_domains.dns_security_categories:
        for category in profile.botnet_domains.dns_security_categories:
            print(f"Category: {category.name}, Action: {category.action}")

# Define filter parameters as dictionary
list_params = {
    "folder": "Texas",
    "dns_security_categories": ["pan-dns-sec-phishing", "pan-dns-sec-malware"]
}

# List with filters as kwargs
filtered_profiles = client.dns_security_profile.list(**list_params)
```

### Filtering Responses

The `list()` method supports additional parameters to refine your query results even further. Alongside basic filters
(like `types`, `values`, and `tags`), you can leverage the `exact_match`, `exclude_folders`, `exclude_snippets`, and
`exclude_devices` parameters to control which objects are included or excluded after the initial API response is fetched.

**Parameters:**

- `exact_match (bool)`: When `True`, only objects defined exactly in the specified container (`folder`, `snippet`, or `device`) are returned. Inherited or propagated objects are filtered out.
- `exclude_folders (List[str])`: Provide a list of folder names that you do not want included in the results.
- `exclude_snippets (List[str])`: Provide a list of snippet values to exclude from the results.
- `exclude_devices (List[str])`: Provide a list of device values to exclude from the results.

**Examples:**

```python
# Only return profiles defined exactly in 'Texas'
exact_profiles = client.dns_security_profile.list(
    folder='Texas',
    exact_match=True
)

for profile in exact_profiles:
    print(f"Exact match: {profile.name} in {profile.folder}")

# Exclude all profiles from the 'All' folder
no_all_profiles = client.dns_security_profile.list(
    folder='Texas',
    exclude_folders=['All']
)

for profile in no_all_profiles:
    assert profile.folder != 'All'
    print(f"Filtered out 'All': {profile.name}")

# Exclude profiles that come from 'default' snippet
no_default_snippet = client.dns_security_profile.list(
    folder='Texas',
    exclude_snippets=['default']
)

for profile in no_default_snippet:
    assert profile.snippet != 'default'
    print(f"Filtered out 'default' snippet: {profile.name}")

# Exclude profiles associated with 'DeviceA'
no_deviceA = client.dns_security_profile.list(
    folder='Texas',
    exclude_devices=['DeviceA']
)

for profile in no_deviceA:
    assert profile.device != 'DeviceA'
    print(f"Filtered out 'DeviceA': {profile.name}")

# Combine exact_match with multiple exclusions
combined_filters = client.dns_security_profile.list(
    folder='Texas',
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

# Configure max_limit using the property setter
client.dns_security_profile.max_limit = 4000

# List all profiles - auto-paginates through results
all_profiles = client.dns_security_profile.list(folder='Texas')

# The profiles are fetched in chunks according to the max_limit setting.
```

### Deleting DNS Security Profiles

```python
# Delete by ID
profile_id = "123e4567-e89b-12d3-a456-426655440000"
client.dns_security_profile.delete(profile_id)
```

## Managing Configuration Changes

### Performing Commits

```python
# Prepare commit parameters
commit_params = {
    "folders": ["Texas"],
    "description": "Updated DNS security profiles",
    "sync": True,
    "timeout": 300  # 5 minute timeout
}

# Commit the changes directly using the client
result = client.commit(**commit_params)

print(f"Commit job ID: {result.job_id}")
```

### Monitoring Jobs

```python
# Get status of specific job using the client
job_status = client.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

# List recent jobs using the client
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
    # Create profile configuration
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

    # Create the profile using the client
    new_profile = client.dns_security_profile.create(profile_config)

    # Commit changes using the client
    result = client.commit(
        folders=["Texas"],
        description="Added test profile",
        sync=True
    )

    # Check job status using the client
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

1. **Profile Configuration**
    - Use descriptive profile names
    - Configure appropriate actions per category
    - Document security decisions
    - Maintain whitelist entries
    - Review sinkhole settings

2. **Container Management**
    - Always specify exactly one container
    - Use consistent container names
    - Validate container existence
    - Group related profiles

3. **Client Usage**
    - Use the unified client interface (`client.dns_security_profile`) for simpler code
    - Perform commits directly on the client (`client.commit()`)
    - Monitor jobs using client methods (`client.get_job_status()`, `client.list_jobs()`)
    - Initialize the client once and reuse across different object types

4. **Performance**
    - Use appropriate pagination
    - Cache frequently accessed profiles
    - Implement proper retry logic
    - Monitor commit operations

5. **Error Handling**
    - Validate input data
    - Handle specific exceptions
    - Log error details
    - Monitor job status
    - Track completion status

## Full Script Examples

Refer to
the [dns_security_profile.py example](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/security/dns_security_profile.py).

## Related Models

- [DNSSecurityProfileBaseModel](../../models/security_services/dns_security_profile_models.md#Overview)
- [DNSSecurityProfileCreateModel](../../models/security_services/dns_security_profile_models.md#Overview)
- [DNSSecurityProfileUpdateModel](../../models/security_services/dns_security_profile_models.md#Overview)
- [DNSSecurityProfileResponseModel](../../models/security_services/dns_security_profile_models.md#Overview)
- [BotnetDomainsModel](../../models/security_services/dns_security_profile_models.md#Overview)
- [DNSSecurityCategoryEntryModel](../../models/security_services/dns_security_profile_models.md#Overview)
- [ListEntryBaseModel](../../models/security_services/dns_security_profile_models.md#Overview)
- [SinkholeSettingsModel](../../models/security_services/dns_security_profile_models.md#Overview)
- [WhitelistEntryModel](../../models/security_services/dns_security_profile_models.md#Overview)
- [ActionEnum](../../models/security_services/dns_security_profile_models.md#Overview)
- [LogLevelEnum](../../models/security_services/dns_security_profile_models.md#Overview)
- [PacketCaptureEnum](../../models/security_services/dns_security_profile_models.md#Overview)
- [IPv4AddressEnum](../../models/security_services/dns_security_profile_models.md#Overview)
- [IPv6AddressEnum](../../models/security_services/dns_security_profile_models.md#Overview)
