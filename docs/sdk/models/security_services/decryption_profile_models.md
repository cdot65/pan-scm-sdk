# Decryption Profile Models

## Table of Contents

1. [Overview](#overview)
2. [Model Attributes](#model-attributes)
3. [Enum Types](#enum-types)
4. [Supporting Models](#supporting-models)
5. [Exceptions](#exceptions)
6. [Model Validators](#model-validators)
7. [Usage Examples](#usage-examples)

## Overview {#Overview}

The Decryption Profile models provide a structured way to manage SSL/TLS decryption settings in Palo Alto Networks' Strata Cloud Manager. These models support configuring forward proxy, inbound proxy, and no-proxy SSL settings, as well as protocol-specific settings like allowed algorithms and TLS versions. The models handle validation of inputs and outputs when interacting with the SCM API.

### Models

The module provides the following Pydantic models:

- `DecryptionProfileBaseModel`: Base model with fields common to all profile operations
- `DecryptionProfileCreateModel`: Model for creating new decryption profiles
- `DecryptionProfileUpdateModel`: Model for updating existing decryption profiles
- `DecryptionProfileResponseModel`: Response model for decryption profile operations
- `SSLProtocolSettings`: Model for SSL protocol configuration
- `SSLForwardProxy`: Model for SSL forward proxy settings
- `SSLInboundProxy`: Model for SSL inbound proxy settings
- `SSLNoProxy`: Model for SSL no-proxy settings

All models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model.

## Model Attributes

### DecryptionProfileBaseModel

| Attribute             | Type                | Required | Default | Description                                                 |
|-----------------------|---------------------|----------|---------|-------------------------------------------------------------|
| name                  | str                 | Yes      | None    | Profile name. Pattern: `^[A-Za-z0-9][A-Za-z0-9_\-\.\s]*$`   |
| ssl_forward_proxy     | SSLForwardProxy     | No       | None    | SSL Forward Proxy settings                                  |
| ssl_inbound_proxy     | SSLInboundProxy     | No       | None    | SSL Inbound Proxy settings                                  |
| ssl_no_proxy          | SSLNoProxy          | No       | None    | SSL No Proxy settings                                       |
| ssl_protocol_settings | SSLProtocolSettings | No       | None    | SSL Protocol settings                                       |
| folder                | str                 | No**     | None    | Folder location. Max 64 chars                               |
| snippet               | str                 | No**     | None    | Snippet location. Max 64 chars                              |
| device                | str                 | No**     | None    | Device location. Max 64 chars                               |

\** Exactly one container (folder/snippet/device) must be provided for create operations

### DecryptionProfileCreateModel

Inherits all fields from `DecryptionProfileBaseModel` and enforces that **exactly one** of `folder`, `snippet`, or `device` is provided during creation.

### DecryptionProfileUpdateModel

Extends `DecryptionProfileBaseModel` by adding:

| Attribute | Type | Required | Default | Description                          |
|-----------|------|----------|---------|--------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the profile |

### DecryptionProfileResponseModel

Extends `DecryptionProfileBaseModel` by adding:

| Attribute | Type | Required | Default | Description                          |
|-----------|------|----------|---------|--------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the profile |

## Enum Types

### SSLVersion

Defines the SSL/TLS version options:

| Value    | Description          |
|----------|----------------------|
| `sslv3`  | SSL version 3        |
| `tls1-0` | TLS version 1.0      |
| `tls1-1` | TLS version 1.1      |
| `tls1-2` | TLS version 1.2      |
| `tls1-3` | TLS version 1.3      |
| `max`    | Maximum available    |

## Supporting Models

### SSLProtocolSettings

| Attribute                    | Type       | Required | Default  | Description                         |
|------------------------------|------------|----------|----------|-------------------------------------|
| min_version                  | SSLVersion | No       | tls1-0   | Minimum SSL/TLS version             |
| max_version                  | SSLVersion | No       | tls1-2   | Maximum SSL/TLS version             |
| auth_algo_md5                | bool       | No       | True     | Allow MD5 authentication            |
| auth_algo_sha1               | bool       | No       | True     | Allow SHA1 authentication           |
| auth_algo_sha256             | bool       | No       | True     | Allow SHA256 authentication         |
| auth_algo_sha384             | bool       | No       | True     | Allow SHA384 authentication         |
| enc_algo_3des                | bool       | No       | True     | Allow 3DES encryption               |
| enc_algo_aes_128_cbc         | bool       | No       | True     | Allow AES-128-CBC encryption        |
| enc_algo_aes_128_gcm         | bool       | No       | True     | Allow AES-128-GCM encryption        |
| enc_algo_aes_256_cbc         | bool       | No       | True     | Allow AES-256-CBC encryption        |
| enc_algo_aes_256_gcm         | bool       | No       | True     | Allow AES-256-GCM encryption        |
| enc_algo_chacha20_poly1305   | bool       | No       | True     | Allow ChaCha20-Poly1305 encryption  |
| enc_algo_rc4                 | bool       | No       | True     | Allow RC4 encryption                |
| keyxchg_algo_dhe             | bool       | No       | True     | Allow DHE key exchange              |
| keyxchg_algo_ecdhe           | bool       | No       | True     | Allow ECDHE key exchange            |
| keyxchg_algo_rsa             | bool       | No       | True     | Allow RSA key exchange              |

### SSLForwardProxy

| Attribute                          | Type | Required | Default | Description                              |
|------------------------------------|------|----------|---------|------------------------------------------|
| auto_include_altname               | bool | No       | False   | Include alternative names                |
| block_client_cert                  | bool | No       | False   | Block client certificates                |
| block_expired_certificate          | bool | No       | False   | Block expired certificates               |
| block_timeout_cert                 | bool | No       | False   | Block certificates that timed out        |
| block_tls13_downgrade_no_resource  | bool | No       | False   | Block TLS 1.3 downgrade when no resource |
| block_unknown_cert                 | bool | No       | False   | Block unknown certificates               |
| block_unsupported_cipher           | bool | No       | False   | Block unsupported ciphers                |
| block_unsupported_version          | bool | No       | False   | Block unsupported versions               |
| block_untrusted_issuer             | bool | No       | False   | Block untrusted issuers                  |
| restrict_cert_exts                 | bool | No       | False   | Restrict certificate extensions          |
| strip_alpn                         | bool | No       | False   | Strip ALPN                               |

### SSLInboundProxy

| Attribute                  | Type | Required | Default | Description                     |
|----------------------------|------|----------|---------|---------------------------------|
| block_if_hsm_unavailable   | bool | No       | False   | Block if HSM is unavailable     |
| block_if_no_resource       | bool | No       | False   | Block if no resources available |
| block_unsupported_cipher   | bool | No       | False   | Block unsupported ciphers       |
| block_unsupported_version  | bool | No       | False   | Block unsupported versions      |

### SSLNoProxy

| Attribute                  | Type | Required | Default | Description                |
|----------------------------|------|----------|---------|----------------------------|
| block_expired_certificate  | bool | No       | False   | Block expired certificates |
| block_untrusted_issuer     | bool | No       | False   | Block untrusted issuers    |

## Exceptions

The Decryption Profile models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
    - When multiple container types (folder/snippet/device) are specified
    - When no container type is specified for create operations
    - When SSL version validation fails (max_version < min_version)
    - When name pattern validation fails (must start with alphanumeric character)
    - When container field pattern validation fails
    - When field length limits are exceeded

## Model Validators

### SSL Version Validation

The SSL protocol settings enforce that max_version cannot be less than min_version:

```python
# Using dictionary
try:
    profile_dict = {
        "name": "invalid-profile",
        "folder": "Texas",
        "ssl_protocol_settings": {
            "min_version": "tls1-2",
            "max_version": "tls1-1"  # Invalid: max < min
        }
    }
    response = profile.create(profile_dict)
except ValueError as e:
    print(e)  # "max_version cannot be less than min_version"

# Using model directly
from scm.models.security import SSLProtocolSettings

try:
    settings = SSLProtocolSettings(
        min_version="tls1-2",
        max_version="tls1-1"  # Invalid: max < min
    )
except ValueError as e:
    print(e)  # "max_version cannot be less than min_version"
```

### Container Type Validation

For create operations, exactly one container type must be specified:

```python
# Using dictionary
from scm.config.security import DecryptionProfile

# Error: multiple containers specified
try:
    profile_dict = {
        "name": "invalid-profile",
        "folder": "Texas",
        "device": "fw01",  # Can't specify both folder and device
        "ssl_protocol_settings": {
            "min_version": "tls1-2",
            "max_version": "tls1-3"
        }
    }
    profile = DecryptionProfile(api_client)
    response = profile.create(profile_dict)
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."
```

## Usage Examples

### Creating a Basic Decryption Profile

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
    "name": "basic-profile",
    "folder": "Texas",
    "ssl_protocol_settings": {
        "min_version": "tls1-2",
        "max_version": "tls1-3",
        "auth_algo_sha256": True,
        "auth_algo_sha384": True
    }
}

response = client.decryption_profile.create(profile_dict)
print(f"Created profile: {response.name}")
```

### Creating a Profile with Forward Proxy Settings

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary
forward_proxy_config = {
    "name": "forward-proxy-profile",
    "folder": "Texas",
    "ssl_forward_proxy": {
        "auto_include_altname": True,
        "block_expired_certificate": True,
        "block_untrusted_issuer": True,
        "strip_alpn": False
    },
    "ssl_protocol_settings": {
        "min_version": "tls1-2",
        "max_version": "tls1-3"
    }
}

response = client.decryption_profile.create(forward_proxy_config)
print(f"Created forward proxy profile: {response.name}")
```

### Updating a Decryption Profile

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Fetch existing profile
existing = client.decryption_profile.fetch(name="basic-profile", folder="Texas")

# Modify attributes using dot notation
existing.ssl_protocol_settings.min_version = "tls1-2"
existing.ssl_protocol_settings.max_version = "tls1-3"

# Modify forward proxy settings if present
if existing.ssl_forward_proxy:
    existing.ssl_forward_proxy.block_expired_certificate = True
    existing.ssl_forward_proxy.block_untrusted_issuer = True

# Pass modified object to update()
updated = client.decryption_profile.update(existing)
print(f"Updated profile: {updated.name}")
```
