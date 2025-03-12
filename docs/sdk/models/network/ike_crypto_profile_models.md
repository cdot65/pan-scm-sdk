# IKE Crypto Profile Models

The IKE Crypto Profile models provide data validation and serialization for IKE Crypto Profiles in Strata Cloud Manager (SCM).

## Model Imports

```python
from scm.models.network import (
    IKECryptoProfileCreateModel,
    IKECryptoProfileUpdateModel,
    IKECryptoProfileResponseModel,
    HashAlgorithm,
    EncryptionAlgorithm,
    DHGroup,
    LifetimeSeconds,
    LifetimeMinutes,
    LifetimeHours,
    LifetimeDays,
)
```

## Enum Types

### HashAlgorithm

Defines the hash algorithm options for IKE crypto profiles:

```python
class HashAlgorithm(str, Enum):
    MD5 = "md5"
    SHA1 = "sha1"
    SHA256 = "sha256"
    SHA384 = "sha384"
    SHA512 = "sha512"
```

### EncryptionAlgorithm

Defines the encryption algorithm options for IKE crypto profiles:

```python
class EncryptionAlgorithm(str, Enum):
    DES = "des"
    THREE_DES = "3des"
    AES_128_CBC = "aes-128-cbc"
    AES_192_CBC = "aes-192-cbc"
    AES_256_CBC = "aes-256-cbc"
    AES_128_GCM = "aes-128-gcm"
    AES_256_GCM = "aes-256-gcm"
```

### DHGroup

Defines the Diffie-Hellman group options for IKE crypto profiles:

```python
class DHGroup(str, Enum):
    GROUP1 = "group1"
    GROUP2 = "group2"
    GROUP5 = "group5"
    GROUP14 = "group14"
    GROUP19 = "group19"
    GROUP20 = "group20"
```

## Lifetime Models

IKE Crypto Profiles support four different lifetime units. Each has its own model with validation:

### LifetimeSeconds

```python
class LifetimeSeconds(BaseModel):
    seconds: int = Field(
        ...,
        description="Specify lifetime in seconds",
        ge=180,
        le=65535,
    )
```

### LifetimeMinutes

```python
class LifetimeMinutes(BaseModel):
    minutes: int = Field(
        ...,
        description="Specify lifetime in minutes",
        ge=3,
        le=65535,
    )
```

### LifetimeHours

```python
class LifetimeHours(BaseModel):
    hours: int = Field(
        ...,
        description="Specify lifetime in hours",
        ge=1,
        le=65535,
    )
```

### LifetimeDays

```python
class LifetimeDays(BaseModel):
    days: int = Field(
        ...,
        description="Specify lifetime in days",
        ge=1,
        le=365,
    )
```

## Base Model

The `IKECryptoProfileBaseModel` serves as the foundation for all IKE Crypto Profile models:

```python
class IKECryptoProfileBaseModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    name: str = Field(
        ...,
        description="The name of the IKE crypto profile",
        pattern=r"^[0-9a-zA-Z._-]+$",
        max_length=31,
    )
    hash: List[HashAlgorithm] = Field(
        ...,
        description="Hashing algorithms",
    )
    encryption: List[EncryptionAlgorithm] = Field(
        ...,
        description="Encryption algorithms",
    )
    dh_group: List[DHGroup] = Field(
        ...,
        description="Phase-1 DH group",
    )
    lifetime: Optional[LifetimeType] = Field(
        None,
        description="Lifetime configuration",
    )
    authentication_multiple: Optional[int] = Field(
        0,
        description="IKEv2 SA reauthentication interval equals authetication-multiple * rekey-lifetime; 0 means reauthentication disabled",
        ge=0,
        le=50,
    )

    # Container fields
    folder: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        description="The folder in which the resource is defined",
    )
    snippet: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        description="The snippet in which the resource is defined",
    )
    device: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        description="The device in which the resource is defined",
    )
```

## Create Model

Used for creating new IKE Crypto Profiles:

```python
class IKECryptoProfileCreateModel(IKECryptoProfileBaseModel):
    """Model for creating new IKE Crypto Profiles."""

    @model_validator(mode="after")
    def validate_container(self) -> "IKECryptoProfileCreateModel":
        container_fields = ["folder", "snippet", "device"]
        provided = [
            field for field in container_fields if getattr(self, field) is not None
        ]
        if len(provided) != 1:
            raise ValueError(
                "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            )
        return self
```

## Update Model

Used for updating existing IKE Crypto Profiles:

```python
class IKECryptoProfileUpdateModel(IKECryptoProfileBaseModel):
    """Model for updating existing IKE Crypto Profiles."""

    id: UUID = Field(
        ...,
        description="The UUID of the IKE crypto profile",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
```

## Response Model

Represents IKE Crypto Profiles returned from the API:

```python
class IKECryptoProfileResponseModel(IKECryptoProfileBaseModel):
    """Model for IKE Crypto Profile responses."""

    id: UUID = Field(
        ...,
        description="The UUID of the IKE crypto profile",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
```

## Usage Examples

### Creating a Profile

```python
from scm.models.network import (
    IKECryptoProfileCreateModel,
    HashAlgorithm,
    EncryptionAlgorithm,
    DHGroup,
)

# Using the model directly
profile_data = {
    "name": "example-ike-crypto",
    "hash": [HashAlgorithm.SHA1, HashAlgorithm.SHA256],
    "encryption": [
        EncryptionAlgorithm.AES_128_CBC,
        EncryptionAlgorithm.AES_256_CBC
    ],
    "dh_group": [DHGroup.GROUP2, DHGroup.GROUP5],
    "lifetime": {"hours": 8},
    "folder": "Example-Folder",
}

# Create the model and validate
profile_model = IKECryptoProfileCreateModel(**profile_data)

# Access properties
print(f"Profile name: {profile_model.name}")
print(f"Hash algorithms: {[h.value for h in profile_model.hash]}")
```

### Updating a Profile

```python
from scm.models.network import IKECryptoProfileUpdateModel

# Create update model
update_data = {
    "id": "123e4567-e89b-12d3-a456-426655440000",
    "name": "example-ike-crypto",
    "hash": [HashAlgorithm.SHA256, HashAlgorithm.SHA384],
    "encryption": [
        EncryptionAlgorithm.AES_256_CBC,
        EncryptionAlgorithm.AES_256_GCM,
    ],
    "dh_group": [DHGroup.GROUP5, DHGroup.GROUP14],
    "lifetime": {"days": 1},
    "folder": "Example-Folder"
}

update_model = IKECryptoProfileUpdateModel(**update_data)

# Convert model to dict for API request
payload = update_model.model_dump(exclude_unset=True, by_alias=True)
```

### Handling Responses

```python
from scm.models.network import IKECryptoProfileResponseModel

# Parse API response into model
response_data = {
    "id": "123e4567-e89b-12d3-a456-426655440000",
    "name": "example-ike-crypto",
    "hash": ["sha1", "sha256"],
    "encryption": ["aes-128-cbc", "aes-256-cbc"],
    "dh_group": ["group2", "group5"],
    "lifetime": {"hours": 8},
    "folder": "Example-Folder",
}

response_model = IKECryptoProfileResponseModel(**response_data)

# Access model properties
print(f"Profile ID: {response_model.id}")
print(f"Hash algorithms: {[h.value for h in response_model.hash]}")
print(f"Using SHA1: {HashAlgorithm.SHA1 in response_model.hash}")
```
