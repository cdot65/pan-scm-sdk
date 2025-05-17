"""IKE Gateway models for Strata Cloud Manager SDK.

Contains Pydantic models for representing IKE gateway objects and related data.
"""

from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PeerIdType(str, Enum):
    """Types of peer IDs supported for IKE Gateway authentication."""

    IPADDR = "ipaddr"
    KEYID = "keyid"
    FQDN = "fqdn"
    UFQDN = "ufqdn"


class LocalIdType(str, Enum):
    """Types of local IDs supported for IKE Gateway authentication."""

    IPADDR = "ipaddr"
    KEYID = "keyid"
    FQDN = "fqdn"
    UFQDN = "ufqdn"


class ProtocolVersion(str, Enum):
    """IKE protocol versions supported."""

    IKEV2_PREFERRED = "ikev2-preferred"
    IKEV1 = "ikev1"
    IKEV2 = "ikev2"


class PreSharedKey(BaseModel):
    """Pre-shared key authentication configuration."""

    key: str = Field(
        ...,
        description="Pre-shared key for authentication",
        json_schema_extra={"format": "password"},
    )


class CertificateAuth(BaseModel):
    """Certificate-based authentication configuration."""

    allow_id_payload_mismatch: Optional[bool] = Field(
        None,
        description="Allow ID payload mismatch",
    )
    certificate_profile: Optional[str] = Field(
        None,
        description="Certificate profile name",
    )
    local_certificate: Optional[Dict[str, Any]] = Field(
        None,
        description="Local certificate configuration",
    )
    strict_validation_revocation: Optional[bool] = Field(
        None,
        description="Enable strict validation revocation",
    )
    use_management_as_source: Optional[bool] = Field(
        None,
        description="Use management interface as source",
    )


class Authentication(BaseModel):
    """Authentication configuration for IKE Gateway."""

    pre_shared_key: Optional[PreSharedKey] = Field(
        None,
        description="Pre-shared key authentication",
    )
    certificate: Optional[CertificateAuth] = Field(
        None,
        description="Certificate-based authentication",
    )

    @model_validator(mode="after")
    def validate_auth_method(self) -> "Authentication":
        """Validate that only one authentication method is configured."""
        if self.pre_shared_key is not None and self.certificate is not None:
            raise ValueError(
                "Only one authentication method can be configured: pre_shared_key or certificate"
            )
        if self.pre_shared_key is None and self.certificate is None:
            raise ValueError(
                "At least one authentication method must be provided: pre_shared_key or certificate"
            )
        return self


class PeerId(BaseModel):
    """Peer identification configuration."""

    type: PeerIdType = Field(
        ...,
        description="Type of peer ID",
    )
    id: str = Field(
        ...,
        description="Peer ID string",
        pattern=r"^(.+\@[\*a-zA-Z0-9.-]+)$|^([\*$a-zA-Z0-9_:.-]+)$|^(([[:xdigit:]][[:xdigit:]])+)$|^([a-zA-Z0-9.]+=(\\,|[^,])+[, ]+)*([a-zA-Z0-9.]+=(\\,|[^,])+)$",
        min_length=1,
        max_length=1024,
    )


class LocalId(BaseModel):
    """Local identification configuration."""

    type: LocalIdType = Field(
        ...,
        description="Type of local ID",
    )
    id: str = Field(
        ...,
        description="Local ID string",
        pattern=r"^(.+\@[a-zA-Z0-9.-]+)$|^([$a-zA-Z0-9_:.-]+)$|^(([[:xdigit:]][[:xdigit:]])+)$|^([a-zA-Z0-9.]+=(\\,|[^,])+[, ]+)*([a-zA-Z0-9.]+=(\\,|[^,])+)$",
        min_length=1,
        max_length=1024,
    )


class DeadPeerDetection(BaseModel):
    """Dead Peer Detection (DPD) configuration."""

    enable: Optional[bool] = Field(
        None,
        description="Enable Dead Peer Detection",
    )


class IKEv1(BaseModel):
    """IKEv1 protocol configuration."""

    ike_crypto_profile: Optional[str] = Field(
        None,
        description="IKE Crypto Profile name for IKEv1",
    )
    dpd: Optional[DeadPeerDetection] = Field(
        None,
        description="Dead Peer Detection configuration",
    )


class IKEv2(BaseModel):
    """IKEv2 protocol configuration."""

    ike_crypto_profile: Optional[str] = Field(
        None,
        description="IKE Crypto Profile name for IKEv2",
    )
    dpd: Optional[DeadPeerDetection] = Field(
        None,
        description="Dead Peer Detection configuration",
    )


