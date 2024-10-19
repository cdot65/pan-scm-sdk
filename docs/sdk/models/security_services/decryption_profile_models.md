# Decryption Profile Models

This section covers the data models associated with the `DecryptionProfile` configuration object.

---

## DecryptionProfileRequestModel

Used when creating or updating a decryption profile object.

### Attributes

- `name` (str): **Required.** The name of the decryption profile.
- `folder` (Optional[str]): The folder where the profile is defined.
- `snippet` (Optional[str]): The snippet where the profile is defined.
- `device` (Optional[str]): The device where the profile is defined.
- `ssl_forward_proxy` (Optional[SSLForwardProxy]): SSL Forward Proxy settings.
- `ssl_inbound_proxy` (Optional[SSLInboundProxy]): SSL Inbound Proxy settings.
- `ssl_no_proxy` (Optional[SSLNoProxy]): SSL No Proxy settings.
- `ssl_protocol_settings` (Optional[SSLProtocolSettings]): SSL Protocol settings.

### Example

<div class="termy">

<!-- termynal -->

```python
decryption_profile_request = DecryptionProfileRequestModel(
    name="test_profile",
    folder="Prisma Access",
    ssl_forward_proxy=SSLForwardProxy(
        auto_include_altname=True,
        block_client_cert=False,
        block_expired_certificate=True
    ),
    ssl_protocol_settings=SSLProtocolSettings(
        min_version=SSLVersion.tls1_0,
        max_version=SSLVersion.tls1_2
    )
)
```

</div>

---

## DecryptionProfileResponseModel

Used when parsing decryption profile objects retrieved from the API.

### Attributes

- `id` (str): The UUID of the decryption profile object.
- `name` (str): The name of the decryption profile.
- `folder` (Optional[str]): The folder where the profile is defined.
- `snippet` (Optional[str]): The snippet where the profile is defined.
- `device` (Optional[str]): The device where the profile is defined.
- `ssl_forward_proxy` (Optional[SSLForwardProxy]): SSL Forward Proxy settings.
- `ssl_inbound_proxy` (Optional[SSLInboundProxy]): SSL Inbound Proxy settings.
- `ssl_no_proxy` (Optional[SSLNoProxy]): SSL No Proxy settings.
- `ssl_protocol_settings` (Optional[SSLProtocolSettings]): SSL Protocol settings.

### Example

<div class="termy">

<!-- termynal -->

```python
decryption_profile_response = DecryptionProfileResponseModel(
    id="123e4567-e89b-12d3-a456-426655440000",
    name="test_profile",
    folder="Prisma Access",
    ssl_forward_proxy=SSLForwardProxy(
        auto_include_altname=True,
        block_client_cert=False,
        block_expired_certificate=True
    ),
    ssl_protocol_settings=SSLProtocolSettings(
        min_version=SSLVersion.tls1_0,
        max_version=SSLVersion.tls1_2
    )
)
```

</div>

---

## Additional Models

### SSLForwardProxy

Represents SSL Forward Proxy settings.

#### Attributes

- `auto_include_altname` (bool): Automatically include alternative names.
- `block_client_cert` (bool): Block client certificate.
- `block_expired_certificate` (bool): Block expired certificates.
- `block_timeout_cert` (bool): Block certificates that have timed out.
- `block_tls13_downgrade_no_resource` (bool): Block TLS 1.3 downgrade when no resource is available.
- `block_unknown_cert` (bool): Block unknown certificates.
- `block_unsupported_cipher` (bool): Block unsupported cipher suites.
- `block_unsupported_version` (bool): Block unsupported SSL/TLS versions.
- `block_untrusted_issuer` (bool): Block untrusted certificate issuers.
- `restrict_cert_exts` (bool): Restrict certificate extensions.
- `strip_alpn` (bool): Strip ALPN (Application-Layer Protocol Negotiation).

### Example

<div class="termy">

<!-- termynal -->

```python
ssl_forward_proxy = SSLForwardProxy(
    auto_include_altname=True,
    block_client_cert=False,
    block_expired_certificate=True,
    block_untrusted_issuer=True,
    strip_alpn=False
)
```

</div>

### SSLInboundProxy

Represents SSL Inbound Proxy settings.

#### Attributes

- `block_if_hsm_unavailable` (bool): Block if HSM (Hardware Security Module) is unavailable.
- `block_if_no_resource` (bool): Block if no resources are available.
- `block_unsupported_cipher` (bool): Block unsupported cipher suites.
- `block_unsupported_version` (bool): Block unsupported SSL/TLS versions.

### Example

<div class="termy">

<!-- termynal -->

```python
ssl_inbound_proxy = SSLInboundProxy(
    block_if_hsm_unavailable=False,
    block_if_no_resource=True,
    block_unsupported_cipher=True,
    block_unsupported_version=True
)
```

