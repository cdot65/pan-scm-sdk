# Decryption Profile Configuration Object

The `DecryptionProfile` class is used to manage decryption profile objects in the Strata Cloud Manager. It provides
methods to create, retrieve, update, delete, and list decryption profile objects.

---

## Creating an API client object

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm

api_client = Scm(
    client_id="this-is-a-placeholder",
    client_secret="this-is-a-placeholder",
    tsg_id="this-is-a-placeholder",
)
```

</div>

## Importing the DecryptionProfile Class

<div class="termy">

<!-- termynal -->

```python
from scm.config.security import DecryptionProfile

decryption_profile = DecryptionProfile(api_client)
```

</div>

## Methods

### `create(data: Dict[str, Any]) -> DecryptionProfileResponseModel`

Creates a new decryption profile object.

**Parameters:**

- `data` (Dict[str, Any]): A dictionary containing the decryption profile object data.

**Example:**

<div class="termy">

<!-- termynal -->

```python
profile_data = {
    "name": "test_profile",
    "folder": "Prisma Access",
    "ssl_forward_proxy": {
        "auto_include_altname": True,
        "block_client_cert": False,
        "block_expired_certificate": True
    },
    "ssl_protocol_settings": {
        "min_version": "tls1-0",
        "max_version": "tls1-2"
    }
}

new_profile = decryption_profile.create(profile_data)
print(f"Created decryption profile with ID: {new_profile.id}")
```

</div>

### `get(object_id: str) -> DecryptionProfileResponseModel`

Retrieves a decryption profile object by its ID.

**Parameters:**

- `object_id` (str): The UUID of the decryption profile object.

**Example:**

<div class="termy">

<!-- termynal -->

```python
profile_id = "123e4567-e89b-12d3-a456-426655440000"
profile_object = decryption_profile.get(profile_id)
print(f"Decryption Profile Name: {profile_object.name}")
```

</div>

### `update(object_id: str, data: Dict[str, Any]) -> DecryptionProfileResponseModel`

Updates an existing decryption profile object.

**Parameters:**

- `object_id` (str): The UUID of the decryption profile object.
- `data` (Dict[str, Any]): A dictionary containing the updated decryption profile data.

**Example:**

<div class="termy">

<!-- termynal -->

```python
update_data = {
    "name": "Updated Profile",
    "folder": "Prisma Access",
    "ssl_inbound_proxy": {
        "block_if_no_resource": True,
        "block_unsupported_cipher": True
    }
}

updated_profile = decryption_profile.update(profile_id, update_data)
print(f"Updated decryption profile with ID: {updated_profile.id}")
```

</div>

### `delete(object_id: str) -> None`

Deletes a decryption profile object by its ID.

**Parameters:**

- `object_id` (str): The UUID of the decryption profile object.

**Example:**

<div class="termy">

<!-- termynal -->

```python
decryption_profile.delete(profile_id)
print(f"Deleted decryption profile with ID: {profile_id}")
```

</div>

###
`list(folder: Optional[str] = None, snippet: Optional[str] = None, device: Optional[str] = None, offset: Optional[int] = None, limit: Optional[int] = None, name: Optional[str] = None, **filters) -> List[DecryptionProfileResponseModel]`

Lists decryption profile objects, optionally filtered by folder, snippet, device, or other criteria.

**Parameters:**

- `folder` (Optional[str]): The folder to list decryption profiles from.
- `snippet` (Optional[str]): The snippet to list decryption profiles from.
- `device` (Optional[str]): The device to list decryption profiles from.
- `offset` (Optional[int]): The offset for pagination.
- `limit` (Optional[int]): The limit for pagination.
- `name` (Optional[str]): Filter profiles by name.
- `**filters`: Additional filters.

**Example:**

<div class="termy">

<!-- termynal -->

```python
profiles = decryption_profile.list(folder='Prisma Access', limit=10)

for profile in profiles:
    print(f"Decryption Profile Name: {profile.name}, ID: {profile.id}")
```

</div>

---

## Usage Examples

### Example 1: Creating a profile with SSL Forward Proxy settings

<div class="termy">

<!-- termynal -->

```python
profile_data = {
    "name": "forward_proxy_profile",
    "folder": "Prisma Access",
    "ssl_forward_proxy": {
        "auto_include_altname": True,
        "block_client_cert": False,
        "block_expired_certificate": True,
        "block_untrusted_issuer": True,
        "strip_alpn": False
    }
}

new_profile = decryption_profile.create(profile_data)
print(f"Created profile with ID: {new_profile.id}")
```

</div>

### Example 2: Updating a profile with SSL Inbound Proxy settings

<div class="termy">

<!-- termynal -->

```python
update_data = {
    "name": "inbound_proxy_profile",
    "folder": "Prisma Access",
    "ssl_inbound_proxy": {
        "block_if_hsm_unavailable": True,
        "block_if_no_resource": True,
        "block_unsupported_cipher": False,
        "block_unsupported_version": True
    }
}

