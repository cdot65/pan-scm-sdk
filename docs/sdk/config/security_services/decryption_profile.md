# Decryption Profile Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Model Attributes](#model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating Decryption Profiles](#creating-decryption-profiles)
    - [Retrieving Profiles](#retrieving-profiles)
    - [Updating Profiles](#updating-profiles)
    - [Listing Profiles](#listing-profiles)
    - [Filtering Responses](#filtering-responses)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Deleting Profiles](#deleting-profiles)
7. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Full Script Examples](#full-script-examples)
11. [Related Models](#related-models)

## Overview

The `DecryptionProfile` class provides functionality to manage decryption profiles in Palo Alto Networks' Strata Cloud
Manager. This class inherits from `BaseObject` and provides methods for creating, retrieving, updating, and deleting
decryption profiles that control SSL/TLS inspection settings for both forward proxy and inbound proxy scenarios.

## Core Methods

| Method     | Description                        | Parameters                              | Return Type                            |
|------------|------------------------------------|-----------------------------------------|----------------------------------------|
| `create()` | Creates a new profile              | `data: Dict[str, Any]`                  | `DecryptionProfileResponseModel`       |
| `get()`    | Retrieves a profile by ID          | `object_id: str`                        | `DecryptionProfileResponseModel`       |
| `update()` | Updates an existing profile        | `profile: DecryptionProfileUpdateModel` | `DecryptionProfileResponseModel`       |
| `delete()` | Deletes a profile                  | `object_id: str`                        | `None`                                 |
| `list()`   | Lists profiles with filtering      | `folder: str`, `**filters`              | `List[DecryptionProfileResponseModel]` |
| `fetch()`  | Gets profile by name and container | `name: str`, `folder: str`              | `DecryptionProfileResponseModel`       |

## Model Attributes

### Base Profile Attributes

| Attribute             | Type                | Required | Default | Description                                                          |
|-----------------------|---------------------|----------|---------|----------------------------------------------------------------------|
| `name`                | str                 | Yes      | None    | Profile name. Pattern: `^[A-Za-z0-9][A-Za-z0-9_\-\.\s]*$`            |
| `id`                  | UUID                | Yes*     | None    | Unique identifier (*response/update only)                            |
| `ssl_forward_proxy`   | SSLForwardProxy     | No       | None    | SSL Forward Proxy settings                                           |
| `ssl_inbound_proxy`   | SSLInboundProxy     | No       | None    | SSL Inbound Proxy settings                                           |
| `ssl_no_proxy`        | SSLNoProxy          | No       | None    | SSL No Proxy settings                                                |
| `ssl_protocol_settings` | SSLProtocolSettings | No     | None    | SSL Protocol settings                                                |
| `folder`              | str                 | No**     | None    | Folder location. Max 64 chars                                        |
| `snippet`             | str                 | No**     | None    | Snippet location. Max 64 chars                                       |
| `device`              | str                 | No**     | None    | Device location. Max 64 chars                                        |

\* Only required for update and response models
\** Exactly one container (folder/snippet/device) must be provided for create operations

### SSL Protocol Settings

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

### Forward Proxy Settings (SSLForwardProxy)

| Attribute                          | Type | Required | Default | Description                              |
|------------------------------------|------|----------|---------|------------------------------------------|
| `auto_include_altname`             | bool | No       | False   | Include alternative names                |
| `block_client_cert`                | bool | No       | False   | Block client certificates                |
| `block_expired_certificate`        | bool | No       | False   | Block expired certificates               |
| `block_timeout_cert`               | bool | No       | False   | Block certificates that timed out        |
| `block_tls13_downgrade_no_resource`| bool | No       | False   | Block TLS 1.3 downgrade when no resource |
| `block_unknown_cert`               | bool | No       | False   | Block unknown certificates               |
| `block_unsupported_cipher`         | bool | No       | False   | Block unsupported ciphers                |
| `block_unsupported_version`        | bool | No       | False   | Block unsupported versions               |
| `block_untrusted_issuer`           | bool | No       | False   | Block untrusted issuers                  |
| `restrict_cert_exts`               | bool | No       | False   | Restrict certificate extensions          |
| `strip_alpn`                       | bool | No       | False   | Strip ALPN                               |

### Inbound Proxy Settings (SSLInboundProxy)

| Attribute                 | Type | Required | Default | Description                    |
|---------------------------|------|----------|---------|--------------------------------|
| `block_if_hsm_unavailable`| bool | No       | False   | Block if HSM is unavailable    |
| `block_if_no_resource`    | bool | No       | False   | Block if no resources available|
| `block_unsupported_cipher`| bool | No       | False   | Block unsupported ciphers      |
| `block_unsupported_version`| bool| No       | False   | Block unsupported versions     |

### No Proxy Settings (SSLNoProxy)

| Attribute                 | Type | Required | Default | Description                    |
|---------------------------|------|----------|---------|--------------------------------|
| `block_expired_certificate`| bool| No       | False   | Block expired certificates     |
| `block_untrusted_issuer`  | bool | No       | False   | Block untrusted issuers        |

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

The Decryption Profile service can be accessed using the unified client interface (recommended):

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access decryption profiles directly through the client
profiles = client.decryption_profile
```

## Usage Examples

### Creating Decryption Profiles

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

# Create forward proxy profile using the client
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

# Create inbound proxy profile
inbound_profile = client.decryption_profile.create(inbound_proxy_config)
```

### Retrieving Profiles

```python
# Fetch by name and folder
profile = client.decryption_profile.fetch(name="forward-proxy-profile", folder="Texas")
print(f"Found profile: {profile.name}")

# Get by ID
profile_by_id = client.decryption_profile.get(profile.id)
print(f"Retrieved profile: {profile_by_id.name}")
```

### Updating Profiles

```python
# Fetch existing profile
existing_profile = client.decryption_profile.fetch(
    name="forward-proxy-profile",
    folder="Texas"
)

# Update SSL settings
existing_profile.ssl_protocol_settings.min_version = "tls1-2"
existing_profile.ssl_protocol_settings.max_version = "tls1-3"

# Update forward proxy settings
existing_profile.ssl_forward_proxy.block_expired_certificate = True
existing_profile.ssl_forward_proxy.block_untrusted_issuer = True

# Perform update
updated_profile = client.decryption_profile.update(existing_profile)
```

### Listing Profiles

```python
# List with direct filter parameters
filtered_profiles = client.decryption_profile.list(
    folder='Texas',
    types=['forward']
)

# Process results
for profile in filtered_profiles:
    print(f"Name: {profile.name}")
    if profile.ssl_forward_proxy:
        print("Type: Forward Proxy")
    elif profile.ssl_inbound_proxy:
        print("Type: Inbound Proxy")

# Define filter parameters as dictionary
list_params = {
    "folder": "Texas",
    "types": ["forward", "inbound"]
}

# List with filters as kwargs
filtered_profiles = client.decryption_profile.list(**list_params)
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
exact_profiles = client.decryption_profile.list(
    folder='Texas',
    exact_match=True
)

for profile in exact_profiles:
    print(f"Exact match: {profile.name} in {profile.folder}")

# Exclude all profiles from the 'All' folder
no_all_profiles = client.decryption_profile.list(
    folder='Texas',
    exclude_folders=['All']
)

for profile in no_all_profiles:
    assert profile.folder != 'All'
    print(f"Filtered out 'All': {profile.name}")

# Exclude profiles that come from 'default' snippet
no_default_snippet = client.decryption_profile.list(
    folder='Texas',
    exclude_snippets=['default']
)

for profile in no_default_snippet:
    assert profile.snippet != 'default'
    print(f"Filtered out 'default' snippet: {profile.name}")

# Exclude profiles associated with 'DeviceA'
no_deviceA = client.decryption_profile.list(
    folder='Texas',
    exclude_devices=['DeviceA']
)

for profile in no_deviceA:
    assert profile.device != 'DeviceA'
    print(f"Filtered out 'DeviceA': {profile.name}")

# Combine exact_match with multiple exclusions
combined_filters = client.decryption_profile.list(
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
client.decryption_profile.max_limit = 4000

# List all profiles - auto-paginates through results
all_profiles = client.decryption_profile.list(folder='Texas')

# The profiles are fetched in chunks according to the max_limit setting.
```

### Deleting Profiles

```python
# Delete by ID
profile_id = "123e4567-e89b-12d3-a456-426655440000"
client.decryption_profile.delete(profile_id)
```

## Managing Configuration Changes

### Performing Commits

```python
# Prepare commit parameters
commit_params = {
    "folders": ["Texas"],
    "description": "Updated decryption profiles",
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
        "folder": "Texas",
        "ssl_protocol_settings": {
            "min_version": "tls1-2",
            "max_version": "tls1-3"
        },
        "ssl_forward_proxy": {
            "block_expired_certificate": True
        }
    }

    # Create the profile using the client
    new_profile = client.decryption_profile.create(profile_config)

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

1. **SSL/TLS Configuration**
    - Use modern protocol versions (TLS 1.2+)
    - Enable strong cipher suites
    - Regularly review security settings
    - Monitor for deprecated algorithms
    - Document protocol choices

2. **Certificate Management**
    - Validate certificate chains
    - Handle expired certificates
    - Monitor untrusted issuers
    - Implement proper revocation
    - Document certificate policies

3. **Client Usage**
    - Use the unified client interface (`client.decryption_profile`) for simpler code
    - Perform commits directly on the client (`client.commit()`)
    - Monitor jobs using client methods (`client.get_job_status()`, `client.list_jobs()`)
    - Initialize the client once and reuse across different object types

4. **Performance**
    - Monitor resource usage
    - Implement caching
    - Use appropriate timeouts
    - Handle connection limits
    - Track decryption load

5. **Error Handling**
    - Validate input data
    - Handle specific exceptions
    - Log error details
    - Monitor commit status
    - Track job completion

## Full Script Examples

Refer to
the [decryption_profile.py example](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/security/decryption_profile.py).

## Related Models

- [DecryptionProfileBaseModel](../../models/security_services/decryption_profile_models.md#Overview)
- [DecryptionProfileCreateModel](../../models/security_services/decryption_profile_models.md#Overview)
- [DecryptionProfileUpdateModel](../../models/security_services/decryption_profile_models.md#Overview)
- [DecryptionProfileResponseModel](../../models/security_services/decryption_profile_models.md#Overview)
- [SSLProtocolSettings](../../models/security_services/decryption_profile_models.md#Overview)
- [SSLForwardProxy](../../models/security_services/decryption_profile_models.md#Overview)
- [SSLInboundProxy](../../models/security_services/decryption_profile_models.md#Overview)
- [SSLNoProxy](../../models/security_services/decryption_profile_models.md#Overview)
- [SSLVersion](../../models/security_services/decryption_profile_models.md#Overview)
