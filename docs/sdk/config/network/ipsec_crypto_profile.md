# IPsec Crypto Profiles

## Overview

The IPsec Crypto Profile service provides functionality for configuring and managing IPsec crypto profiles within Palo Alto Networks' Strata Cloud Manager. IPsec crypto profiles define the security protocols, encryption, and authentication algorithms used in IPsec VPN tunnels.

## Class Definition

```python
class IPsecCryptoProfile(BaseObject):
    def __init__(self, api_client, max_limit: Optional[int] = None):
        ...
```

## Constructor Parameters

- `api_client`: The API client instance
- `max_limit` (Optional[int]): Maximum number of objects to return in a single API request. Defaults to 2500. Must be between 1 and 5000.

## Methods

### create

```python
def create(self, data: Dict[str, Any]) -> IPsecCryptoProfileResponseModel:
    ...
```

Creates a new IPsec crypto profile.

**Parameters:**
- `data` (Dict[str, Any]): Dictionary containing the IPsec crypto profile configuration

**Returns:**
- `IPsecCryptoProfileResponseModel`: Response model containing the created profile data

**Example:**
```python
profile = client.ipsec_crypto_profile.create({
    "name": "esp-aes-128-sha1",
    "lifetime": {"seconds": 3600},
    "esp": {
        "encryption": ["aes-128-cbc"],
        "authentication": ["sha1"]
    },
    "folder": "Shared"
})
print(f"Created IPsec crypto profile with ID: {profile.id}")
```

### get

```python
def get(self, object_id: str) -> IPsecCryptoProfileResponseModel:
    ...
```

Gets an IPsec crypto profile by ID.

**Parameters:**
- `object_id` (str): The ID of the IPsec crypto profile to retrieve

**Returns:**
- `IPsecCryptoProfileResponseModel`: Response model containing the profile data

**Example:**
```python
profile_id = "123e4567-e89b-12d3-a456-426655440000"
profile = client.ipsec_crypto_profile.get(profile_id)
print(f"Profile name: {profile.name}")
```

### update

```python
def update(self, profile: IPsecCryptoProfileUpdateModel) -> IPsecCryptoProfileResponseModel:
    ...
```

Updates an existing IPsec crypto profile.

**Parameters:**
- `profile` (IPsecCryptoProfileUpdateModel): IPsecCryptoProfileUpdateModel instance containing the update data

**Returns:**
- `IPsecCryptoProfileResponseModel`: Response model containing the updated profile data

**Example:**
```python
from scm.models.network import IPsecCryptoProfileUpdateModel, DhGroup

# Create update model
update_model = IPsecCryptoProfileUpdateModel(
    id="123e4567-e89b-12d3-a456-426655440000",
    name="esp-aes-256-sha256",
    dh_group=DhGroup.GROUP14,
    lifetime={"hours": 2},
    esp={
        "encryption": ["aes-256-cbc"],
        "authentication": ["sha256"]
    },
    folder="Shared"
)

# Update the profile
updated_profile = client.ipsec_crypto_profile.update(update_model)
print(f"Updated profile: {updated_profile.name}")
```

### list

```python
def list(
    self,
    folder: Optional[str] = None,
    snippet: Optional[str] = None,
    device: Optional[str] = None,
    exact_match: bool = False,
    exclude_folders: Optional[List[str]] = None,
    exclude_snippets: Optional[List[str]] = None,
    exclude_devices: Optional[List[str]] = None,
    **filters,
) -> List[IPsecCryptoProfileResponseModel]:
    ...
```

Lists IPsec crypto profile objects with optional filtering.

**Parameters:**
- `folder` (Optional[str]): Optional folder name
- `snippet` (Optional[str]): Optional snippet name
- `device` (Optional[str]): Optional device name
- `exact_match` (bool): If True, only return objects whose container exactly matches the provided container parameter
- `exclude_folders` (Optional[List[str]]): List of folder names to exclude from results
- `exclude_snippets` (Optional[List[str]]): List of snippet values to exclude from results
- `exclude_devices` (Optional[List[str]]): List of device values to exclude from results
- `**filters`: Additional filters for client-side filtering

**Returns:**
- `List[IPsecCryptoProfileResponseModel]`: A list of IPsec crypto profile objects

**Example:**
```python
# List all IPsec crypto profiles in the Shared folder
profiles = client.ipsec_crypto_profile.list(folder="Shared")
for profile in profiles:
    print(f"Profile: {profile.name}, DH Group: {profile.dh_group}")

# List with filtering
profiles = client.ipsec_crypto_profile.list(
    folder="Shared",
    exact_match=True,
    exclude_folders=["Deprecated"]
)
```

