# IPsec Crypto Profile Models

## Table of Contents

1. [Overview](#overview)
2. [Model Attributes](#model-attributes)
3. [Enum Types](#enum-types)
4. [Supporting Models](#supporting-models)
5. [Lifetime Models](#lifetime-models)
6. [Lifesize Models](#lifesize-models)
7. [Exceptions](#exceptions)
8. [Model Validators](#model-validators)
9. [Usage Examples](#usage-examples)

## Overview {#Overview}

The IPsec Crypto Profile models provide a structured way to manage IPsec crypto profile configurations in Palo Alto Networks' Strata Cloud Manager. These models support defining security protocols, encryption algorithms, authentication methods, and lifetime/lifesize settings for IPsec VPN tunnels. The models handle validation of inputs and outputs when interacting with the SCM API.

### Models

The module provides the following Pydantic models:

- `IPsecCryptoProfileBaseModel`: Base model with fields common to all IPsec crypto profile operations
- `IPsecCryptoProfileCreateModel`: Model for creating new IPsec crypto profiles
- `IPsecCryptoProfileUpdateModel`: Model for updating existing IPsec crypto profiles
- `IPsecCryptoProfileResponseModel`: Response model for IPsec crypto profile operations
- `EspConfig`: ESP (Encapsulating Security Payload) configuration model
- `AhConfig`: AH (Authentication Header) configuration model
- `LifetimeSeconds`: Lifetime in seconds model
- `LifetimeMinutes`: Lifetime in minutes model
- `LifetimeHours`: Lifetime in hours model
- `LifetimeDays`: Lifetime in days model
- `LifesizeKB`: Lifesize in kilobytes model
- `LifesizeMB`: Lifesize in megabytes model
- `LifesizeGB`: Lifesize in gigabytes model
- `LifesizeTB`: Lifesize in terabytes model
- `DhGroup`: Enum for Diffie-Hellman group options
- `EspEncryption`: Enum for ESP encryption algorithm options
- `EspAuthentication`: Enum for ESP authentication algorithm options
- `AhAuthentication`: Enum for AH authentication algorithm options

All models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model.

## Model Attributes

| Attribute  | Type           | Required | Default  | Description                                                |
|------------|----------------|----------|----------|------------------------------------------------------------|
| `name`     | str            | Yes      | None     | Profile name. Max 31 chars. Pattern: `^[0-9a-zA-Z._-]+$`   |
| `id`       | UUID           | Yes*     | None     | Unique identifier (*response/update only)                  |
| `dh_group` | DhGroup        | No       | group2   | Phase-2 DH group (PFS DH group)                            |
| `lifetime` | dict           | Yes      | None     | Lifetime configuration (seconds, minutes, hours, or days)  |
| `lifesize` | dict           | No       | None     | Lifesize configuration (kb, mb, gb, or tb)                 |
| `esp`      | EspConfig      | No*      | None     | ESP configuration (encryption and authentication)          |
| `ah`       | AhConfig       | No*      | None     | AH configuration (authentication only)                     |
| `folder`   | str            | No**     | None     | Folder containing the profile. Max 64 chars                |
| `snippet`  | str            | No**     | None     | Snippet containing the profile. Max 64 chars               |
| `device`   | str            | No**     | None     | Device containing the profile. Max 64 chars                |

\* Only required for update and response models
\* Exactly one of `esp` or `ah` must be provided
\** Exactly one container field (folder/snippet/device) must be provided for create operations

## Enum Types

### DhGroup

Defines the Diffie-Hellman group options for IPsec key exchange:

| Value     | Description                         |
|-----------|-------------------------------------|
| `no-pfs`  | No Perfect Forward Secrecy          |
| `group1`  | DH Group 1 (768-bit)                |
| `group2`  | DH Group 2 (1024-bit) - default     |
| `group5`  | DH Group 5 (1536-bit)               |
| `group14` | DH Group 14 (2048-bit)              |
| `group19` | DH Group 19 (256-bit ECP)           |
| `group20` | DH Group 20 (384-bit ECP)           |

### EspEncryption

Defines the ESP encryption algorithm options:

| Value         | Description                    |
|---------------|--------------------------------|
| `des`         | DES encryption (deprecated)    |
| `3des`        | Triple DES encryption          |
| `aes-128-cbc` | AES-128 CBC encryption         |
| `aes-192-cbc` | AES-192 CBC encryption         |
| `aes-256-cbc` | AES-256 CBC encryption         |
| `aes-128-gcm` | AES-128 GCM encryption         |
| `aes-256-gcm` | AES-256 GCM encryption         |
| `null`        | No encryption                  |

### EspAuthentication

Defines the ESP authentication algorithm options:

| Value    | Description                    |
|----------|--------------------------------|
| `md5`    | MD5 hash (deprecated)          |
| `sha1`   | SHA-1 hash                     |
| `sha256` | SHA-256 hash                   |
| `sha384` | SHA-384 hash                   |
| `sha512` | SHA-512 hash                   |

### AhAuthentication

Defines the AH authentication algorithm options:

| Value    | Description                    |
|----------|--------------------------------|
| `md5`    | MD5 hash (deprecated)          |
| `sha1`   | SHA-1 hash                     |
| `sha256` | SHA-256 hash                   |
| `sha384` | SHA-384 hash                   |
| `sha512` | SHA-512 hash                   |

## Supporting Models

### EspConfig Model

Encapsulating Security Payload (ESP) configuration:

| Attribute        | Type               | Required | Default | Description              |
|------------------|--------------------|----------|---------|--------------------------|
| `encryption`     | List[EspEncryption]| Yes      | None    | Encryption algorithms    |
| `authentication` | List[str]          | Yes      | None    | Authentication algorithms|

### AhConfig Model

Authentication Header (AH) configuration:

| Attribute        | Type                 | Required | Default | Description              |
|------------------|----------------------|----------|---------|--------------------------|
| `authentication` | List[AhAuthentication]| Yes     | None    | Authentication algorithms|

## Lifetime Models

IPsec Crypto Profiles support four different lifetime units. Each has its own model with validation:

### LifetimeSeconds

| Attribute | Type | Required | Default | Description                          |
|-----------|------|----------|---------|--------------------------------------|
| `seconds` | int  | Yes      | None    | Lifetime in seconds (range: 180-65535) |

### LifetimeMinutes

| Attribute | Type | Required | Default | Description                          |
|-----------|------|----------|---------|--------------------------------------|
| `minutes` | int  | Yes      | None    | Lifetime in minutes (range: 3-65535) |

### LifetimeHours

| Attribute | Type | Required | Default | Description                          |
|-----------|------|----------|---------|--------------------------------------|
| `hours`   | int  | Yes      | None    | Lifetime in hours (range: 1-65535)   |

### LifetimeDays

| Attribute | Type | Required | Default | Description                          |
|-----------|------|----------|---------|--------------------------------------|
| `days`    | int  | Yes      | None    | Lifetime in days (range: 1-365)      |

## Lifesize Models

IPsec Crypto Profiles support four different lifesize units. Each has its own model with validation:

### LifesizeKB

| Attribute | Type | Required | Default | Description                          |
|-----------|------|----------|---------|--------------------------------------|
| `kb`      | int  | Yes      | None    | Lifesize in kilobytes (range: 1-65535) |

### LifesizeMB

| Attribute | Type | Required | Default | Description                          |
|-----------|------|----------|---------|--------------------------------------|
| `mb`      | int  | Yes      | None    | Lifesize in megabytes (range: 1-65535) |

### LifesizeGB

| Attribute | Type | Required | Default | Description                          |
|-----------|------|----------|---------|--------------------------------------|
| `gb`      | int  | Yes      | None    | Lifesize in gigabytes (range: 1-65535) |

### LifesizeTB

| Attribute | Type | Required | Default | Description                          |
|-----------|------|----------|---------|--------------------------------------|
| `tb`      | int  | Yes      | None    | Lifesize in terabytes (range: 1-65535) |

## Exceptions

The IPsec Crypto Profile models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
    - When name doesn't match the required pattern `^[0-9a-zA-Z._-]+$`
    - When name exceeds 31 characters
    - When both ESP and AH are configured (only one allowed)
    - When neither ESP nor AH is configured (one required)
    - When container validation fails (not exactly one of folder/snippet/device provided)
    - When lifetime values are outside their valid ranges
    - When lifesize values are outside their valid ranges

## Model Validators

### Security Protocol Validation

The models enforce that exactly one security protocol (ESP or AH) must be configured:

```python
from scm.models.network.ipsec_crypto_profile import IPsecCryptoProfileCreateModel

# This will raise a validation error - both protocols provided
try:
    profile = IPsecCryptoProfileCreateModel(
        name="test-profile",
        lifetime={"hours": 8},
        esp={"encryption": ["aes-256-cbc"], "authentication": ["sha256"]},
        ah={"authentication": ["sha512"]},  # Can't have both
        folder="Texas"
    )
except ValueError as e:
    print(e)  # "Only one security protocol (ESP or AH) can be configured at a time"

# This will raise a validation error - no protocol provided
try:
    profile = IPsecCryptoProfileCreateModel(
        name="test-profile",
        lifetime={"hours": 8},
        # Missing esp or ah
        folder="Texas"
    )
except ValueError as e:
    print(e)  # "At least one security protocol (ESP or AH) must be configured"
```

### Container Type Validation

For create operations, exactly one container type must be specified:

```python
from scm.models.network.ipsec_crypto_profile import IPsecCryptoProfileCreateModel

# This will raise a validation error - multiple containers specified
try:
    profile = IPsecCryptoProfileCreateModel(
        name="test-profile",
        lifetime={"hours": 8},
        esp={"encryption": ["aes-256-cbc"], "authentication": ["sha256"]},
        folder="Texas",
        device="fw01"  # Can't specify both folder and device
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."
```

### Lifetime Value Validation

Each lifetime model enforces valid ranges:

```python
from scm.models.network.ipsec_crypto_profile import LifetimeSeconds, LifetimeDays

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

### Creating an ESP-based IPsec Crypto Profile

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary
esp_config = {
    "name": "esp-aes256-sha256",
    "dh_group": "group14",
    "lifetime": {"hours": 8},
    "lifesize": {"gb": 50},
    "esp": {
        "encryption": ["aes-256-cbc", "aes-256-gcm"],
        "authentication": ["sha256", "sha384"]
    },
    "folder": "Texas"
}

response = client.ipsec_crypto_profile.create(esp_config)
print(f"Created profile: {response.name} (ID: {response.id})")
```

### Creating an AH-based IPsec Crypto Profile

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary
ah_config = {
    "name": "ah-sha512",
    "dh_group": "group19",
    "lifetime": {"days": 1},
    "ah": {
        "authentication": ["sha512"]
    },
    "folder": "Texas"
}

response = client.ipsec_crypto_profile.create(ah_config)
print(f"Created profile: {response.name} (ID: {response.id})")
```

### Updating an IPsec Crypto Profile

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

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

# Pass modified object to update()
updated = client.ipsec_crypto_profile.update(existing)
print(f"Updated profile: {updated.name}")
```

### Working with Enums

```python
from scm.models.network.ipsec_crypto_profile import (
    DhGroup,
    EspEncryption,
)

# Using enum values in configuration
profile_config = {
    "name": "esp-enum-example",
    "dh_group": DhGroup.GROUP14.value,
    "lifetime": {"hours": 8},
    "esp": {
        "encryption": [EspEncryption.AES_256_CBC.value, EspEncryption.AES_256_GCM.value],
        "authentication": ["sha256"]
    },
    "folder": "Texas"
}

response = client.ipsec_crypto_profile.create(profile_config)

# Get string values from enums
print(f"DH Group: {DhGroup.GROUP14.value}")  # "group14"
print(f"Encryption: {EspEncryption.AES_256_GCM.value}")  # "aes-256-gcm"
```

### Handling Different Lifetime Configurations

```python
# Different lifetime options
seconds_lifetime = {"seconds": 28800}  # 8 hours in seconds (min: 180)
minutes_lifetime = {"minutes": 480}     # 8 hours in minutes (min: 3)
hours_lifetime = {"hours": 8}           # 8 hours (min: 1)
days_lifetime = {"days": 1}             # 1 day (max: 365)

# Create profile with specific lifetime
profile_config = {
    "name": "ipsec-crypto-daily",
    "lifetime": days_lifetime,
    "esp": {
        "encryption": ["aes-256-cbc"],
        "authentication": ["sha256"]
    },
    "folder": "Texas"
}

response = client.ipsec_crypto_profile.create(profile_config)
```

### Handling Different Lifesize Configurations

```python
# Different lifesize options
kb_lifesize = {"kb": 1024}    # 1 MB in kilobytes
mb_lifesize = {"mb": 100}     # 100 megabytes
gb_lifesize = {"gb": 10}      # 10 gigabytes
tb_lifesize = {"tb": 1}       # 1 terabyte

# Create profile with lifesize limit
profile_config = {
    "name": "ipsec-crypto-lifesize",
    "lifetime": {"hours": 8},
    "lifesize": gb_lifesize,
    "esp": {
        "encryption": ["aes-256-gcm"],
        "authentication": ["sha256"]
    },
    "folder": "Texas"
}

response = client.ipsec_crypto_profile.create(profile_config)
```
