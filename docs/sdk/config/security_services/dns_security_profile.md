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

| Attribute                 | Type                 | Required | Description                                 |
|---------------------------|----------------------|----------|---------------------------------------------|
| `name`                    | str                  | Yes      | Profile name (max 63 chars)                 |
| `id`                      | UUID                 | Yes*     | Unique identifier (*response only)          |
| `description`             | str                  | No       | Profile description                         |
| `botnet_domains`          | BotnetDomainsModel   | No       | Botnet domains configuration                |
| `dns_security_categories` | List[CategoryEntry]  | No       | DNS security category settings              |
| `lists`                   | List[ListEntry]      | No       | Custom domain lists                         |
| `sinkhole`                | SinkholeSettings     | No       | Sinkhole configuration                      |
| `whitelist`               | List[WhitelistEntry] | No       | Whitelisted domains                         |
| `folder`                  | str                  | Yes**    | Folder location (**one container required)  |
| `snippet`                 | str                  | Yes**    | Snippet location (**one container required) |
| `device`                  | str                  | Yes**    | Device location (**one container required)  |

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

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.security import DNSSecurityProfile

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize DNS Security Profile object
dns_security_profiles = DNSSecurityProfile(client)
```

</div>

## Usage Examples

### Creating DNS Security Profiles

<div class="termy">

<!-- termynal -->

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

# Create basic profile
basic_profile_obj = dns_security_profiles.create(basic_profile)

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
advanced_profile_obj = dns_security_profiles.create(advanced_profile)
```

</div>

### Retrieving DNS Security Profiles

<div class="termy">

<!-- termynal -->

```python
# Fetch by name and folder
profile = dns_security_profiles.fetch(name="basic-profile", folder="Texas")
print(f"Found profile: {profile.name}")

# Get by ID
profile_by_id = dns_security_profiles.get(profile.id)
print(f"Retrieved profile: {profile_by_id.name}")
print(f"Categories: {profile_by_id.botnet_domains.dns_security_categories}")
```

</div>

### Updating DNS Security Profiles

<div class="termy">

<!-- termynal -->

```python
# Fetch existing profile
existing_profile = dns_security_profiles.fetch(name="basic-profile", folder="Texas")

# Update description and categories
existing_profile.description = "Updated DNS security profile"
existing_profile.botnet_domains.dns_security_categories.append({
    'name': 'pan-dns-sec-grayware',
    'action': 'block',
    'log_level': 'high'
})

# Perform update
updated_profile = dns_security_profiles.update(existing_profile)
```

</div>

### Listing DNS Security Profiles

<div class="termy">

<!-- termynal -->

```python
# List with direct filter parameters
filtered_profiles = dns_security_profiles.list(
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
filtered_profiles = dns_security_profiles.list(**list_params)
```

</div>

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

<div class="termy">

<!-- termynal -->

```python
# Only return dns_security_profiles defined exactly in 'Texas'
exact_dns_security_profiles = dns_security_profiles.list(
    folder='Texas',
    exact_match=True
)

for app in exact_dns_security_profiles:
    print(f"Exact match: {app.name} in {app.folder}")

# Exclude all dns_security_profiles from the 'All' folder
no_all_dns_security_profiles = dns_security_profiles.list(
    folder='Texas',
    exclude_folders=['All']
)

for app in no_all_dns_security_profiles:
    assert app.folder != 'All'
    print(f"Filtered out 'All': {app.name}")

# Exclude dns_security_profiles that come from 'default' snippet
no_default_snippet = dns_security_profiles.list(
    folder='Texas',
    exclude_snippets=['default']
)

for app in no_default_snippet:
    assert app.snippet != 'default'
    print(f"Filtered out 'default' snippet: {app.name}")

# Exclude dns_security_profiles associated with 'DeviceA'
no_deviceA = dns_security_profiles.list(
    folder='Texas',
    exclude_devices=['DeviceA']
)

for app in no_deviceA:
    assert app.device != 'DeviceA'
    print(f"Filtered out 'DeviceA': {app.name}")

# Combine exact_match with multiple exclusions
combined_filters = dns_security_profiles.list(
    folder='Texas',
    exact_match=True,
    exclude_folders=['All'],
    exclude_snippets=['default'],
    exclude_devices=['DeviceA']
)

for app in combined_filters:
    print(f"Combined filters result: {app.name} in {app.folder}")
```

</div>

### Controlling Pagination with max_limit

The SDK supports pagination through the `max_limit` parameter, which defines how many objects are retrieved per API call. By default, `max_limit` is set to 2500. The API itself imposes a maximum allowed value of 5000. If you set `max_limit` higher than 5000, it will be capped to the API's maximum. The `list()` method will continue to iterate through all objects until all results have been retrieved. Adjusting `max_limit` can help manage retrieval performance and memory usage when working with large datasets.

<div class="termy">

<!-- termynal -->

```python
# Initialize the DNSSecurityProfile object with a custom max_limit
# This will retrieve up to 4321 objects per API call, up to the API limit of 5000.
profile_client = DNSSecurityProfile(api_client=client, max_limit=4321)

# Now when we call list(), it will use the specified max_limit for each request
# while auto-paginating through all available objects.
all_profiles = profile_client.list(folder='Texas')

# 'all_profiles' contains all objects from 'Texas', fetched in chunks of up to 4321 at a time.
```

</div>

### Deleting DNS Security Profiles

<div class="termy">

<!-- termynal -->

```python
# Delete by ID
profile_id = "123e4567-e89b-12d3-a456-426655440000"
dns_security_profiles.delete(profile_id)
```

</div>

## Managing Configuration Changes

### Performing Commits

<div class="termy">

<!-- termynal -->

```python
# Prepare commit parameters
commit_params = {
    "folders": ["Texas"],
    "description": "Updated DNS security profiles",
    "sync": True,
    "timeout": 300  # 5 minute timeout
}

# Commit the changes
result = dns_security_profiles.commit(**commit_params)

print(f"Commit job ID: {result.job_id}")
```

</div>

### Monitoring Jobs

<div class="termy">

<!-- termynal -->

```python
# Get status of specific job
job_status = dns_security_profiles.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

# List recent jobs
recent_jobs = dns_security_profiles.list_jobs(limit=10)
for job in recent_jobs.data:
    print(f"Job {job.id}: {job.type_str} - {job.status_str}")
```

</div>

## Error Handling

<div class="termy">

<!-- termynal -->

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

    # Create the profile
    new_profile = dns_security_profiles.create(profile_config)

    # Commit changes
    result = dns_security_profiles.commit(
        folders=["Texas"],
        description="Added test profile",
        sync=True
    )

    # Check job status
    status = dns_security_profiles.get_job_status(result.job_id)

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

</div>

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

3. **Security Categories**
    - Configure all relevant categories
    - Set appropriate log levels
    - Enable packet capture selectively
    - Review category actions regularly
    - Document exceptions

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

- [DNSSecurityProfileCreateModel](../../models/security_services/dns_security_profile_models.md#Overview)
- [DNSSecurityProfileUpdateModel](../../models/security_services/dns_security_profile_models.md#Overview)
- [DNSSecurityProfileResponseModel](../../models/security_services/dns_security_profile_models.md#Overview)