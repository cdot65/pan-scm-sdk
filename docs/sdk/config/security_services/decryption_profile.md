# Decryption Profile Configuration Object

Manages decryption profiles that control SSL/TLS inspection settings in Palo Alto Networks Strata Cloud Manager.

## Class Overview

The `DecryptionProfile` class inherits from `BaseObject` and provides CRUD operations for decryption profiles that control SSL/TLS inspection settings for both forward proxy and inbound proxy scenarios.

### Methods

| Method     | Description                        | Parameters                              | Return Type                            |
|------------|------------------------------------|-----------------------------------------|----------------------------------------|
| `create()` | Creates a new profile              | `data: Dict[str, Any]`                  | `DecryptionProfileResponseModel`       |
| `get()`    | Retrieves a profile by ID          | `object_id: str`                        | `DecryptionProfileResponseModel`       |
| `update()` | Updates an existing profile        | `profile: DecryptionProfileUpdateModel` | `DecryptionProfileResponseModel`       |
| `delete()` | Deletes a profile                  | `object_id: str`                        | `None`                                 |
| `list()`   | Lists profiles with filtering      | `folder: str`, `**filters`              | `List[DecryptionProfileResponseModel]` |
| `fetch()`  | Gets profile by name and container | `name: str`, `folder: str`              | `DecryptionProfileResponseModel`       |

### Model Attributes

#### Base Profile Attributes

| Attribute               | Type                | Required | Default | Description                                                   |
|-------------------------|---------------------|----------|---------|---------------------------------------------------------------|
| `name`                  | str                 | Yes      | None    | Profile name. Pattern: `^[A-Za-z0-9][A-Za-z0-9_\-\.\s]*$`     |
| `id`                    | UUID                | Yes*     | None    | Unique identifier (*response/update only)                     |
| `ssl_forward_proxy`     | SSLForwardProxy     | No       | None    | SSL Forward Proxy settings                                    |
| `ssl_inbound_proxy`     | SSLInboundProxy     | No       | None    | SSL Inbound Proxy settings                                    |
| `ssl_no_proxy`          | SSLNoProxy          | No       | None    | SSL No Proxy settings                                         |
| `ssl_protocol_settings` | SSLProtocolSettings | No       | None    | SSL Protocol settings                                         |
| `folder`                | str                 | No**     | None    | Folder location. Max 64 chars                                 |
| `snippet`               | str                 | No**     | None    | Snippet location. Max 64 chars                                |
| `device`                | str                 | No**     | None    | Device location. Max 64 chars                                 |

\* Only required for update and response models
\** Exactly one container (`folder`, `snippet`, or `device`) must be provided for create operations

#### SSL Protocol Settings

| Attribute                    | Type       | Required | Default  | Description                         |
|------------------------------|------------|----------|----------|-------------------------------------|
| `min_version`                | SSLVersion | No       | tls1-0   | Minimum SSL/TLS version             |
| `max_version`                | SSLVersion | No       | tls1-2   | Maximum SSL/TLS version             |
| `auth_algo_md5`              | bool       | No       | True     | Allow MD5 authentication            |
| `auth_algo_sha1`             | bool       | No       | True     | Allow SHA1 authentication           |
| `auth_algo_sha256`           | bool       | No       | True     | Allow SHA256 authentication         |
| `auth_algo_sha384`           | bool       | No       | True     | Allow SHA384 authentication         |
| `enc_algo_3des`              | bool       | No       | True     | Allow 3DES encryption               |
| `enc_algo_aes_128_cbc`       | bool       | No       | True     | Allow AES-128-CBC encryption        |
| `enc_algo_aes_128_gcm`       | bool       | No       | True     | Allow AES-128-GCM encryption        |
| `enc_algo_aes_256_cbc`       | bool       | No       | True     | Allow AES-256-CBC encryption        |
| `enc_algo_aes_256_gcm`       | bool       | No       | True     | Allow AES-256-GCM encryption        |
| `enc_algo_chacha20_poly1305` | bool       | No       | True     | Allow ChaCha20-Poly1305 encryption  |
| `enc_algo_rc4`               | bool       | No       | True     | Allow RC4 encryption                |
| `keyxchg_algo_dhe`           | bool       | No       | True     | Allow DHE key exchange              |
| `keyxchg_algo_ecdhe`         | bool       | No       | True     | Allow ECDHE key exchange            |
| `keyxchg_algo_rsa`           | bool       | No       | True     | Allow RSA key exchange              |

#### Forward Proxy Settings (SSLForwardProxy)

