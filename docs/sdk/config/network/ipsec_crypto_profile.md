# IPsec Crypto Profile Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [IPsec Crypto Profile Model Attributes](#ipsec-crypto-profile-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating IPsec Crypto Profiles](#creating-ipsec-crypto-profiles)
    - [Retrieving IPsec Crypto Profiles](#retrieving-ipsec-crypto-profiles)
    - [Updating IPsec Crypto Profiles](#updating-ipsec-crypto-profiles)
    - [Listing IPsec Crypto Profiles](#listing-ipsec-crypto-profiles)
    - [Filtering Responses](#filtering-responses)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Deleting IPsec Crypto Profiles](#deleting-ipsec-crypto-profiles)
7. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Related Models](#related-models)

## Overview

The `IPsecCryptoProfile` class provides functionality to manage IPsec Crypto Profile objects in Palo Alto Networks' Strata Cloud Manager. This class inherits from `BaseObject` and provides methods for creating, retrieving, updating, and deleting IPsec crypto profiles used for IPsec VPN tunnels.

IPsec Crypto Profiles define:

- Security protocols (ESP or AH)
- Encryption algorithms for data confidentiality
- Authentication algorithms for data integrity
- Diffie-Hellman groups for Perfect Forward Secrecy (PFS)
- Lifetime and lifesize settings for security key rotation

## Core Methods

| Method     | Description                              | Parameters                                | Return Type                        |
|------------|------------------------------------------|-------------------------------------------|-----------------------------------|
| `create()` | Creates a new IPsec crypto profile       | `data: Dict[str, Any]`                    | `IPsecCryptoProfileResponseModel` |
| `get()`    | Retrieves a profile by ID                | `object_id: str`                          | `IPsecCryptoProfileResponseModel` |
| `update()` | Updates an existing profile              | `profile: IPsecCryptoProfileUpdateModel`  | `IPsecCryptoProfileResponseModel` |
| `delete()` | Deletes a profile                        | `object_id: str`                          | `None`                            |
| `list()`   | Lists profiles with filtering            | `folder: str`, `**filters`                | `List[IPsecCryptoProfileResponseModel]` |
| `fetch()`  | Gets profile by name and container       | `name: str`, `folder: str`                | `IPsecCryptoProfileResponseModel` |

## IPsec Crypto Profile Model Attributes

| Attribute  | Type           | Required | Default  | Description                                                |
|------------|----------------|----------|----------|------------------------------------------------------------|
| `name`     | str            | Yes      | None     | Profile name. Max 31 chars. Pattern: `^[0-9a-zA-Z._-]+$`   |
| `id`       | UUID           | Yes*     | None     | Unique identifier (*response/update only)                  |
| `dh_group` | DhGroup        | No       | group2   | Phase-2 DH group (PFS DH group)                            |
| `lifetime` | LifetimeType   | Yes      | None     | Lifetime configuration (seconds, minutes, hours, or days)  |
| `lifesize` | LifesizeType   | No       | None     | Lifesize configuration (kb, mb, gb, or tb)                 |
| `esp`      | EspConfig      | No*      | None     | ESP configuration (encryption and authentication)          |
| `ah`       | AhConfig       | No*      | None     | AH configuration (authentication only)                     |
| `folder`   | str            | No**     | None     | Folder containing the profile. Max 64 chars                |
| `snippet`  | str            | No**     | None     | Snippet containing the profile. Max 64 chars               |
| `device`   | str            | No**     | None     | Device containing the profile. Max 64 chars                |

\* Only required for update and response models
\* Exactly one of `esp` or `ah` must be provided
\** Exactly one container field (folder/snippet/device) must be provided for create operations

## Exceptions

| Exception                    | HTTP Code | Description                            |
|------------------------------|-----------|----------------------------------------|
| `InvalidObjectError`         | 400       | Invalid profile data or format         |
| `MissingQueryParameterError` | 400       | Missing required parameters            |
| `NameNotUniqueError`         | 409       | Profile name already exists            |
| `ObjectNotPresentError`      | 404       | Profile not found                      |
| `AuthenticationError`        | 401       | Authentication failed                  |
| `ServerError`                | 500       | Internal server error                  |

## Basic Configuration

The IPsec Crypto Profile service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

### Unified Client Interface (Recommended)

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the IPsec Crypto Profile service directly through the client
ipsec_profiles = client.ipsec_crypto_profile
```

### Traditional Service Instantiation (Legacy)

```python
from scm.client import Scm
from scm.config.network import IPsecCryptoProfile

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize IPsecCryptoProfile object explicitly
ipsec_profiles = IPsecCryptoProfile(client)
```

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

## Usage Examples

### Creating IPsec Crypto Profiles

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Create ESP-based profile with AES-256 encryption
esp_config = {
    "name": "esp-aes256-sha256",
    "dh_group": "group14",
    "lifetime": {"hours": 8},
    "lifesize": {"gb": 20},
    "esp": {
        "encryption": ["aes-256-cbc"],
        "authentication": ["sha256"]
    },
    "folder": "Texas"
}

esp_profile = client.ipsec_crypto_profile.create(esp_config)
print(f"Created ESP profile: {esp_profile.name} (ID: {esp_profile.id})")

# Create AH-based profile (authentication only)
ah_config = {
    "name": "ah-sha512",
    "dh_group": "group19",
    "lifetime": {"days": 1},
    "ah": {
        "authentication": ["sha512"]
    },
    "folder": "Texas"
}

ah_profile = client.ipsec_crypto_profile.create(ah_config)
print(f"Created AH profile: {ah_profile.name} (ID: {ah_profile.id})")
```

### Retrieving IPsec Crypto Profiles

```python
# Fetch by name and folder
profile = client.ipsec_crypto_profile.fetch(
    name="esp-aes256-sha256",
    folder="Texas"
)
print(f"Found profile: {profile.name}")

# Get by ID
profile_by_id = client.ipsec_crypto_profile.get(profile.id)
print(f"Retrieved profile: {profile_by_id.name}")
```

### Updating IPsec Crypto Profiles

```python
# Fetch existing profile
existing = client.ipsec_crypto_profile.fetch(
    name="esp-aes256-sha256",
    folder="Texas"
)

# Modify attributes using dot notation
existing.dh_group = "group20"
existing.lifetime = {"hours": 24}
existing.esp = {
    "encryption": ["aes-256-gcm"],
    "authentication": ["sha384"]
}

# Perform update
updated_profile = client.ipsec_crypto_profile.update(existing)
print(f"Updated profile: {updated_profile.name}")
```

### Listing IPsec Crypto Profiles

```python
# List all profiles in a folder
profiles = client.ipsec_crypto_profile.list(folder="Texas")

# Process results
for profile in profiles:
    print(f"Profile: {profile.name}")
    print(f"  DH Group: {profile.dh_group}")
    if profile.esp:
        print(f"  ESP Encryption: {profile.esp.encryption}")
    if profile.ah:
        print(f"  AH Authentication: {profile.ah.authentication}")
```

### Filtering Responses

The `list()` method supports additional filtering parameters:

```python
# List with exact match on container
profiles = client.ipsec_crypto_profile.list(
    folder="Texas",
    exact_match=True
)

# Exclude specific folders from results
profiles = client.ipsec_crypto_profile.list(
    folder="All",
    exclude_folders=["Shared", "Default"]
)

# Exclude specific snippets
profiles = client.ipsec_crypto_profile.list(
    folder="Texas",
    exclude_snippets=["default-snippet"]
)

# Exclude specific devices
profiles = client.ipsec_crypto_profile.list(
    folder="Texas",
    exclude_devices=["DeviceA", "DeviceB"]
)
```

### Controlling Pagination with max_limit

The SDK supports pagination through the `max_limit` parameter, which defines how many objects are retrieved per API call. By default, `max_limit` is set to 2500. The API itself imposes a maximum allowed value of 5000.

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Configure max_limit using the property setter
client.ipsec_crypto_profile.max_limit = 1000

# List all profiles - auto-paginates through results
all_profiles = client.ipsec_crypto_profile.list(folder="Texas")
```

### Deleting IPsec Crypto Profiles

```python
# Get the profile to delete
profile = client.ipsec_crypto_profile.fetch(
    name="esp-aes256-sha256",
    folder="Texas"
)

# Delete by ID
client.ipsec_crypto_profile.delete(str(profile.id))
print(f"Deleted profile: {profile.name}")
```

## Managing Configuration Changes

### Performing Commits

```python
# Prepare commit parameters
commit_params = {
    "folders": ["Texas"],
    "description": "Updated IPsec crypto profiles",
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
    # Create IPsec crypto profile
    profile_config = {
        "name": "ipsec-crypto-test",
        "dh_group": "group14",
        "lifetime": {"hours": 8},
        "esp": {
            "encryption": ["aes-256-cbc"],
            "authentication": ["sha256"]
        },
        "folder": "Texas"
    }

    new_profile = client.ipsec_crypto_profile.create(profile_config)

    # Commit changes
    result = client.commit(
        folders=["Texas"],
        description="Added IPsec crypto profile",
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
except MissingQueryParameterError as e:
    print(f"Missing parameter: {e.message}")
```

## Best Practices

1. **Client Usage**
    - Use the unified client interface (`client.ipsec_crypto_profile`) for streamlined code
    - Create a single client instance and reuse it across your application
    - Perform commit operations directly on the client object (`client.commit()`)

2. **Security Protocol Selection**
    - Choose between ESP (Encapsulating Security Payload) or AH (Authentication Header) based on requirements
    - ESP provides both encryption and authentication
    - AH provides authentication only (no encryption)
    - Only one protocol can be configured per profile

3. **Algorithm Selection**
    - Use strong encryption algorithms (AES-256) for sensitive data
    - Prefer AES-GCM for modern deployments (provides both encryption and authentication)
    - Avoid deprecated algorithms (DES, 3DES, MD5) in production
    - Consider compatibility with connection endpoints

4. **DH Group Selection**
    - Higher DH group numbers provide stronger security but require more processing
    - `no-pfs` disables Perfect Forward Secrecy (not recommended)
    - Common choices: group14 (2048-bit), group19, group20 (NIST elliptic curves)

5. **Lifetime Configuration**
    - Configure appropriate lifetimes based on security requirements
    - Shorter lifetimes provide better security but more overhead
    - Balance security needs with performance considerations
    - Consider using lifesize in addition to lifetime for high-traffic tunnels

6. **Container Management**
    - Always specify exactly one container (folder, snippet, or device)
    - Use consistent folder structures across related configurations
    - Validate container existence before creating profiles

7. **Error Handling**
    - Implement comprehensive error handling for all operations
    - Check job status after commits
    - Handle specific exceptions before generic ones
    - Log error details for troubleshooting

## Related Models

- [IPsecCryptoProfileBaseModel](../../models/network/ipsec_crypto_profile_models.md#Overview)
- [IPsecCryptoProfileCreateModel](../../models/network/ipsec_crypto_profile_models.md#Overview)
- [IPsecCryptoProfileUpdateModel](../../models/network/ipsec_crypto_profile_models.md#Overview)
- [IPsecCryptoProfileResponseModel](../../models/network/ipsec_crypto_profile_models.md#Overview)
- [DhGroup](../../models/network/ipsec_crypto_profile_models.md#Overview)
- [EspEncryption](../../models/network/ipsec_crypto_profile_models.md#Overview)
- [EspAuthentication](../../models/network/ipsec_crypto_profile_models.md#Overview)
- [AhAuthentication](../../models/network/ipsec_crypto_profile_models.md#Overview)
- [EspConfig](../../models/network/ipsec_crypto_profile_models.md#Overview)
- [AhConfig](../../models/network/ipsec_crypto_profile_models.md#Overview)
- [LifetimeSeconds](../../models/network/ipsec_crypto_profile_models.md#Overview)
- [LifetimeMinutes](../../models/network/ipsec_crypto_profile_models.md#Overview)
- [LifetimeHours](../../models/network/ipsec_crypto_profile_models.md#Overview)
- [LifetimeDays](../../models/network/ipsec_crypto_profile_models.md#Overview)
- [LifesizeKB](../../models/network/ipsec_crypto_profile_models.md#Overview)
- [LifesizeMB](../../models/network/ipsec_crypto_profile_models.md#Overview)
- [LifesizeGB](../../models/network/ipsec_crypto_profile_models.md#Overview)
- [LifesizeTB](../../models/network/ipsec_crypto_profile_models.md#Overview)
