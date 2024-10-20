# scm/models/security/decryption_profiles.py

from typing import List, Optional
from pydantic import (
    BaseModel,
    Field,
    field_validator,
    ConfigDict,
    model_validator,
)
from enum import Enum
import uuid


# Enums
class SSLVersion(str, Enum):
    """Enumeration of SSL/TLS versions."""

    sslv3 = "sslv3"
    tls1_0 = "tls1-0"
    tls1_1 = "tls1-1"
    tls1_2 = "tls1-2"
    tls1_3 = "tls1-3"
    max = "max"


# Define the order of SSL/TLS versions
SSL_VERSIONS_ORDER = [
    "sslv3",
    "tls1-0",
    "tls1-1",
    "tls1-2",
    "tls1-3",
    "max",
]


# Models for ssl_protocol_settings
class SSLProtocolSettings(BaseModel):
    """Represents SSL protocol settings."""

    auth_algo_md5: bool = Field(
        True,
        description="Allow MD5 authentication algorithm",
    )
    auth_algo_sha1: bool = Field(
        True,
        description="Allow SHA1 authentication algorithm",
    )
    auth_algo_sha256: bool = Field(
        True,
        description="Allow SHA256 authentication algorithm",
    )
    auth_algo_sha384: bool = Field(
        True,
        description="Allow SHA384 authentication algorithm",
    )
    enc_algo_3des: bool = Field(
        True,
        description="Allow 3DES encryption algorithm",
    )
    enc_algo_aes_128_cbc: bool = Field(
        True,
        description="Allow AES-128-CBC encryption algorithm",
    )
    enc_algo_aes_128_gcm: bool = Field(
        True,
        description="Allow AES-128-GCM encryption algorithm",
    )
    enc_algo_aes_256_cbc: bool = Field(
        True,
        description="Allow AES-256-CBC encryption algorithm",
    )
    enc_algo_aes_256_gcm: bool = Field(
        True,
        description="Allow AES-256-GCM encryption algorithm",
    )
    enc_algo_chacha20_poly1305: bool = Field(
        True,
        description="Allow ChaCha20-Poly1305 encryption algorithm",
    )
    enc_algo_rc4: bool = Field(
        True,
        description="Allow RC4 encryption algorithm",
    )
    keyxchg_algo_dhe: bool = Field(
        True,
        description="Allow DHE key exchange algorithm",
    )
    keyxchg_algo_ecdhe: bool = Field(
        True,
        description="Allow ECDHE key exchange algorithm",
    )
    keyxchg_algo_rsa: bool = Field(
        True,
        description="Allow RSA key exchange algorithm",
    )
    max_version: SSLVersion = Field(
        SSLVersion.tls1_2,
        description="Maximum allowed SSL/TLS version",
    )
    min_version: SSLVersion = Field(
        SSLVersion.tls1_0,
        description="Minimum allowed SSL/TLS version",
    )

    @model_validator(mode="after")
    def validate_versions(self):
        if SSL_VERSIONS_ORDER.index(self.max_version) < SSL_VERSIONS_ORDER.index(
            self.min_version
        ):
            raise ValueError("max_version cannot be less than min_version")
        return self


# Models for ssl_forward_proxy
class SSLForwardProxy(BaseModel):
    """Represents SSL Forward Proxy settings."""

    auto_include_altname: bool = Field(
        False,
        description="Automatically include alternative names",
    )
    block_client_cert: bool = Field(
        False,
        description="Block client certificate",
    )
    block_expired_certificate: bool = Field(
        False,
        description="Block expired certificates",
    )
    block_timeout_cert: bool = Field(
        False,
        description="Block certificates that have timed out",
    )
    block_tls13_downgrade_no_resource: bool = Field(
        False,
        description="Block TLS 1.3 downgrade when no resource is available",
    )
    block_unknown_cert: bool = Field(
        False,
        description="Block unknown certificates",
    )
    block_unsupported_cipher: bool = Field(
        False,
        description="Block unsupported cipher suites",
    )
    block_unsupported_version: bool = Field(
        False,
        description="Block unsupported SSL/TLS versions",
    )
    block_untrusted_issuer: bool = Field(
        False,
        description="Block untrusted certificate issuers",
    )
    restrict_cert_exts: bool = Field(
        False,
        description="Restrict certificate extensions",
    )
    strip_alpn: bool = Field(
        False,
        description="Strip ALPN (Application-Layer Protocol Negotiation)",
    )