| Attribute                           | Type | Required | Default | Description                              |
|-------------------------------------|------|----------|---------|------------------------------------------|
| `auto_include_altname`              | bool | No       | False   | Include alternative names                |
| `block_client_cert`                 | bool | No       | False   | Block client certificates                |
| `block_expired_certificate`         | bool | No       | False   | Block expired certificates               |
| `block_timeout_cert`                | bool | No       | False   | Block certificates that timed out        |
| `block_tls13_downgrade_no_resource` | bool | No       | False   | Block TLS 1.3 downgrade when no resource |
| `block_unknown_cert`                | bool | No       | False   | Block unknown certificates               |
| `block_unsupported_cipher`          | bool | No       | False   | Block unsupported ciphers                |
| `block_unsupported_version`         | bool | No       | False   | Block unsupported versions               |
| `block_untrusted_issuer`            | bool | No       | False   | Block untrusted issuers                  |
| `restrict_cert_exts`                | bool | No       | False   | Restrict certificate extensions          |
| `strip_alpn`                        | bool | No       | False   | Strip ALPN                               |

#### Inbound Proxy Settings (SSLInboundProxy)

| Attribute                  | Type | Required | Default | Description                    |
|----------------------------|------|----------|---------|--------------------------------|
| `block_if_hsm_unavailable` | bool | No       | False   | Block if HSM is unavailable    |
| `block_if_no_resource`     | bool | No       | False   | Block if no resources available|
| `block_unsupported_cipher` | bool | No       | False   | Block unsupported ciphers      |
| `block_unsupported_version`| bool | No       | False   | Block unsupported versions     |

#### No Proxy Settings (SSLNoProxy)

| Attribute                   | Type | Required | Default | Description                    |
|-----------------------------|------|----------|---------|--------------------------------|
| `block_expired_certificate` | bool | No       | False   | Block expired certificates     |
| `block_untrusted_issuer`    | bool | No       | False   | Block untrusted issuers        |

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
from scm.client import ScmClient

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

profiles = client.decryption_profile
```

## Methods

### List Decryption Profiles

```python
filtered_profiles = client.decryption_profile.list(
    folder='Texas',
    types=['forward']
)

for profile in filtered_profiles:
    print(f"Name: {profile.name}")
    if profile.ssl_forward_proxy:
        print("Type: Forward Proxy")
    elif profile.ssl_inbound_proxy:
        print("Type: Inbound Proxy")
```

**Filtering responses:**

```python
exact_profiles = client.decryption_profile.list(
    folder='Texas',
    exact_match=True
)

combined_filters = client.decryption_profile.list(
    folder='Texas',
    exact_match=True,
    exclude_folders=['All'],
    exclude_snippets=['default'],
    exclude_devices=['DeviceA']
)
```

**Controlling pagination with max_limit:**

```python
client.decryption_profile.max_limit = 4000

all_profiles = client.decryption_profile.list(folder='Texas')
```

### Fetch a Decryption Profile

```python
profile = client.decryption_profile.fetch(name="forward-proxy-profile", folder="Texas")
print(f"Found profile: {profile.name}")
```

### Create a Decryption Profile

```python
# Forward proxy configuration
forward_proxy_config = {
    "name": "forward-proxy-profile",
    "folder": "Texas",
    "ssl_forward_proxy": {
        "auto_include_altname": True,
        "block_expired_certificate": True,
        "block_untrusted_issuer": True
    },
    "ssl_protocol_settings": {
        "min_version": "tls1-2",
        "max_version": "tls1-3"
    }
}
forward_profile = client.decryption_profile.create(forward_proxy_config)

# Inbound proxy configuration
inbound_proxy_config = {
    "name": "inbound-proxy-profile",
    "folder": "Texas",
    "ssl_inbound_proxy": {
        "block_if_no_resource": True,
        "block_unsupported_cipher": True
    },
    "ssl_protocol_settings": {
        "min_version": "tls1-2",
        "max_version": "tls1-3",
        "auth_algo_sha256": True,
        "auth_algo_sha384": True
    }
}
inbound_profile = client.decryption_profile.create(inbound_proxy_config)
```

### Update a Decryption Profile

```python
existing_profile = client.decryption_profile.fetch(
    name="forward-proxy-profile",
    folder="Texas"
)

existing_profile.ssl_protocol_settings.min_version = "tls1-2"
existing_profile.ssl_protocol_settings.max_version = "tls1-3"
existing_profile.ssl_forward_proxy.block_expired_certificate = True
existing_profile.ssl_forward_proxy.block_untrusted_issuer = True

updated_profile = client.decryption_profile.update(existing_profile)
```

### Delete a Decryption Profile

```python
client.decryption_profile.delete("123e4567-e89b-12d3-a456-426655440000")
```

### Get a Decryption Profile by ID

```python
profile_by_id = client.decryption_profile.get(profile.id)
print(f"Retrieved profile: {profile_by_id.name}")
```

## Use Cases

### Committing Changes

```python
result = client.commit(
    folders=["Texas"],
    description="Updated decryption profiles",
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
        "folder": "Texas",
        "ssl_protocol_settings": {
            "min_version": "tls1-2",
            "max_version": "tls1-3"
        },
        "ssl_forward_proxy": {
            "block_expired_certificate": True
        }
    }
    new_profile = client.decryption_profile.create(profile_config)
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

- [Decryption Profile Models](../../models/security_services/decryption_profile_models.md#Overview)
- [Security Services Overview](index.md)
- [API Client](../../client.md)
- [Full Example Scripts](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/security/decryption_profile.py)
