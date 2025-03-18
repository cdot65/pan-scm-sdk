# IPsec Crypto Profile Models

## Overview {#Overview}

IPsec Crypto Profile models define the data structures for configuring IPsec VPN encryption and authentication settings in Palo Alto Networks' Strata Cloud Manager. These models provide validation of security protocols, encryption algorithms, authentication methods, and lifetime settings.

## Model Hierarchy

The IPsec Crypto Profile models follow a standard pattern with several related models:

- **Base Model**: `IPsecCryptoProfileBaseModel` - Common attributes for all IPsec crypto profile objects
- **Create Model**: `IPsecCryptoProfileCreateModel` - Used when creating a new IPsec crypto profile
- **Update Model**: `IPsecCryptoProfileUpdateModel` - Used when updating an existing IPsec crypto profile
- **Response Model**: `IPsecCryptoProfileResponseModel` - Returned from API responses

## Data Models

### IPsecCryptoProfileBaseModel

Base model with fields common to all IPsec crypto profile operations.

```python
class IPsecCryptoProfileBaseModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    name: str = Field(
        ...,
        description="Alphanumeric string begin with letter: [0-9a-zA-Z._-]",
        pattern=r"^[0-9a-zA-Z._\-]+$",
        max_length=31,
    )
    dh_group: Optional[DhGroup] = Field(
        default=DhGroup.GROUP2,
        description="Phase-2 DH group (PFS DH group)",
    )
    lifetime: Union[LifetimeSeconds, LifetimeMinutes, LifetimeHours, LifetimeDays] = Field(
        ...,
        description="Lifetime configuration",
    )
    lifesize: Optional[Union[LifesizeKB, LifesizeMB, LifesizeGB, LifesizeTB]] = Field(
        None,
        description="Lifesize configuration",
    )
    esp: Optional[EspConfig] = Field(
        None,
        description="ESP configuration",
    )
    ah: Optional[AhConfig] = Field(
        None,
        description="AH configuration",
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

### IPsecCryptoProfileCreateModel

Model used when creating new IPsec Crypto Profiles.

```python
class IPsecCryptoProfileCreateModel(IPsecCryptoProfileBaseModel):
    """Model for creating new IPsec Crypto Profiles."""

    @model_validator(mode="after")
    def validate_container(self) -> "IPsecCryptoProfileCreateModel":
        """Validate that exactly one container field is provided."""
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

### IPsecCryptoProfileUpdateModel

Model used when updating existing IPsec Crypto Profiles.

```python
class IPsecCryptoProfileUpdateModel(IPsecCryptoProfileBaseModel):
    """Model for updating existing IPsec Crypto Profiles."""

    id: UUID = Field(
        ...,
        description="The UUID of the IPsec crypto profile",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
```

### IPsecCryptoProfileResponseModel

Model representing IPsec Crypto Profile responses from the API.

```python
class IPsecCryptoProfileResponseModel(IPsecCryptoProfileBaseModel):
    """Model for IPsec Crypto Profile responses."""

    id: UUID = Field(
        ...,
        description="The UUID of the IPsec crypto profile",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
```

## Auxiliary Models

### DhGroup Enum

Defines the available Diffie-Hellman groups for IPsec key exchange.

```python
class DhGroup(str, Enum):
    """DH group options for IPsec crypto profiles."""

    NO_PFS = "no-pfs"
    GROUP1 = "group1"
    GROUP2 = "group2"
    GROUP5 = "group5"
    GROUP14 = "group14"
    GROUP19 = "group19"
    GROUP20 = "group20"
```

### ESP Algorithms

Encapsulating Security Payload (ESP) encryption and authentication algorithms.

```python
class EspEncryption(str, Enum):
    """ESP encryption algorithm options."""

    DES = "des"
    TRIPLE_DES = "3des"
    AES_128_CBC = "aes-128-cbc"
    AES_192_CBC = "aes-192-cbc"
    AES_256_CBC = "aes-256-cbc"
    AES_128_GCM = "aes-128-gcm"
    AES_256_GCM = "aes-256-gcm"
    NULL = "null"

class EspAuthentication(str, Enum):
    """ESP authentication algorithm options."""

    MD5 = "md5"
    SHA1 = "sha1"
    SHA256 = "sha256"
    SHA384 = "sha384"
    SHA512 = "sha512"
```

### AH Authentication

Authentication Header (AH) authentication algorithms.

```python
class AhAuthentication(str, Enum):
    """AH authentication algorithm options."""

    MD5 = "md5"
    SHA1 = "sha1"
    SHA256 = "sha256"
    SHA384 = "sha384"
    SHA512 = "sha512"
```

### ESP and AH Configuration Models

```python
class EspConfig(BaseModel):
    """ESP configuration for IPsec crypto profiles."""

    encryption: List[EspEncryption] = Field(
        ...,
        description="Encryption algorithm",
    )
    authentication: List[str] = Field(
        ...,
        description="Authentication algorithm",
    )

class AhConfig(BaseModel):
    """AH configuration for IPsec crypto profiles."""

    authentication: List[AhAuthentication] = Field(
        ...,
        description="Authentication algorithm",
    )
```

### Lifetime Models

Models for specifying IPsec security association lifetimes in different time units.

```python
class LifetimeSeconds(BaseModel):
    """Lifetime specified in seconds."""

    seconds: int = Field(
        ...,
        description="Specify lifetime in seconds",
        ge=180,
        le=65535,
    )

class LifetimeMinutes(BaseModel):
    """Lifetime specified in minutes."""

    minutes: int = Field(
        ...,
        description="Specify lifetime in minutes",
        ge=3,
        le=65535,
    )

class LifetimeHours(BaseModel):
    """Lifetime specified in hours."""

    hours: int = Field(
        ...,
        description="Specify lifetime in hours",
        ge=1,
        le=65535,
    )

class LifetimeDays(BaseModel):
    """Lifetime specified in days."""

    days: int = Field(
        ...,
        description="Specify lifetime in days",
        ge=1,
        le=365,
    )
```

