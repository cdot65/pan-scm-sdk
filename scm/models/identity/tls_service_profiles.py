"""TLS Service Profile models for Strata Cloud Manager SDK.

Contains Pydantic models for representing TLS service profile objects and related data.
"""

# scm/models/identity/tls_service_profiles.py

from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


class TlsVersion(str, Enum):
    """Enumeration of supported TLS protocol versions."""

    tls1_0 = "tls1-0"
    tls1_1 = "tls1-1"
    tls1_2 = "tls1-2"
    tls1_3 = "tls1-3"


class TlsProtocolSettings(BaseModel):
    """TLS protocol and cipher suite configuration.

    Attributes:
        min_version (Optional[TlsVersion]): Minimum TLS version.
        max_version (Optional[TlsVersion]): Maximum TLS version.
        keyxchg_algo_rsa (Optional[bool]): Enable RSA key exchange.
        keyxchg_algo_dhe (Optional[bool]): Enable DHE key exchange.
        keyxchg_algo_ecdhe (Optional[bool]): Enable ECDHE key exchange.
        enc_algo_3des (Optional[bool]): Enable 3DES encryption.
        enc_algo_rc4 (Optional[bool]): Enable RC4 encryption.
        enc_algo_aes_128_cbc (Optional[bool]): Enable AES-128-CBC encryption.
        enc_algo_aes_256_cbc (Optional[bool]): Enable AES-256-CBC encryption.
        enc_algo_aes_128_gcm (Optional[bool]): Enable AES-128-GCM encryption.
        enc_algo_aes_256_gcm (Optional[bool]): Enable AES-256-GCM encryption.
        auth_algo_sha1 (Optional[bool]): Enable SHA1 authentication.
        auth_algo_sha256 (Optional[bool]): Enable SHA256 authentication.
        auth_algo_sha384 (Optional[bool]): Enable SHA384 authentication.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    min_version: Optional[TlsVersion] = Field(
        None,
        description="Minimum TLS version",
    )
    max_version: Optional[TlsVersion] = Field(
        None,
        description="Maximum TLS version",
    )
    keyxchg_algo_rsa: Optional[bool] = Field(
        None,
        description="Enable RSA key exchange",
    )
    keyxchg_algo_dhe: Optional[bool] = Field(
        None,
        description="Enable DHE key exchange",
    )
    keyxchg_algo_ecdhe: Optional[bool] = Field(
        None,
        description="Enable ECDHE key exchange",
    )
    enc_algo_3des: Optional[bool] = Field(
        None,
        description="Enable 3DES encryption",
    )
    enc_algo_rc4: Optional[bool] = Field(
        None,
        description="Enable RC4 encryption",
    )
    enc_algo_aes_128_cbc: Optional[bool] = Field(
        None,
        description="Enable AES-128-CBC encryption",
    )
    enc_algo_aes_256_cbc: Optional[bool] = Field(
        None,
        description="Enable AES-256-CBC encryption",
    )
    enc_algo_aes_128_gcm: Optional[bool] = Field(
        None,
        description="Enable AES-128-GCM encryption",
    )
    enc_algo_aes_256_gcm: Optional[bool] = Field(
        None,
        description="Enable AES-256-GCM encryption",
    )
    auth_algo_sha1: Optional[bool] = Field(
        None,
        description="Enable SHA1 authentication",
    )
    auth_algo_sha256: Optional[bool] = Field(
        None,
        description="Enable SHA256 authentication",
    )
    auth_algo_sha384: Optional[bool] = Field(
        None,
        description="Enable SHA384 authentication",
    )


# Base Model
class TlsServiceProfileBaseModel(BaseModel):
    """Base model for TLS Service Profile containing common fields across all operations.

    Attributes:
        name (str): Profile name.
        certificate (str): Certificate name.
        protocol_settings (Optional[TlsProtocolSettings]): TLS protocol configuration.
        folder (Optional[str]): Folder in which the resource is defined.
        snippet (Optional[str]): Snippet in which the resource is defined.
        device (Optional[str]): Device in which the resource is defined.

    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    name: str = Field(
        ...,
        description="Profile name",
        max_length=127,
        pattern=r"^[a-zA-Z0-9._-]+$",
    )
    certificate: str = Field(
        ...,
        description="Certificate name",
        max_length=255,
    )
    protocol_settings: Optional[TlsProtocolSettings] = Field(
        None,
        description="TLS protocol and cipher suite configuration",
    )

    folder: Optional[str] = Field(
        None,
        description="Folder in which the resource is defined",
        max_length=64,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
    )
    snippet: Optional[str] = Field(
        None,
        description="Snippet in which the resource is defined",
        max_length=64,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
    )
    device: Optional[str] = Field(
        None,
        description="Device in which the resource is defined",
        max_length=64,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
    )


class TlsServiceProfileCreateModel(TlsServiceProfileBaseModel):
    """Model for creating a new TLS Service Profile.

    Inherits from base model and adds create-specific validation.
    """

    @model_validator(mode="after")
    def validate_container_type(self) -> "TlsServiceProfileCreateModel":
        """Ensure exactly one container field (folder, snippet, or device) is set.

        Returns:
            TlsServiceProfileCreateModel: The validated model instance.

        Raises:
            ValueError: If zero or more than one container field is set.

        """
        container_fields = [
            "folder",
            "snippet",
            "device",
        ]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


class TlsServiceProfileUpdateModel(TlsServiceProfileBaseModel):
    """Model for updating an existing TLS Service Profile.

    All fields are optional to allow partial updates.
    """

    id: UUID = Field(
        ...,
        description="Profile ID",
    )


class TlsServiceProfileResponseModel(TlsServiceProfileBaseModel):
    """Model for TLS Service Profile API responses.

    Includes all base fields plus the id field.
    """

    model_config = ConfigDict(
        extra="ignore",
        validate_assignment=True,
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    id: UUID = Field(
        ...,
        description="Profile ID",
    )
