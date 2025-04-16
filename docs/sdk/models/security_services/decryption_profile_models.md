# Decryption Profile Models

## Overview {#Overview}

The Decryption Profile models provide a structured way to manage SSL/TLS decryption settings in Palo Alto Networks'
Strata Cloud Manager. These models support configuring forward proxy, inbound proxy, and no-proxy SSL settings, as well
as
protocol-specific settings like allowed algorithms and TLS versions. The models handle validation of inputs and outputs
when interacting with the SCM API.

## Attributes

| Attribute             | Type                | Required | Default | Description                                            |
|-----------------------|---------------------|----------|---------|--------------------------------------------------------|
| name                  | str                 | Yes      | None    | Name of profile. Must start with alphanumeric char     |
| ssl_forward_proxy     | SSLForwardProxy     | No       | None    | SSL Forward Proxy settings                             |
| ssl_inbound_proxy     | SSLInboundProxy     | No       | None    | SSL Inbound Proxy settings                             |
| ssl_no_proxy          | SSLNoProxy          | No       | None    | SSL No Proxy settings                                  |
| ssl_protocol_settings | SSLProtocolSettings | No       | None    | SSL Protocol settings                                  |
| folder                | str                 | No*      | None    | Folder where profile is defined. Max length: 64 chars  |
| snippet               | str                 | No*      | None    | Snippet where profile is defined. Max length: 64 chars |
| device                | str                 | No*      | None    | Device where profile is defined. Max length: 64 chars  |
| id                    | UUID                | Yes**    | None    | UUID of the profile (response only)                    |

\* Exactly one container type (folder/snippet/device) must be provided
\** Only required for response model

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

profile = DecryptionProfile(api_client)
response = profile.create(profile_dict)

# Using model directly
from scm.models.security import (
    DecryptionProfileCreateModel,
    SSLProtocolSettings,
    SSLVersion
)

profile = DecryptionProfileCreateModel(
    name="basic-profile",
    folder="Texas",
    ssl_protocol_settings=SSLProtocolSettings(
        min_version=SSLVersion.tls1_2,
        max_version=SSLVersion.tls1_3,
        auth_algo_sha256=True,
        auth_algo_sha384=True
    )
)

payload = profile.model_dump(exclude_unset=True)
response = profile.create(payload)
```

### Creating a Profile with Forward Proxy Settings

```python
# Using dictionary
forward_proxy_dict = {
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

response = profile.create(forward_proxy_dict)

# Using model directly
from scm.models.security import (
    DecryptionProfileCreateModel,
    SSLForwardProxy,
    SSLProtocolSettings,
    SSLVersion
)

forward_proxy = DecryptionProfileCreateModel(
    name="forward-proxy-profile",
    folder="Texas",
    ssl_forward_proxy=SSLForwardProxy(
        auto_include_altname=True,
        block_expired_certificate=True,
        block_untrusted_issuer=True,
        strip_alpn=False
    ),
    ssl_protocol_settings=SSLProtocolSettings(
        min_version=SSLVersion.tls1_2,
        max_version=SSLVersion.tls1_3
    )
)

payload = forward_proxy.model_dump(exclude_unset=True)
response = profile.create(payload)
```

### Updating a Decryption Profile

```python
# Using dictionary
update_dict = {
    "id": "123e4567-e89b-12d3-a456-426655440000",
    "name": "updated-profile",
    "ssl_protocol_settings": {
        "min_version": "tls1-2",
        "max_version": "tls1-3",
        "auth_algo_sha384": True,
        "enc_algo_aes_256_gcm": True
    }
}

response = profile.update(update_dict)

# Using model directly
from scm.models.security import DecryptionProfileUpdateModel

update = DecryptionProfileUpdateModel(
    id="123e4567-e89b-12d3-a456-426655440000",
    name="updated-profile",
    ssl_protocol_settings=SSLProtocolSettings(
        min_version=SSLVersion.tls1_2,
        max_version=SSLVersion.tls1_3,
        auth_algo_sha384=True,
        enc_algo_aes_256_gcm=True
    )
)

payload = update.model_dump(exclude_unset=True)
response = profile.update(payload)
```
