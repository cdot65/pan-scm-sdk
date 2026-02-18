"""IPsec Tunnel models for Strata Cloud Manager SDK.

Contains Pydantic models for representing IPsec tunnel objects and related data.
"""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class IkeGatewayRef(BaseModel):
    """Reference to an IKE gateway."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(
        ...,
        description="The name of the IKE gateway",
    )


class PortPair(BaseModel):
    """Local and remote port pair for proxy ID protocol."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    local_port: Optional[int] = Field(
        default=0,
        ge=0,
        le=65535,
        description="Local port number",
    )
    remote_port: Optional[int] = Field(
        default=0,
        ge=0,
        le=65535,
        description="Remote port number",
    )


class ProxyIdProtocol(BaseModel):
    """Protocol configuration for proxy ID."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    number: Optional[int] = Field(
        default=None,
        ge=1,
        le=254,
        description="IP protocol number",
    )
    tcp: Optional[PortPair] = Field(
        default=None,
        description="TCP port pair",
    )
    udp: Optional[PortPair] = Field(
        default=None,
        description="UDP port pair",
    )

    @model_validator(mode="after")
    def validate_single_protocol(self) -> "ProxyIdProtocol":
        """Validate that at most one protocol type is set.

        Returns:
            ProxyIdProtocol: The validated model instance.

        Raises:
            ValueError: If more than one protocol type is set.

        """
        protocol_fields = [self.number, self.tcp, self.udp]
        configured = [f for f in protocol_fields if f is not None]

        if len(configured) > 1:
            raise ValueError("At most one of 'number', 'tcp', or 'udp' can be set")

        return self


class ProxyId(BaseModel):
    """Proxy ID configuration for IPsec tunnel."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(
        ...,
        description="The name of the proxy ID",
    )
    local: Optional[str] = Field(
        default=None,
        description="Local address or subnet",
    )
    remote: Optional[str] = Field(
        default=None,
        description="Remote address or subnet",
    )
    protocol: Optional[ProxyIdProtocol] = Field(
        default=None,
        description="Protocol configuration",
    )


class AutoKey(BaseModel):
    """Auto key configuration for IPsec tunnel."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    ike_gateway: List[IkeGatewayRef] = Field(
        ...,
        description="List of IKE gateway references",
    )
    ipsec_crypto_profile: str = Field(
        ...,
        description="IPsec crypto profile name",
    )
    proxy_id: Optional[List[ProxyId]] = Field(
        default=None,
        description="List of proxy IDs",
    )
    proxy_id_v6: Optional[List[ProxyId]] = Field(
        default=None,
        description="List of IPv6 proxy IDs",
    )


class TunnelMonitor(BaseModel):
    """Tunnel monitor configuration for IPsec tunnel."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    enable: Optional[bool] = Field(
        default=True,
        description="Enable tunnel monitoring",
    )
    destination_ip: str = Field(
        ...,
        description="Destination IP address for tunnel monitoring",
    )
    proxy_id: Optional[str] = Field(
        default=None,
        description="Proxy ID for tunnel monitoring",
    )


class IPsecTunnelBaseModel(BaseModel):
    """Base model for IPsec Tunnels containing fields common to all operations."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    name: str = Field(
        ...,
        description="The name of the IPsec tunnel",
        max_length=63,
    )
    auto_key: AutoKey = Field(
        ...,
        description="Auto key configuration",
    )
    anti_replay: Optional[bool] = Field(
        default=None,
        description="Enable anti-replay protection",
    )
    copy_tos: Optional[bool] = Field(
        default=False,
        description="Copy TOS header",
    )
    enable_gre_encapsulation: Optional[bool] = Field(
        default=False,
        description="Enable GRE encapsulation",
    )
    tunnel_monitor: Optional[TunnelMonitor] = Field(
        default=None,
        description="Tunnel monitor configuration",
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


class IPsecTunnelCreateModel(IPsecTunnelBaseModel):
    """Model for creating new IPsec Tunnels."""

    @model_validator(mode="after")
    def validate_container_type(self) -> "IPsecTunnelCreateModel":
        """Ensure exactly one container field (folder, snippet, or device) is set.

        Returns:
            IPsecTunnelCreateModel: The validated model instance.

        Raises:
            ValueError: If zero or more than one container field is set.

        """
        container_fields = ["folder", "snippet", "device"]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


class IPsecTunnelUpdateModel(IPsecTunnelBaseModel):
    """Model for updating existing IPsec Tunnels."""

    id: UUID = Field(
        ...,
        description="The UUID of the IPsec tunnel",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class IPsecTunnelResponseModel(IPsecTunnelBaseModel):
    """Model for IPsec Tunnel responses."""

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    id: UUID = Field(
        ...,
        description="The UUID of the IPsec tunnel",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
