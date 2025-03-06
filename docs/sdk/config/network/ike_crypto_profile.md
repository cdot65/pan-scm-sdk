# IKE Crypto Profiles

IKE (Internet Key Exchange) Crypto Profiles define the encryption, authentication, and key exchange parameters used for IPsec VPN tunnels in Strata Cloud Manager (SCM).

## Overview

The `IKECryptoProfile` class in the SCM SDK provides methods to create, retrieve, update, and delete IKE crypto profiles. These profiles define:

- Hash algorithms for integrity validation
- Encryption algorithms for data confidentiality
- Diffie-Hellman groups for secure key exchange
- Lifetime settings for security key rotation

## Importing the Module

```python
from scm.client import ScmClient
from scm.config.network import IKECryptoProfile
```

## Initializing the Client

```python
# Initialize with ScmClient
client = ScmClient(
    client_id="your-client-id",
    client_secret="your-client-secret",
    tsg_id="your-tsg-id",
)

# Create the IKE Crypto Profile service instance
ike_crypto_profile = IKECryptoProfile(client)
```

## Creating an IKE Crypto Profile

```python
# Define the IKE Crypto Profile
profile_data = {
    "name": "example-ike-crypto",
    "hash": ["sha1", "sha256"],
    "encryption": ["aes-128-cbc", "aes-256-cbc"],
    "dh_group": ["group2", "group5", "group14"],
    "lifetime": {"hours": 8},
    "folder": "Example-Folder"
}

# Create the profile
new_profile = ike_crypto_profile.create(profile_data)

# Print the profile ID
print(f"Created IKE Crypto Profile with ID: {new_profile.id}")
```

## Retrieving an IKE Crypto Profile

Get by ID:

```python
# Get by ID
profile = ike_crypto_profile.get("123e4567-e89b-12d3-a456-426655440000")
print(f"Retrieved profile: {profile.name}")
```

Fetch by name:

```python
# Fetch by name
profile = ike_crypto_profile.fetch(
    name="example-ike-crypto",
    folder="Example-Folder"
)
print(f"Retrieved profile: {profile.name}")
```

## Listing IKE Crypto Profiles

```python
# List all profiles in a folder
profiles = ike_crypto_profile.list(folder="Example-Folder")

# Print profile names
for profile in profiles:
    print(f"Profile: {profile.name} (ID: {profile.id})")
    print(f"  Hash: {', '.join([h.value for h in profile.hash])}")
    print(f"  Encryption: {', '.join([e.value for e in profile.encryption])}")
    print(f"  DH Groups: {', '.join([g.value for g in profile.dh_group])}")
```

## Updating an IKE Crypto Profile

```python
from scm.models.network import IKECryptoProfileUpdateModel

# Create update model
update_data = {
    "id": "123e4567-e89b-12d3-a456-426655440000",
    "name": "example-ike-crypto",
    "hash": ["sha256", "sha384"],  # Updated hash algorithms
    "encryption": ["aes-256-cbc", "aes-256-gcm"],  # Updated encryption
    "dh_group": ["group2", "group5", "group14"],
    "lifetime": {"days": 1},  # Updated lifetime
    "folder": "Example-Folder"
}

update_model = IKECryptoProfileUpdateModel(**update_data)
updated_profile = ike_crypto_profile.update(update_model)

print(f"Updated profile: {updated_profile.name}")
```

## Deleting an IKE Crypto Profile

```python
# Delete by ID
ike_crypto_profile.delete("123e4567-e89b-12d3-a456-426655440000")
print("Profile deleted successfully")
```

## Available Fields

### IKE Crypto Profile Model

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| name | string | Profile name (max 31 chars) | Yes |
| hash | array | Hashing algorithms (md5, sha1, sha256, sha384, sha512) | Yes |
| encryption | array | Encryption algorithms (des, 3des, aes-128-cbc, aes-192-cbc, aes-256-cbc, aes-128-gcm, aes-256-gcm) | Yes |
| dh_group | array | DH Groups (group1, group2, group5, group14, group19, group20) | Yes |
| lifetime | object | Lifetime configuration (seconds, minutes, hours, or days) | No |
| authentication_multiple | integer | IKEv2 SA reauthentication interval multiplier (0-50) | No |
| folder | string | The folder containing the profile | No |
| snippet | string | The snippet containing the profile | No |
| device | string | The device containing the profile | No |

> **Note:** One of `folder`, `snippet`, or `device` must be provided when creating or updating a profile.

## Lifetime Configuration

The lifetime field accepts one of the following formats:

```python
# Seconds (valid range: 180-65535)
lifetime = {"seconds": 300}

# Minutes (valid range: 3-65535)
lifetime = {"minutes": 60}

# Hours (valid range: 1-65535)
lifetime = {"hours": 8}

# Days (valid range: 1-365)
lifetime = {"days": 30}
```

## Full Example

```python
from scm.client import Client
from scm.config.network import IKECryptoProfile
from scm.models.network import (
    IKECryptoProfileUpdateModel,
    HashAlgorithm,
    EncryptionAlgorithm,
    DHGroup,
)

# Initialize client
client = ScmClient(
    client_id="your-client-id",
    client_secret="your-client-secret",
    tsg_id="your-tsg-id",
)

# Create IKE Crypto Profile service
ike_crypto_profile = IKECryptoProfile(client)

# Create a new profile
profile_data = {
    "name": "example-ike-crypto",
    "hash": [HashAlgorithm.SHA1, HashAlgorithm.SHA256],
    "encryption": [
        EncryptionAlgorithm.AES_128_CBC, 
        EncryptionAlgorithm.AES_256_CBC
    ],
    "dh_group": [DHGroup.GROUP2, DHGroup.GROUP5, DHGroup.GROUP14],
    "lifetime": {"hours": 8},
    "folder": "Example-Folder"
}

new_profile = ike_crypto_profile.create(profile_data)
print(f"Created profile with ID: {new_profile.id}")

# List all profiles
profiles = ike_crypto_profile.list(folder="Example-Folder")
print(f"Found {len(profiles)} profiles")

# Update the profile
update_data = {
    "id": str(new_profile.id),
    "name": new_profile.name,
    "hash": [HashAlgorithm.SHA256, HashAlgorithm.SHA384],
    "encryption": [
        EncryptionAlgorithm.AES_256_CBC,
        EncryptionAlgorithm.AES_256_GCM,
    ],
    "dh_group": new_profile.dh_group,
    "lifetime": {"days": 1},
    "folder": "Example-Folder"
}

update_model = IKECryptoProfileUpdateModel(**update_data)
updated_profile = ike_crypto_profile.update(update_model)
print(f"Updated profile encryption: {[e.value for e in updated_profile.encryption]}")

# Delete the profile
ike_crypto_profile.delete(str(updated_profile.id))
print("Profile deleted successfully")
```

## Error Handling

```python
from scm.exceptions import InvalidObjectError, MissingQueryParameterError

try:
    # Attempt to fetch a profile
    profile = ike_crypto_profile.fetch(
        name="example-ike-crypto",
        folder="Example-Folder"
    )
except InvalidObjectError as e:
    print(f"Invalid object error: {e}")
except MissingQueryParameterError as e:
    print(f"Missing parameter error: {e}")
except Exception as e:
    print(f"Error: {e}")
```