class Protocol(BaseModel):
    """IKE protocol configuration."""

    ikev1: Optional[IKEv1] = Field(
        None,
        description="IKEv1 configuration",
    )
    ikev2: Optional[IKEv2] = Field(
        None,
        description="IKEv2 configuration",
    )
    version: Optional[ProtocolVersion] = Field(
        ProtocolVersion.IKEV2_PREFERRED,
        description="IKE protocol version preference",
    )

    @model_validator(mode="after")
    def validate_protocol_config(self) -> "Protocol":
        """Validate protocol configuration based on version selection."""
        if self.version == ProtocolVersion.IKEV1 and self.ikev1 is None:
            raise ValueError("IKEv1 configuration is required when version is set to ikev1")
        if self.version == ProtocolVersion.IKEV2 and self.ikev2 is None:
            raise ValueError("IKEv2 configuration is required when version is set to ikev2")
        if (
            self.version == ProtocolVersion.IKEV2_PREFERRED
            and self.ikev1 is None
            and self.ikev2 is None
        ):
            raise ValueError(
                "Either IKEv1 or IKEv2 configuration must be provided when version is ikev2-preferred"
            )
        return self


class NatTraversal(BaseModel):
    """NAT traversal configuration."""

    enable: Optional[bool] = Field(
        None,
        description="Enable NAT traversal",
    )


class Fragmentation(BaseModel):
    """IKE fragmentation configuration."""

    enable: bool = Field(
        False,
        description="Enable IKE fragmentation",
    )


class ProtocolCommon(BaseModel):
    """Common protocol configuration for IKE Gateway."""

    nat_traversal: Optional[NatTraversal] = Field(
        None,
        description="NAT traversal configuration",
    )
    passive_mode: Optional[bool] = Field(
        None,
        description="Enable passive mode",
    )
    fragmentation: Optional[Fragmentation] = Field(
        None,
        description="IKE fragmentation configuration",
    )


class IpAddress(BaseModel):
    """IP address configuration for peer."""

    ip: str = Field(
        ...,
        description="Static IP address of peer gateway",
    )


class FqdnAddress(BaseModel):
    """FQDN configuration for peer."""

    fqdn: str = Field(
        ...,
        description="FQDN of peer gateway",
        max_length=255,
    )


class DynamicAddress(BaseModel):
    """Dynamic address configuration for peer."""

    dynamic: Dict[str, Any] = Field(
        default_factory=dict,
        description="Dynamic peer address configuration",
    )


class PeerAddress(BaseModel):
    """Peer address configuration for IKE Gateway."""

    ip: Optional[str] = Field(
        None,
        description="Static IP address of peer gateway",
    )
    fqdn: Optional[str] = Field(
        None,
        description="FQDN of peer gateway",
        max_length=255,
    )
    dynamic: Optional[Dict[str, Any]] = Field(
        None,
        description="Dynamic peer address configuration",
    )

    @model_validator(mode="after")
    def validate_peer_address(self) -> "PeerAddress":
        """Validate that only one peer address type is configured."""
        configured_types = [
            self.ip,
            self.fqdn,
            self.dynamic,
        ]
        filled_types = [t for t in configured_types if t is not None]

        if len(filled_types) != 1:
            raise ValueError(
                "Exactly one peer address type must be configured: ip, fqdn, or dynamic"
            )
        return self


class IKEGatewayBaseModel(BaseModel):
    """Base model for IKE Gateway containing fields common to all operations."""

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    name: str = Field(
        ...,
        description="The name of the IKE Gateway",
        pattern=r"^[0-9a-zA-Z._\-]+$",
        max_length=63,
    )
    authentication: Authentication = Field(
        ...,
        description="Authentication configuration",
    )
    peer_id: Optional[PeerId] = Field(
        None,
        description="Peer identification",
    )
    local_id: Optional[LocalId] = Field(
        None,
        description="Local identification",
    )
    protocol: Protocol = Field(
        ...,
        description="IKE protocol configuration",
    )
    protocol_common: Optional[ProtocolCommon] = Field(
        None,
        description="Common protocol configuration",
    )
    peer_address: PeerAddress = Field(
        ...,
        description="Peer address configuration",
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


class IKEGatewayCreateModel(IKEGatewayBaseModel):
    """Model for creating new IKE Gateways."""

    @model_validator(mode="after")
    def validate_container_type(self) -> "IKEGatewayCreateModel":
        """Ensure exactly one container field (folder, snippet, or device) is set.

        Returns:
            IKEGatewayCreateModel: The validated model instance.

        Raises:
            ValueError: If zero or more than one container field is set.

        """
        container_fields = ["folder", "snippet", "device"]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


class IKEGatewayUpdateModel(IKEGatewayBaseModel):
    """Model for updating existing IKE Gateways."""

    id: UUID = Field(
        ...,
        description="The UUID of the IKE Gateway",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class IKEGatewayResponseModel(IKEGatewayBaseModel):
    """Model for IKE Gateway responses."""

    id: UUID = Field(
        ...,
        description="The UUID of the IKE Gateway",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