</div>

### SSLNoProxy

Represents SSL No Proxy settings.

#### Attributes

- `block_expired_certificate` (bool): Block expired certificates.
- `block_untrusted_issuer` (bool): Block untrusted certificate issuers.

### Example

<div class="termy">

<!-- termynal -->

```python
ssl_no_proxy = SSLNoProxy(
    block_expired_certificate=True,
    block_untrusted_issuer=False
)
```

</div>

### SSLProtocolSettings

Represents SSL Protocol settings.

#### Attributes

- `auth_algo_md5` (bool): Allow MD5 authentication algorithm.
- `auth_algo_sha1` (bool): Allow SHA1 authentication algorithm.
- `auth_algo_sha256` (bool): Allow SHA256 authentication algorithm.
- `auth_algo_sha384` (bool): Allow SHA384 authentication algorithm.
- `enc_algo_3des` (bool): Allow 3DES encryption algorithm.
- `enc_algo_aes_128_cbc` (bool): Allow AES-128-CBC encryption algorithm.
- `enc_algo_aes_128_gcm` (bool): Allow AES-128-GCM encryption algorithm.
- `enc_algo_aes_256_cbc` (bool): Allow AES-256-CBC encryption algorithm.
- `enc_algo_aes_256_gcm` (bool): Allow AES-256-GCM encryption algorithm.
- `enc_algo_chacha20_poly1305` (bool): Allow ChaCha20-Poly1305 encryption algorithm.
- `enc_algo_rc4` (bool): Allow RC4 encryption algorithm.
- `keyxchg_algo_dhe` (bool): Allow DHE key exchange algorithm.
- `keyxchg_algo_ecdhe` (bool): Allow ECDHE key exchange algorithm.
- `keyxchg_algo_rsa` (bool): Allow RSA key exchange algorithm.
- `max_version` (SSLVersion): Maximum allowed SSL/TLS version.
- `min_version` (SSLVersion): Minimum allowed SSL/TLS version.

### Example

<div class="termy">

<!-- termynal -->

```python
ssl_protocol_settings = SSLProtocolSettings(
    min_version=SSLVersion.tls1_1,
    max_version=SSLVersion.tls1_3,
    auth_algo_sha256=True,
    auth_algo_sha384=True,
    enc_algo_aes_256_gcm=True,
    enc_algo_chacha20_poly1305=True,
    keyxchg_algo_ecdhe=True
)
```

</div>

### SSLVersion

Enumeration of SSL/TLS versions.

#### Values

- `sslv3`
- `tls1_0`
- `tls1_1`
- `tls1_2`
- `tls1_3`
- `max`

### Example

<div class="termy">

<!-- termynal -->

```python
min_version = SSLVersion.tls1_1
max_version = SSLVersion.tls1_3
```

</div>

---

## Full Example

<div class="termy">

<!-- termynal -->

```python
from scm.models.security import (
    DecryptionProfileRequestModel,
    SSLForwardProxy,
    SSLInboundProxy,
    SSLNoProxy,
    SSLProtocolSettings,
    SSLVersion
)

# Create a comprehensive decryption profile request
profile_request = DecryptionProfileRequestModel(
    name="comprehensive_profile",
    folder="Prisma Access",
    ssl_forward_proxy=SSLForwardProxy(
        auto_include_altname=True,
        block_client_cert=False,
        block_expired_certificate=True,
        block_untrusted_issuer=True,
        strip_alpn=False
    ),
    ssl_inbound_proxy=SSLInboundProxy(
        block_if_hsm_unavailable=False,
        block_if_no_resource=True,
        block_unsupported_cipher=True,
        block_unsupported_version=True
    ),
    ssl_no_proxy=SSLNoProxy(
        block_expired_certificate=True,
        block_untrusted_issuer=False
    ),
    ssl_protocol_settings=SSLProtocolSettings(
        min_version=SSLVersion.tls1_2,
        max_version=SSLVersion.tls1_3,
        auth_algo_sha256=True,
        auth_algo_sha384=True,
        enc_algo_aes_256_gcm=True,
        enc_algo_chacha20_poly1305=True,
        keyxchg_algo_ecdhe=True
    )
)

# Convert the model to a dictionary
profile_dict = profile_request.model_dump(exclude_unset=True)

print("Decryption Profile Request:")
print(profile_dict)
```

</div>

This example demonstrates how to create a comprehensive `DecryptionProfileRequestModel` object with various SSL
settings, including forward proxy, inbound proxy, no proxy, and protocol settings. The resulting object can be used with
the `DecryptionProfile.create()` method to create a new decryption profile in the Strata Cloud Manager.
