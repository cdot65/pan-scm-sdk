# IKE Crypto Profile Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [IKE Crypto Profile Model Attributes](#ike-crypto-profile-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating IKE Crypto Profiles](#creating-ike-crypto-profiles)
    - [Retrieving IKE Crypto Profiles](#retrieving-ike-crypto-profiles)
    - [Updating IKE Crypto Profiles](#updating-ike-crypto-profiles)
    - [Listing IKE Crypto Profiles](#listing-ike-crypto-profiles)
    - [Filtering Responses](#filtering-responses)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Deleting IKE Crypto Profiles](#deleting-ike-crypto-profiles)
7. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Full Script Examples](#full-script-examples)
11. [Related Models](#related-models)

## Overview

The `IKECryptoProfile` class provides functionality to manage IKE (Internet Key Exchange) Crypto Profile objects in Palo Alto Networks' Strata Cloud Manager. This class inherits from `BaseObject` and provides methods for creating, retrieving, updating, and deleting IKE crypto profiles used for IPsec VPN tunnels.

IKE Crypto Profiles define:

- Hash algorithms for integrity validation
- Encryption algorithms for data confidentiality
- Diffie-Hellman groups for secure key exchange
- Lifetime settings for security key rotation

## Core Methods

| Method     | Description                           | Parameters                                              | Return Type                      |
|------------|---------------------------------------|---------------------------------------------------------|----------------------------------|
| `create()` | Creates a new IKE crypto profile      | `data: Dict[str, Any]`                                  | `IKECryptoProfileResponseModel`  |
| `get()`    | Retrieves a profile by ID             | `object_id: str`                                        | `IKECryptoProfileResponseModel`  |
| `update()` | Updates an existing profile           | `profile: IKECryptoProfileUpdateModel`                  | `IKECryptoProfileResponseModel`  |
| `delete()` | Deletes a profile                     | `object_id: str`                                        | `None`                           |
| `list()`   | Lists profiles with filtering         | `folder: str`, `snippet: str`, `device: str`, `**filters` | `List[IKECryptoProfileResponseModel]` |
| `fetch()`  | Gets profile by name and container    | `name: str`, `folder: str`, `snippet: str`, `device: str` | `IKECryptoProfileResponseModel`  |

## IKE Crypto Profile Model Attributes

| Attribute                | Type                    | Required | Default | Description                                                    |
|--------------------------|-------------------------|----------|---------|----------------------------------------------------------------|
| `name`                   | str                     | Yes      | None    | Profile name. Max 31 chars. Pattern: `^[0-9a-zA-Z._-]+$`       |
| `id`                     | UUID                    | Yes*     | None    | Unique identifier (*response/update only)                      |
| `hash`                   | List[HashAlgorithm]     | Yes      | None    | Hashing algorithms                                             |
| `encryption`             | List[EncryptionAlgorithm] | Yes    | None    | Encryption algorithms                                          |
| `dh_group`               | List[DHGroup]           | Yes      | None    | Phase-1 DH groups                                              |
| `lifetime`               | LifetimeType            | No       | None    | Lifetime configuration (seconds, minutes, hours, or days)      |
| `authentication_multiple`| int                     | No       | 0       | IKEv2 SA reauthentication interval multiplier (0-50)           |
| `folder`                 | str                     | No**     | None    | Folder containing the profile. Max 64 chars                    |
| `snippet`                | str                     | No**     | None    | Snippet containing the profile. Max 64 chars                   |
| `device`                 | str                     | No**     | None    | Device containing the profile. Max 64 chars                    |

\* Only required for update and response models
\** Exactly one container field (folder/snippet/device) must be provided

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

The IKE Crypto Profile service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

### Unified Client Interface (Recommended)

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the IKE Crypto Profile service directly through the client
ike_profiles = client.ike_crypto_profile
```

### Traditional Service Instantiation (Legacy)

```python
from scm.client import Scm
from scm.config.network import IKECryptoProfile

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize IKECryptoProfile object explicitly
ike_profiles = IKECryptoProfile(client)
```

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

## Usage Examples

### Creating IKE Crypto Profiles

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Prepare IKE crypto profile configuration
profile_config = {
    "name": "ike-crypto-sha256-aes256",
    "hash": ["sha256", "sha384"],
    "encryption": ["aes-256-cbc", "aes-256-gcm"],
    "dh_group": ["group14", "group19", "group20"],
    "lifetime": {"hours": 8},
    "authentication_multiple": 3,
    "folder": "Texas"
}

# Create the IKE crypto profile
new_profile = client.ike_crypto_profile.create(profile_config)
print(f"Created IKE crypto profile: {new_profile.name} (ID: {new_profile.id})")
```

### Retrieving IKE Crypto Profiles

```python
# Fetch by name and folder
profile = client.ike_crypto_profile.fetch(
    name="ike-crypto-sha256-aes256",
    folder="Texas"
)
print(f"Found profile: {profile.name}")

# Get by ID
profile_by_id = client.ike_crypto_profile.get(profile.id)
print(f"Retrieved profile: {profile_by_id.name}")
```

### Updating IKE Crypto Profiles

```python
# Fetch existing profile
existing = client.ike_crypto_profile.fetch(
    name="ike-crypto-sha256-aes256",
    folder="Texas"
)

# Modify attributes using dot notation
existing.hash = ["sha384", "sha512"]
existing.encryption = ["aes-256-gcm"]
existing.lifetime = {"days": 1}

# Perform update
updated_profile = client.ike_crypto_profile.update(existing)
print(f"Updated profile: {updated_profile.name}")
```

### Listing IKE Crypto Profiles

```python
# List all profiles in a folder
profiles = client.ike_crypto_profile.list(folder="Texas")

# Process results
for profile in profiles:
    print(f"Profile: {profile.name}")
    print(f"  Hash: {[h.value for h in profile.hash]}")
    print(f"  Encryption: {[e.value for e in profile.encryption]}")
    print(f"  DH Groups: {[g.value for g in profile.dh_group]}")
```

### Filtering Responses

The `list()` method supports additional filtering parameters:

```python
# List with exact match on container
profiles = client.ike_crypto_profile.list(
    folder="Texas",
    exact_match=True
)

# Exclude specific folders from results
profiles = client.ike_crypto_profile.list(
    folder="All",
    exclude_folders=["Shared", "Default"]
)

# Exclude specific snippets
profiles = client.ike_crypto_profile.list(
    folder="Texas",
    exclude_snippets=["default-snippet"]
)

# Exclude specific devices
profiles = client.ike_crypto_profile.list(
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
client.ike_crypto_profile.max_limit = 1000

# List all profiles - auto-paginates through results
all_profiles = client.ike_crypto_profile.list(folder="Texas")
```

### Deleting IKE Crypto Profiles

```python
# Get the profile to delete
profile = client.ike_crypto_profile.fetch(
    name="ike-crypto-sha256-aes256",
    folder="Texas"
)

# Delete by ID
client.ike_crypto_profile.delete(str(profile.id))
print(f"Deleted profile: {profile.name}")
```

## Managing Configuration Changes

### Performing Commits

```python
# Prepare commit parameters
commit_params = {
    "folders": ["Texas"],
    "description": "Updated IKE crypto profiles",
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
    # Create IKE crypto profile
    profile_config = {
        "name": "ike-crypto-test",
        "hash": ["sha256"],
        "encryption": ["aes-256-cbc"],
        "dh_group": ["group14"],
        "folder": "Texas"
    }

    new_profile = client.ike_crypto_profile.create(profile_config)

    # Commit changes
    result = client.commit(
        folders=["Texas"],
        description="Added IKE crypto profile",
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
    - Use the unified client interface (`client.ike_crypto_profile`) for streamlined code
    - Create a single client instance and reuse it across your application
    - Perform commit operations directly on the client object (`client.commit()`)

2. **Algorithm Selection**
    - Use strong hash algorithms (SHA-256 or higher) for security
    - Prefer AES-256 encryption for sensitive data
    - Use higher DH groups (group14, group19, group20) for better security
    - Avoid deprecated algorithms (MD5, DES, 3DES) in production

3. **Lifetime Configuration**
    - Set appropriate lifetimes based on security requirements
    - Shorter lifetimes provide better security but more overhead
    - Balance security needs with performance considerations

4. **Container Management**
    - Always specify exactly one container (folder, snippet, or device)
    - Use consistent folder structures across related configurations
    - Validate container existence before creating profiles

5. **Error Handling**
    - Implement comprehensive error handling for all operations
    - Check job status after commits
    - Handle specific exceptions before generic ones
    - Log error details for troubleshooting

## Full Script Examples

Refer to the [ike_crypto_profile.py example](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/network/ike_crypto_profile.py).

## Related Models

- [IKECryptoProfileBaseModel](../../models/network/ike_crypto_profile_models.md)
- [IKECryptoProfileCreateModel](../../models/network/ike_crypto_profile_models.md)
- [IKECryptoProfileUpdateModel](../../models/network/ike_crypto_profile_models.md)
- [IKECryptoProfileResponseModel](../../models/network/ike_crypto_profile_models.md)
- [HashAlgorithm](../../models/network/ike_crypto_profile_models.md)
- [EncryptionAlgorithm](../../models/network/ike_crypto_profile_models.md)
- [DHGroup](../../models/network/ike_crypto_profile_models.md)
- [LifetimeSeconds](../../models/network/ike_crypto_profile_models.md)
- [LifetimeMinutes](../../models/network/ike_crypto_profile_models.md)
- [LifetimeHours](../../models/network/ike_crypto_profile_models.md)
- [LifetimeDays](../../models/network/ike_crypto_profile_models.md)