### fetch

```python
def fetch(
    self,
    name: str,
    folder: Optional[str] = None,
    snippet: Optional[str] = None,
    device: Optional[str] = None,
) -> IPsecCryptoProfileResponseModel:
    ...
```

Fetches a single IPsec crypto profile by name.

**Parameters:**
- `name` (str): The name of the IPsec crypto profile to fetch
- `folder` (Optional[str]): The folder in which the resource is defined
- `snippet` (Optional[str]): The snippet in which the resource is defined
- `device` (Optional[str]): The device in which the resource is defined

**Returns:**
- `IPsecCryptoProfileResponseModel`: The fetched IPsec crypto profile object

**Example:**
```python
profile = client.ipsec_crypto_profile.fetch(
    name="esp-aes-128-sha1",
    folder="Shared"
)
print(f"Found profile with ID: {profile.id}")
```

### delete

```python
def delete(self, object_id: str) -> None:
    ...
```

Deletes an IPsec crypto profile.

**Parameters:**
- `object_id` (str): The ID of the object to delete

**Returns:**
- None

**Example:**
```python
profile_id = "123e4567-e89b-12d3-a456-426655440000"
client.ipsec_crypto_profile.delete(profile_id)
print(f"Deleted profile with ID: {profile_id}")
```

## Common Use Cases

### Creating ESP-based Profile

```python
esp_profile = client.ipsec_crypto_profile.create({
    "name": "esp-aes-256-gcm",
    "dh_group": "group14",
    "lifetime": {"hours": 8},
    "lifesize": {"gb": 20},
    "esp": {
        "encryption": ["aes-256-gcm"],
        "authentication": ["sha256"]
    },
    "folder": "Shared"
})
```

### Creating AH-based Profile

```python
ah_profile = client.ipsec_crypto_profile.create({
    "name": "ah-sha-512",
    "dh_group": "group19",
    "lifetime": {"days": 1},
    "ah": {
        "authentication": ["sha512"]
    },
    "folder": "Shared"
})
```

### Updating an Existing Profile

```python
# First fetch the profile
profile = client.ipsec_crypto_profile.fetch(
    name="esp-aes-128-sha1",
    folder="Shared"
)

# Create update model
from scm.models.network import IPsecCryptoProfileUpdateModel

update_model = IPsecCryptoProfileUpdateModel(
    id=profile.id,
    name=profile.name,
    dh_group="group5",  # Updating the DH group
    lifetime={"hours": 24},  # Updating lifetime
    esp={
        "encryption": ["aes-128-cbc", "aes-256-cbc"],  # Adding additional encryption option
        "authentication": ["sha1"]
    },
    folder="Shared"
)

# Update the profile
updated_profile = client.ipsec_crypto_profile.update(update_model)
```

## Error Handling

The IPsec Crypto Profile service can raise several exceptions:

- `InvalidObjectError`: Raised when input data is invalid
- `MissingQueryParameterError`: Raised when a required query parameter is missing
- `APIError`: Raised when an API error occurs

Example of handling errors:

```python
from scm.exceptions import InvalidObjectError, MissingQueryParameterError, APIError

try:
    profile = client.ipsec_crypto_profile.create({
        "name": "invalid-profile",
        # Missing required fields
    })
except InvalidObjectError as e:
    print(f"Invalid data: {e}")
except MissingQueryParameterError as e:
    print(f"Missing parameter: {e}")
except APIError as e:
    print(f"API error: {e}")
```

## Best Practices

1. **Container Validation**:
   - Always provide exactly one of: folder, snippet, or device

2. **Security Protocol Selection**:
   - Choose between ESP (Encapsulating Security Payload) or AH (Authentication Header) based on your security requirements
   - ESP provides both encryption and authentication
   - AH provides authentication only

3. **Algorithm Selection**:
   - Select encryption and authentication algorithms that meet your security requirements
   - Consider using AES-GCM for modern deployments (provides both encryption and authentication)
   - Consider compatibility with connection endpoints

4. **DH Group Selection**:
   - Higher DH group numbers provide stronger security but require more processing power
   - Common choices include group14 (2048-bit), group19 and group20 (NIST elliptic curves)

5. **Lifetime Settings**:
   - Configure appropriate lifetime based on security requirements
   - Balance security (shorter lifetimes) with overhead (more frequent key exchanges)

## See Also

- [IPsec Crypto Profile Models](../../models/network/ipsec_crypto_profile_models.md) - Data models for IPsec crypto profiles
- [IKE Crypto Profiles](ike_crypto_profile.md) - Configure IKE crypto profiles
- [IKE Gateways](ike_gateway.md) - Configure IKE gateways