updated_profile = decryption_profile.update(profile_id, update_data)
print(f"Updated profile with ID: {updated_profile.id}")
```

</div>

### Example 3: Creating a profile with SSL Protocol settings

<div class="termy">

<!-- termynal -->

```python
profile_data = {
    "name": "protocol_settings_profile",
    "folder": "Prisma Access",
    "ssl_protocol_settings": {
        "min_version": "tls1-1",
        "max_version": "tls1-3",
        "auth_algo_sha256": True,
        "auth_algo_sha384": True,
        "enc_algo_aes_256_gcm": True,
        "enc_algo_chacha20_poly1305": True,
        "keyxchg_algo_ecdhe": True
    }
}

new_profile = decryption_profile.create(profile_data)
print(f"Created profile with ID: {new_profile.id}")
```

</div>

### Example 4: Listing profiles with filters

<div class="termy">

<!-- termynal -->

```python
filtered_profiles = decryption_profile.list(
    folder='Prisma Access',
    limit=5,
    name='proxy_profile'
)

for profile in filtered_profiles:
    print(f"Filtered Profile: {profile.name}")
```

</div>

### Example 5: Creating a profile with SSL No Proxy settings

<div class="termy">

<!-- termynal -->

```python
profile_data = {
    "name": "no_proxy_profile",
    "folder": "Prisma Access",
    "ssl_no_proxy": {
        "block_expired_certificate": True,
        "block_untrusted_issuer": False
    }
}

new_profile = decryption_profile.create(profile_data)
print(f"Created profile with ID: {new_profile.id}")
```

</div>

### Example 6: Updating a profile with multiple SSL settings

<div class="termy">

<!-- termynal -->

```python
update_data = {
    "name": "comprehensive_profile",
    "folder": "Prisma Access",
    "ssl_forward_proxy": {
        "auto_include_altname": True,
        "block_client_cert": False
    },
    "ssl_inbound_proxy": {
        "block_if_no_resource": True
    },
    "ssl_no_proxy": {
        "block_expired_certificate": True
    },
    "ssl_protocol_settings": {
        "min_version": "tls1-2",
        "max_version": "tls1-3"
    }
}

updated_profile = decryption_profile.update(profile_id, update_data)
print(f"Updated profile with ID: {updated_profile.id}")
```

</div>

---

## Full Example

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.security import DecryptionProfile

# Initialize the SCM client
api_client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
)

# Create a DecryptionProfile instance
decryption_profile = DecryptionProfile(api_client)

# Create a new decryption profile
profile_data = {
    "name": "comprehensive_profile",
    "folder": "Prisma Access",
    "ssl_forward_proxy": {
        "auto_include_altname": True,
        "block_client_cert": False,
        "block_expired_certificate": True,
        "block_untrusted_issuer": True,
        "strip_alpn": False
    },
    "ssl_inbound_proxy": {
        "block_if_hsm_unavailable": False,
        "block_if_no_resource": True,
        "block_unsupported_cipher": True,
        "block_unsupported_version": True
    },
    "ssl_no_proxy": {
        "block_expired_certificate": True,
        "block_untrusted_issuer": False
    },
    "ssl_protocol_settings": {
        "min_version": "tls1-2",
        "max_version": "tls1-3",
        "auth_algo_sha256": True,
        "auth_algo_sha384": True,
        "enc_algo_aes_256_gcm": True,
        "enc_algo_chacha20_poly1305": True,
        "keyxchg_algo_ecdhe": True
    }
}

new_profile = decryption_profile.create(profile_data)
print(f"Created comprehensive decryption profile with ID: {new_profile.id}")

# List decryption profiles
profiles = decryption_profile.list(folder='Prisma Access', limit=10)
for profile in profiles:
    print(f"Decryption Profile Name: {profile.name}, ID: {profile.id}")

# Update the profile
update_data = {
    "name": "updated_comprehensive_profile",
    "ssl_forward_proxy": {
        "block_tls13_downgrade_no_resource": True
    },
    "ssl_protocol_settings": {
        "min_version": "tls1-1"
    }
}

updated_profile = decryption_profile.update(new_profile.id, update_data)
print(f"Updated decryption profile with ID: {updated_profile.id}")

# Delete the profile
decryption_profile.delete(new_profile.id)
print(f"Deleted decryption profile with ID: {new_profile.id}")
```

</div>

---

## Related Models

- [DecryptionProfileRequestModel](../../models/security_services/decryption_profile_models.md#DecryptionProfileRequestModel)
- [DecryptionProfileResponseModel](../../models/security_services/decryption_profile_models.md#DecryptionProfileResponseModel)
