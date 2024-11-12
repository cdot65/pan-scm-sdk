# Decryption Profile Configuration Object

The `DecryptionProfile` class provides functionality to manage decryption profiles in Palo Alto Networks' Strata Cloud
Manager.
Decryption profiles define SSL/TLS inspection settings for both forward proxy and inbound proxy scenarios, allowing
granular
control over encryption protocols, algorithms, and certificate validation.

## Overview

Decryption profiles in Strata Cloud Manager allow you to:

- Configure SSL/TLS protocol versions and cipher suites
- Define forward proxy settings for outbound traffic inspection
- Set up inbound proxy settings for inbound traffic inspection
- Specify certificate validation requirements
- Control protocol downgrades and extensions
- Organize profiles within folders, snippets, or devices

## Methods

| Method     | Description                                     |
|------------|-------------------------------------------------|
| `create()` | Creates a new decryption profile                |
| `get()`    | Retrieves a decryption profile by ID            |
| `update()` | Updates an existing decryption profile          |
| `delete()` | Deletes a decryption profile                    |
| `list()`   | Lists decryption profiles with optional filters |
| `fetch()`  | Retrieves a single decryption profile by name   |

## Creating Decryption Profiles

The `create()` method allows you to define new decryption profiles. You must specify a name and exactly one container
type
(folder, snippet, or device).

**Example: Forward Proxy Profile**

<div class="termy">

<!-- termynal -->

```python
forward_proxy = {
    "name": "forward-proxy",
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

new_profile = decryption_profiles.create(forward_proxy)
print(f"Created profile: {new_profile.name}")
```

</div>

**Example: Inbound Proxy Profile**

<div class="termy">

<!-- termynal -->

```python
inbound_proxy = {
    "name": "inbound-proxy",
    "folder": "Shared",
    "ssl_inbound_proxy": {
        "block_if_no_resource": True,
        "block_unsupported_cipher": True,
        "block_unsupported_version": True
    },
    "ssl_protocol_settings": {
        "min_version": "tls1-2",
        "max_version": "tls1-3",
        "auth_algo_sha256": True,
        "auth_algo_sha384": True
    }
}

new_profile = decryption_profiles.create(inbound_proxy)
print(f"Created profile: {new_profile.name}")
```

</div>

## Getting Decryption Profiles

Use the `get()` method to retrieve a decryption profile by its ID.

<div class="termy">

<!-- termynal -->

```python
profile_id = "123e4567-e89b-12d3-a456-426655440000"
profile = decryption_profiles.get(profile_id)
print(f"Profile Name: {profile.name}")
```

</div>

## Updating Decryption Profiles

The `update()` method allows you to modify existing decryption profiles.

<div class="termy">

<!-- termynal -->

```python
fetched_profile = decryption_profiles.fetch(folder='Texas', name="forward-proxy")
fetched_profile["ssl_forward_proxy"]["auto_include_altname"] = False

updated_profile = decryption_profiles.update(fetched_profile)
print(f"Updated profile: {updated_profile.name}")
```

</div>

## Deleting Decryption Profiles

Use the `delete()` method to remove a decryption profile.

<div class="termy">

<!-- termynal -->

```python
profile_id = "123e4567-e89b-12d3-a456-426655440000"
decryption_profiles.delete(profile_id)
print("Profile deleted successfully")
```

</div>

## Listing Decryption Profiles

The `list()` method retrieves multiple decryption profiles with optional filtering. You can filter the results using the
following kwargs:

- `types`: List[str] - Filter by proxy types (e.g., ['forward', 'inbound', 'no'])

<div class="termy">

<!-- termynal -->

```python
# List all profiles in a folder
profiles = decryption_profiles.list(folder="Texas")

# List only forward proxy profiles
forward_profiles = decryption_profiles.list(
    folder="Texas",
    types=['forward']
)

# List both forward and inbound proxy profiles
mixed_profiles = decryption_profiles.list(
    folder="Texas",
    types=['forward', 'inbound']
)

# Print the results
for profile in profiles:
    print(f"Name: {profile.name}")
    if profile.ssl_forward_proxy:
        print("Type: Forward Proxy")
    elif profile.ssl_inbound_proxy:
        print("Type: Inbound Proxy")
    else:
        print("Type: No Proxy")
```

</div>

## Fetching Decryption Profiles

The `fetch()` method retrieves a single decryption profile by name from a specific container.

<div class="termy">

<!-- termynal -->

```python
profile = decryption_profiles.fetch(name="Oblivion", folder="Texas")

print(f"Found profile: {profile['name']}")
print(f"Current settings: {profile['ssl_protocol_settings']}")
```

</div>

## Full Workflow Example

Here's a complete example demonstrating the full lifecycle of a decryption profile:

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.security import DecryptionProfile

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize decryption profile object
decryption_profiles = DecryptionProfile(client)

# Create new profile
forward_proxy = {
    "name": "forward-proxy",
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

new_profile = decryption_profiles.create(forward_proxy)
print(f"Created profile: {new_profile.name}")

# Fetch the profile by name
fetched_profile = decryption_profiles.fetch(
    name="forward-proxy",
    folder="Texas"
)

# Modify the fetched profile
fetched_profile["ssl_forward_proxy"]["auto_include_altname"] = False

# Update using the modified object
updated_profile = decryption_profiles.update(fetched_profile)
print(f"Updated profile: {updated_profile.name}")

# List all profiles
profiles = decryption_profiles.list(folder="Texas")
for profile in profiles:
    print(f"Listed profile: {profile.name}")

# Clean up
decryption_profiles.delete(new_profile.id)
print("Profile deleted successfully")
```

</div>

## Related Models

- [DecryptionProfileCreateModel](../../models/security/decryption_profile_models.md#decryptionprofilecreatemodel)
- [DecryptionProfileUpdateModel](../../models/security/decryption_profile_models.md#decryptionprofileupdatemodel)
- [DecryptionProfileResponseModel](../../models/security/decryption_profile_models.md#decryptionprofileresponsemodel)