### Lifesize Models

Models for specifying IPsec security association lifesizes in different data units.

```python
class LifesizeKB(BaseModel):
    """Lifesize specified in kilobytes."""

    kb: int = Field(
        ...,
        description="Specify lifesize in kilobytes(KB)",
        ge=1,
        le=65535,
    )

class LifesizeMB(BaseModel):
    """Lifesize specified in megabytes."""

    mb: int = Field(
        ...,
        description="Specify lifesize in megabytes(MB)",
        ge=1,
        le=65535,
    )

class LifesizeGB(BaseModel):
    """Lifesize specified in gigabytes."""

    gb: int = Field(
        ...,
        description="Specify lifesize in gigabytes(GB)",
        ge=1,
        le=65535,
    )

class LifesizeTB(BaseModel):
    """Lifesize specified in terabytes."""

    tb: int = Field(
        ...,
        description="Specify lifesize in terabytes(TB)",
        ge=1,
        le=65535,
    )
```

## Model Validation

The IPsec Crypto Profile models include several validations:

1. **Protocol Validation**: Ensures exactly one of ESP or AH is configured
   ```python
   @model_validator(mode="after")
   def validate_security_protocol(self) -> "IPsecCryptoProfileBaseModel":
       """Validate that exactly one security protocol (ESP or AH) is configured."""
       if self.esp is not None and self.ah is not None:
           raise ValueError("Only one security protocol (ESP or AH) can be configured at a time")

       if self.esp is None and self.ah is None:
           raise ValueError("At least one security protocol (ESP or AH) must be configured")

       return self
   ```

2. **Container Validation**: Ensures exactly one of folder, snippet, or device is provided
   ```python
   @model_validator(mode="after")
   def validate_container(self) -> "IPsecCryptoProfileCreateModel":
       """Validate that exactly one container field is provided."""
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

3. **Name Format Validation**: Ensures name follows the required pattern
   ```python
   name: str = Field(
       ...,
       description="Alphanumeric string begin with letter: [0-9a-zA-Z._-]",
       pattern=r"^[0-9a-zA-Z._\-]+$",
       max_length=31,
   )
   ```

4. **Value Range Validation**: Enforces appropriate ranges for lifetime and lifesize values
   ```python
   seconds: int = Field(
       ...,
       description="Specify lifetime in seconds",
       ge=180,
       le=65535,
   )
   ```

## Usage Examples

### Creating an ESP-based IPsec Crypto Profile

```python
from scm.models.network import (
    IPsecCryptoProfileCreateModel,
    DhGroup,
    EspEncryption,
    LifetimeHours,
    LifesizeGB,
    EspConfig,
)

# Define the lifetime in hours
lifetime = LifetimeHours(hours=8)

# Define the lifesize in gigabytes
lifesize = LifesizeGB(gb=50)

# Define ESP configuration with encryption and authentication
esp_config = EspConfig(
    encryption=[EspEncryption.AES_256_CBC],
    authentication=["sha256"]
)

# Create the IPsec crypto profile model
esp_profile = IPsecCryptoProfileCreateModel(
    name="esp-aes256-sha256",
    dh_group=DhGroup.GROUP14,
    lifetime=lifetime,
    lifesize=lifesize,
    esp=esp_config,
    folder="Shared"
)

# Convert to dictionary for API request
profile_dict = esp_profile.model_dump(exclude_unset=True)
```

### Creating an AH-based IPsec Crypto Profile

```python
from scm.models.network import (
    IPsecCryptoProfileCreateModel,
    DhGroup,
    AhAuthentication,
    LifetimeDays,
    AhConfig,
)

# Define the lifetime in days
lifetime = LifetimeDays(days=1)

# Define AH configuration with authentication
ah_config = AhConfig(
    authentication=[AhAuthentication.SHA512]
)

# Create the IPsec crypto profile model
ah_profile = IPsecCryptoProfileCreateModel(
    name="ah-sha512",
    dh_group=DhGroup.GROUP19,
    lifetime=lifetime,
    ah=ah_config,
    folder="Shared"
)

# Convert to dictionary for API request
profile_dict = ah_profile.model_dump(exclude_unset=True)
```

### Updating an IPsec Crypto Profile

```python
from scm.models.network import (
    IPsecCryptoProfileUpdateModel,
    DhGroup,
    EspEncryption,
    LifetimeMinutes,
    EspConfig,
)
from uuid import UUID

# Define the new lifetime in minutes
lifetime = LifetimeMinutes(minutes=30)

# Define updated ESP configuration
esp_config = EspConfig(
    encryption=[EspEncryption.AES_128_GCM, EspEncryption.AES_256_GCM],
    authentication=["sha1", "sha256"]
)

# Create the update model
update_model = IPsecCryptoProfileUpdateModel(
    id=UUID("123e4567-e89b-12d3-a456-426655440000"),
    name="esp-aes-gcm",
    dh_group=DhGroup.GROUP20,
    lifetime=lifetime,
    esp=esp_config,
    folder="Shared"
)

# Convert to dictionary for API request, excluding unset fields
update_dict = update_model.model_dump(exclude_unset=True)
```

## See Also

- [IPsec Crypto Profile Service](../../config/network/ipsec_crypto_profile.md) - Service for managing IPsec crypto profiles
- [IKE Crypto Profile Models](ike_crypto_profile_models.md) - Data models for IKE crypto profiles
- [IKE Gateway Models](ike_gateway_models.md) - Data models for IKE gateways
