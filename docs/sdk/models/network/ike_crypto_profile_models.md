# IKE Crypto Profile Models

## Table of Contents

1. [Overview](#overview)
2. [Model Attributes](#model-attributes)
3. [Enum Types](#enum-types)
4. [Lifetime Models](#lifetime-models)
5. [Exceptions](#exceptions)
6. [Model Validators](#model-validators)
7. [Usage Examples](#usage-examples)

## Overview {#Overview}

The IKE Crypto Profile models provide data validation and serialization for IKE Crypto Profiles in Palo Alto Networks' Strata Cloud Manager. These models define encryption, authentication, and key exchange parameters used for IPsec VPN tunnels.

### Models

The module provides the following Pydantic models:

- `IKECryptoProfileBaseModel`: Base model with fields common to all IKE crypto profile operations
- `IKECryptoProfileCreateModel`: Model for creating new IKE crypto profiles
- `IKECryptoProfileUpdateModel`: Model for updating existing IKE crypto profiles
- `IKECryptoProfileResponseModel`: Response model for IKE crypto profile operations
- `LifetimeSeconds`: Model for lifetime in seconds
- `LifetimeMinutes`: Model for lifetime in minutes
- `LifetimeHours`: Model for lifetime in hours
- `LifetimeDays`: Model for lifetime in days
- `HashAlgorithm`: Enum for hash algorithm options
- `EncryptionAlgorithm`: Enum for encryption algorithm options
- `DHGroup`: Enum for Diffie-Hellman group options

All models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model.

## Model Attributes

| Attribute                | Type                       | Required | Default | Description                                                    |
|--------------------------|----------------------------|----------|---------|----------------------------------------------------------------|
| `name`                   | str                        | Yes      | None    | Profile name. Max 31 chars. Pattern: `^[0-9a-zA-Z._-]+$`       |
| `id`                     | UUID                       | Yes*     | None    | Unique identifier (*response/update only)                      |
| `hash`                   | List[HashAlgorithm]        | Yes      | None    | Hashing algorithms                                             |
| `encryption`             | List[EncryptionAlgorithm]  | Yes      | None    | Encryption algorithms                                          |
| `dh_group`               | List[DHGroup]              | Yes      | None    | Phase-1 DH groups                                              |
| `lifetime`               | LifetimeType               | No       | None    | Lifetime configuration (seconds, minutes, hours, or days)      |
| `authentication_multiple`| int                        | No       | 0       | IKEv2 SA reauthentication interval multiplier (0-50)           |
| `folder`                 | str                        | No**     | None    | Folder containing the profile. Max 64 chars                    |
| `snippet`                | str                        | No**     | None    | Snippet containing the profile. Max 64 chars                   |
| `device`                 | str                        | No**     | None    | Device containing the profile. Max 64 chars                    |

\* Only required for update and response models
\** Exactly one container field (folder/snippet/device) must be provided for create operations

## Enum Types

### HashAlgorithm

Defines the hash algorithm options for IKE crypto profiles:

| Value      | Description                    |
|------------|--------------------------------|
| `md5`      | MD5 hash (deprecated)          |
| `sha1`     | SHA-1 hash                     |
| `sha256`   | SHA-256 hash                   |
| `sha384`   | SHA-384 hash                   |
| `sha512`   | SHA-512 hash                   |
| `non-auth` | No authentication              |

### EncryptionAlgorithm

Defines the encryption algorithm options for IKE crypto profiles:

| Value         | Description                    |
|---------------|--------------------------------|
| `des`         | DES encryption (deprecated)    |
| `3des`        | Triple DES encryption          |
| `aes-128-cbc` | AES-128 CBC encryption         |
| `aes-192-cbc` | AES-192 CBC encryption         |
| `aes-256-cbc` | AES-256 CBC encryption         |
| `aes-128-gcm` | AES-128 GCM encryption         |
| `aes-256-gcm` | AES-256 GCM encryption         |

### DHGroup

Defines the Diffie-Hellman group options for IKE crypto profiles:

| Value     | Description                    |
|-----------|--------------------------------|
| `group1`  | DH Group 1 (768-bit)           |
| `group2`  | DH Group 2 (1024-bit)          |
| `group5`  | DH Group 5 (1536-bit)          |
| `group14` | DH Group 14 (2048-bit)         |
| `group19` | DH Group 19 (256-bit ECP)      |
| `group20` | DH Group 20 (384-bit ECP)      |

## Lifetime Models

IKE Crypto Profiles support four different lifetime units. Each has its own model with validation:

### LifetimeSeconds

| Attribute | Type | Required | Default | Description                         |
|-----------|------|----------|---------|-------------------------------------|
| `seconds` | int  | Yes      | None    | Lifetime in seconds (range: 180-65535) |

### LifetimeMinutes

| Attribute | Type | Required | Default | Description                         |
|-----------|------|----------|---------|-------------------------------------|
| `minutes` | int  | Yes      | None    | Lifetime in minutes (range: 3-65535) |

### LifetimeHours

| Attribute | Type | Required | Default | Description                         |
|-----------|------|----------|---------|-------------------------------------|
| `hours`   | int  | Yes      | None    | Lifetime in hours (range: 1-65535)  |

### LifetimeDays

| Attribute | Type | Required | Default | Description                         |
|-----------|------|----------|---------|-------------------------------------|
| `days`    | int  | Yes      | None    | Lifetime in days (range: 1-365)     |

### LifetimeType

A union type representing any of the lifetime models:

```python
LifetimeType = Union[LifetimeSeconds, LifetimeMinutes, LifetimeHours, LifetimeDays]
```

## Exceptions

The IKE Crypto Profile models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
    - When name doesn't match the required pattern `^[0-9a-zA-Z._-]+$`
    - When name exceeds 31 characters
    - When required fields (hash, encryption, dh_group) are not provided
    - When container validation fails (not exactly one of folder/snippet/device provided)
    - When authentication_multiple is outside range 0-50
    - When lifetime values are outside their valid ranges

## Model Validators

### Container Validation (Create Model)

The create model enforces that exactly one container field is provided:

```python
from scm.models.network import IKECryptoProfileCreateModel

# This will raise a validation error - no container provided
try:
    profile = IKECryptoProfileCreateModel(
        name="test-profile",
        hash=["sha256"],
        encryption=["aes-256-cbc"],
        dh_group=["group14"]
        # Missing folder, snippet, or device
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."

# This will raise a validation error - multiple containers provided
try:
    profile = IKECryptoProfileCreateModel(
        name="test-profile",
        hash=["sha256"],
        encryption=["aes-256-cbc"],
        dh_group=["group14"],
        folder="Texas",
        snippet="my-snippet"  # Can't have both
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."
```

### Lifetime Value Validation

Each lifetime model enforces valid ranges:

```python
from scm.models.network import LifetimeSeconds, LifetimeDays

# This will raise a validation error - seconds below minimum
try:
    lifetime = LifetimeSeconds(seconds=100)  # Minimum is 180
except ValueError as e:
    print(e)  # "Input should be greater than or equal to 180"

# This will raise a validation error - days above maximum
try:
    lifetime = LifetimeDays(days=400)  # Maximum is 365
except ValueError as e:
    print(e)  # "Input should be less than or equal to 365"
```

## Usage Examples

### Creating an IKE Crypto Profile

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary
profile_dict = {
    "name": "ike-crypto-strong",
    "hash": ["sha256", "sha384"],
    "encryption": ["aes-256-cbc", "aes-256-gcm"],
    "dh_group": ["group14", "group19"],
    "lifetime": {"hours": 8},
    "authentication_multiple": 3,
    "folder": "Texas"
}

response = client.ike_crypto_profile.create(profile_dict)
print(f"Created profile: {response.name} (ID: {response.id})")

# Using model directly
from scm.models.network import IKECryptoProfileCreateModel

profile_model = IKECryptoProfileCreateModel(
    name="ike-crypto-gcm",
    hash=["sha384"],
    encryption=["aes-256-gcm"],
    dh_group=["group19", "group20"],
    lifetime={"days": 1},
    folder="Texas"
)

payload = profile_model.model_dump(exclude_unset=True)
response = client.ike_crypto_profile.create(payload)
```

### Updating an IKE Crypto Profile

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Fetch existing profile
existing = client.ike_crypto_profile.fetch(
    name="ike-crypto-strong",
    folder="Texas"
)

# Modify attributes using dot notation
existing.hash = ["sha384", "sha512"]
existing.encryption = ["aes-256-gcm"]
existing.lifetime = {"days": 1}

# Pass modified object to update()
updated = client.ike_crypto_profile.update(existing)
print(f"Updated profile: {updated.name}")
```

### Working with Enums

```python
from scm.models.network import (
    HashAlgorithm,
    EncryptionAlgorithm,
    DHGroup,
)

# Using enum values in configuration
profile_config = {
    "name": "ike-crypto-enum-example",
    "hash": [HashAlgorithm.SHA256, HashAlgorithm.SHA384],
    "encryption": [
        EncryptionAlgorithm.AES_256_CBC,
        EncryptionAlgorithm.AES_256_GCM
    ],
    "dh_group": [DHGroup.GROUP14, DHGroup.GROUP19],
    "lifetime": {"hours": 8},
    "folder": "Texas"
}

response = client.ike_crypto_profile.create(profile_config)

# Checking enum values in response
if HashAlgorithm.SHA256 in response.hash:
    print("Profile uses SHA-256")

# Get string values from enums
hash_values = [h.value for h in response.hash]
print(f"Hash algorithms: {hash_values}")
```

### Handling Lifetime Configurations

```python
# Different lifetime options
seconds_lifetime = {"seconds": 28800}  # 8 hours in seconds (min: 180)
minutes_lifetime = {"minutes": 480}     # 8 hours in minutes (min: 3)
hours_lifetime = {"hours": 8}           # 8 hours (min: 1)
days_lifetime = {"days": 1}             # 1 day (max: 365)

# Create profile with specific lifetime
profile_config = {
    "name": "ike-crypto-daily",
    "hash": ["sha256"],
    "encryption": ["aes-256-cbc"],
    "dh_group": ["group14"],
    "lifetime": days_lifetime,
    "folder": "Texas"
}

response = client.ike_crypto_profile.create(profile_config)
```