# Models for ssl_inbound_proxy
class SSLInboundProxy(BaseModel):
    """Represents SSL Inbound Proxy settings."""

    block_if_hsm_unavailable: bool = Field(
        False,
        description="Block if HSM (Hardware Security Module) is unavailable",
    )
    block_if_no_resource: bool = Field(
        False,
        description="Block if no resources are available",
    )
    block_unsupported_cipher: bool = Field(
        False,
        description="Block unsupported cipher suites",
    )
    block_unsupported_version: bool = Field(
        False,
        description="Block unsupported SSL/TLS versions",
    )


# Models for ssl_no_proxy
class SSLNoProxy(BaseModel):
    """Represents SSL No Proxy settings."""

    block_expired_certificate: bool = Field(
        False,
        description="Block expired certificates",
    )
    block_untrusted_issuer: bool = Field(
        False,
        description="Block untrusted certificate issuers",
    )


class DecryptionProfileBaseModel(BaseModel):
    """
    Base model for Decryption Profile, containing common fields.
    """

    name: str = Field(
        ...,
        description=(
            "Must start with alphanumeric char and should contain only alphanumeric, "
            "underscore, hyphen, dot or space"
        ),
        pattern=r"^[A-Za-z0-9]{1}[A-Za-z0-9_\-\.\s]{0,}$",
    )
    ssl_forward_proxy: Optional[SSLForwardProxy] = Field(
        None,
        description="SSL Forward Proxy settings",
    )
    ssl_inbound_proxy: Optional[SSLInboundProxy] = Field(
        None,
        description="SSL Inbound Proxy settings",
    )
    ssl_no_proxy: Optional[SSLNoProxy] = Field(
        None,
        description="SSL No Proxy settings",
    )
    ssl_protocol_settings: Optional[SSLProtocolSettings] = Field(
        None,
        description="SSL Protocol settings",
    )


class DecryptionProfileRequestModel(DecryptionProfileBaseModel):
    """
    Represents a Decryption Profile for API requests.
    """

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

    model_config = ConfigDict(validate_assignment=True, arbitrary_types_allowed=True)

    @model_validator(mode="after")
    def validate_container(self) -> "DecryptionProfileRequestModel":
        container_fields = [
            "folder",
            "snippet",
            "device",
        ]
        provided_containers = [
            field for field in container_fields if getattr(self, field) is not None
        ]

        if len(provided_containers) != 1:
            raise ValueError(
                "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            )

        return self


class DecryptionProfileResponseModel(DecryptionProfileBaseModel):
    """
    Represents a Decryption Profile for API responses.
    """

    id: str = Field(
        ...,
        description="UUID of the resource",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
    folder: Optional[str] = Field(
        None,
        description="Folder in which the resource is defined",
    )
    snippet: Optional[str] = Field(
        None,
        description="Snippet in which the resource is defined",
    )
    device: Optional[str] = Field(
        None,
        description="Device in which the resource is defined",
    )

    @field_validator("id")
    def validate_id(cls, v):
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError("Invalid UUID format for 'id'")
        return v


class DecryptionProfilesResponse(BaseModel):
    """
    Represents the API response containing a list of Decryption Profiles.

    Attributes:
        data (List[DecryptionProfileResponseModel]): List of Decryption Profiles.
        offset (int): Offset used in pagination.
        total (int): Total number of profiles available.
        limit (int): Maximum number of profiles returned.
    """

    data: List[DecryptionProfileResponseModel]
    offset: int
    total: int
    limit: int
