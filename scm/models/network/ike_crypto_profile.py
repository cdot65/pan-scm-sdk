"""IKE Crypto Profile models for Strata Cloud Manager SDK.

Contains Pydantic models for representing IKE crypto profile objects and related data.
"""

from enum import Enum
from typing import List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class HashAlgorithm(str, Enum):
    """Hash algorithm options for IKE crypto profiles."""

    MD5 = "md5"
    SHA1 = "sha1"
    SHA256 = "sha256"
    SHA384 = "sha384"
    SHA512 = "sha512"


class EncryptionAlgorithm(str, Enum):
    """Encryption algorithm options for IKE crypto profiles."""

    DES = "des"
    THREE_DES = "3des"
    AES_128_CBC = "aes-128-cbc"
    AES_192_CBC = "aes-192-cbc"
    AES_256_CBC = "aes-256-cbc"
    AES_128_GCM = "aes-128-gcm"
    AES_256_GCM = "aes-256-gcm"


class DHGroup(str, Enum):
    """Diffie-Hellman group options for IKE crypto profiles."""

    GROUP1 = "group1"
    GROUP2 = "group2"
    GROUP5 = "group5"
    GROUP14 = "group14"
    GROUP19 = "group19"
    GROUP20 = "group20"


class LifetimeSeconds(BaseModel):
    """Lifetime in seconds model."""

    seconds: int = Field(
        ...,
        description="Specify lifetime in seconds",
        ge=180,
        le=65535,
    )


class LifetimeMinutes(BaseModel):
    """Lifetime in minutes model."""

    minutes: int = Field(
        ...,
        description="Specify lifetime in minutes",
        ge=3,
        le=65535,
    )


class LifetimeHours(BaseModel):
    """Lifetime in hours model."""

    hours: int = Field(
        ...,
        description="Specify lifetime in hours",
        ge=1,
        le=65535,
    )


class LifetimeDays(BaseModel):
    """Lifetime in days model."""

    days: int = Field(
        ...,
        description="Specify lifetime in days",
        ge=1,
        le=365,
    )


# Union type for lifetime options
LifetimeType = Union[LifetimeSeconds, LifetimeMinutes, LifetimeHours, LifetimeDays]


class IKECryptoProfileBaseModel(BaseModel):
    """Base model for IKE Crypto Profiles containing fields common to all operations."""

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


class IKECryptoProfileCreateModel(IKECryptoProfileBaseModel):
    """Model for creating new IKE Crypto Profiles."""

    @model_validator(mode="after")
    def validate_container_type(self) -> "IKECryptoProfileCreateModel":
        """Ensure exactly one container field (folder, snippet, or device) is set.

        Returns:
            IKECryptoProfileCreateModel: The validated model instance.

        Raises:
            ValueError: If zero or more than one container field is set.

        """
        container_fields = ["folder", "snippet", "device"]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


class IKECryptoProfileUpdateModel(IKECryptoProfileBaseModel):
    """Model for updating existing IKE Crypto Profiles."""

    id: UUID = Field(
        ...,
        description="The UUID of the IKE crypto profile",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class IKECryptoProfileResponseModel(IKECryptoProfileBaseModel):
    """Model for IKE Crypto Profile responses."""

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        extra="ignore",  # Ignore extra fields that aren't in our model
    )

    id: UUID = Field(
        ...,
        description="The UUID of the IKE crypto profile",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
