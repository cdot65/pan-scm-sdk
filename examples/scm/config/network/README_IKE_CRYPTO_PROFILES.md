# IKE Crypto Profiles

This directory contains examples for working with IKE Crypto Profiles in Strata Cloud Manager (SCM).

## What are IKE Crypto Profiles?

IKE (Internet Key Exchange) Crypto Profiles define the authentication and encryption algorithms used to establish secure IPsec VPN tunnels. These profiles define:

- Hash algorithms (MD5, SHA1, SHA256, etc.) for validating data integrity
- Encryption algorithms (AES, 3DES, etc.) for protecting data confidentiality
- Diffie-Hellman (DH) groups for secure key exchange
- Lifetime parameters for key rotation

## Available Examples

- `ike_crypto_profile.py`: Complete CRUD (Create, Read, Update, Delete) example for IKE Crypto Profiles

## Using the Examples

Before running the examples, you need to set the following environment variables:

```bash
export SCM_CLIENT_ID="your-client-id"
export SCM_CLIENT_SECRET="your-client-secret"
export SCM_TSG_ID="your-tenant-service-group-id"
```

To run the examples:

```bash
python ike_crypto_profile.py
```

## IKE Crypto Profile Fields

| Field | Description | Type | Required |
|-------|-------------|------|----------|
| name | Profile name (max 31 chars) | string | Yes |
| hash | Hashing algorithms | array of enum | Yes |
| encryption | Encryption algorithms | array of enum | Yes |
| dh_group | DH group for key exchange | array of enum | Yes |
| lifetime | Key lifetime configuration | object | No |
| authentication_multiple | IKEv2 SA reauthentication interval (0-50) | integer | No |

### Hash Algorithm Options
- md5
- sha1
- sha256
- sha384
- sha512

### Encryption Algorithm Options
- des
- 3des
- aes-128-cbc
- aes-192-cbc
- aes-256-cbc
- aes-128-gcm
- aes-256-gcm

### DH Group Options
- group1
- group2
- group5
- group14
- group19
- group20

### Lifetime Configuration
Specify one of the following:
- seconds (180-65535)
- minutes (3-65535)
- hours (1-65535)
- days (1-365)

## Common Operations

### Creating an IKE Crypto Profile

```python
from scm.client import ScmClient
from scm.config.network import IKECryptoProfile

client = ScmClient(
    client_id="your-client-id",
    client_secret="your-client-secret",
    tsg_id="your-tsg-id"
)

ike_crypto_profile_sdk = IKECryptoProfile(client)

profile_data = {
    "name": "example-ike-crypto",
    "hash": ["sha1", "sha256"],
    "encryption": ["aes-128-cbc", "aes-256-cbc"],
    "dh_group": ["group2", "group5", "group14"],
    "lifetime": {"hours": 8},
    "folder": "Example-Folder"
}

profile = ike_crypto_profile_sdk.create(profile_data)
```

### Updating an IKE Crypto Profile

```python
update_data = {
    "id": "profile-uuid",
    "name": "example-ike-crypto",
    "hash": ["sha256", "sha384"],
    "encryption": ["aes-256-cbc", "aes-256-gcm"],
    "dh_group": ["group2", "group5", "group14"],
    "lifetime": {"days": 1},
    "folder": "Example-Folder"
}

from scm.models.network import IKECryptoProfileUpdateModel
update_model = IKECryptoProfileUpdateModel(**update_data)
updated_profile = ike_crypto_profile_sdk.update(update_model)
```

### Listing IKE Crypto Profiles

```python
profiles = ike_crypto_profile_sdk.list(folder="Example-Folder")
```

### Fetching an IKE Crypto Profile by Name

```python
profile = ike_crypto_profile_sdk.fetch(name="example-ike-crypto", folder="Example-Folder")
```

### Deleting an IKE Crypto Profile

```python
ike_crypto_profile_sdk.delete("profile-uuid")
```
