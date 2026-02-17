"""Models for Ethernet Interface in Palo Alto Networks' Strata Cloud Manager.

This module defines the Pydantic models used for creating, updating, and
representing Ethernet Interface resources in the Strata Cloud Manager.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from scm.models.network._interface_common import (
    AdjustTcpMss,
    ArpEntry,
    BonjourConfig,
    DdnsConfig,
    DhcpClient,
    Ipv6ConfigExtended,
    LldpConfig,
    NdpProxyConfig,
    PoeConfig,
    PppoeConfig,
    StaticIpEntry,
)


class EthernetLayer2(BaseModel):
    """Layer2 configuration for ethernet interfaces."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    vlan_tag: Optional[str] = Field(
        default=None,
        pattern=r"^([1-9]\d{0,2}|[1-3]\d{3}|40[0-8]\d|409[0-6])$",
        description="VLAN tag (1-4096)",
    )
    lldp: Optional[LldpConfig] = Field(
        default=None,
        description="LLDP configuration",
    )


class EthernetLayer3(BaseModel):
    """Layer3 configuration for ethernet interfaces."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    # IP addressing modes (oneOf)
    ip: Optional[List[StaticIpEntry]] = Field(
        default=None,
        description="List of static IP addresses",
    )
    dhcp_client: Optional[DhcpClient] = Field(
        default=None,
        description="DHCP client configuration",
    )
    pppoe: Optional[PppoeConfig] = Field(
        default=None,
        description="PPPoE configuration",
    )

    # Common layer3 fields
    mtu: Optional[int] = Field(
        default=1500,
        ge=576,
        le=9216,
        description="Maximum transmission unit (MTU)",
    )
    interface_management_profile: Optional[str] = Field(
        default=None,
        max_length=31,
        description="Interface management profile name",
    )
    arp: Optional[List[ArpEntry]] = Field(
        default=None,
        description="Static ARP entries",
    )
    ddns_config: Optional[DdnsConfig] = Field(
        default=None,
        description="Dynamic DNS configuration",
    )

    # Additional layer3 fields
    adjust_tcp_mss: Optional[AdjustTcpMss] = Field(
        default=None,
        description="TCP MSS adjustment configuration",
    )
    bonjour: Optional[BonjourConfig] = Field(
        default=None,
        description="Bonjour/mDNS configuration",
    )
    ipv6: Optional[Ipv6ConfigExtended] = Field(
        default=None,
        description="IPv6 configuration",
    )
    lldp: Optional[LldpConfig] = Field(
        default=None,
        description="LLDP configuration",
    )
    ndp_proxy: Optional[NdpProxyConfig] = Field(
        default=None,
        description="NDP proxy configuration",
    )
    untagged_sub_interface: Optional[bool] = Field(
        default=None,
        description="Enable untagged subinterface",
    )

    @model_validator(mode="after")
    def validate_ip_mode(self) -> "EthernetLayer3":
        """Ensure only one IP addressing mode is configured.

        Returns:
            EthernetLayer3: The validated model instance.

        Raises:
            ValueError: If more than one IP addressing mode is configured.

        """
        modes = [self.ip, self.dhcp_client, self.pppoe]
        configured = [m for m in modes if m is not None]
        if len(configured) > 1:
            raise ValueError("Only one IP addressing mode allowed: static IP, DHCP, or PPPoE")
        return self


class EthernetTap(BaseModel):
    """TAP mode configuration for ethernet interfaces."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )


class EthernetInterfaceBaseModel(BaseModel):
    """Base model for Ethernet Interface resources containing common fields."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(
        ...,
        pattern=r"^\$[a-zA-Z0-9_\-]+$",
        max_length=63,
        description="Ethernet interface variable name (must start with $)",
    )
    default_value: Optional[str] = Field(
        default=None,
        pattern=r"^ethernet\d+/\d+(\.\d+)?$",
        description="Physical interface assignment (e.g., ethernet1/1)",
    )
    comment: Optional[str] = Field(
        default=None,
        max_length=1023,
        description="Interface description/comment",
    )

    # Link configuration
    link_speed: Optional[str] = Field(
        default="auto",
        pattern=r"^(auto|10|100|1000|10000|40000|100000)$",
        description="Link speed",
    )
    link_duplex: Optional[str] = Field(
        default="auto",
        pattern=r"^(auto|half|full)$",
        description="Link duplex",
    )
    link_state: Optional[str] = Field(
        default="auto",
        pattern=r"^(auto|up|down)$",
        description="Link state",
    )

    # Power over Ethernet
    poe: Optional[PoeConfig] = Field(
        default=None,
        description="Power over Ethernet configuration",
    )

    # Interface modes (oneOf)
    layer2: Optional[EthernetLayer2] = Field(
        default=None,
        description="Layer2 configuration",
    )
    layer3: Optional[EthernetLayer3] = Field(
        default=None,
        description="Layer3 configuration",
    )
    tap: Optional[EthernetTap] = Field(
        default=None,
        description="TAP mode configuration",
    )

    # Container fields
    folder: Optional[str] = Field(
        default=None,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        description="The folder in which the resource is defined",
    )
    snippet: Optional[str] = Field(
        default=None,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        description="The snippet in which the resource is defined",
    )
    device: Optional[str] = Field(
        default=None,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        description="The device in which the resource is defined",
    )

    @model_validator(mode="after")
    def validate_interface_mode(self) -> "EthernetInterfaceBaseModel":
        """Ensure only one interface mode is configured.

        Returns:
            EthernetInterfaceBaseModel: The validated model instance.

        Raises:
            ValueError: If more than one interface mode is configured.

        """
        modes = [self.layer2, self.layer3, self.tap]
        configured = [m for m in modes if m is not None]
        if len(configured) > 1:
            raise ValueError("Only one interface mode allowed: layer2, layer3, or tap")
        return self


class EthernetInterfaceCreateModel(EthernetInterfaceBaseModel):
    """Model for creating new Ethernet Interface resources."""

    @model_validator(mode="after")
    def validate_container_type(self) -> "EthernetInterfaceCreateModel":
        """Ensure exactly one container field is set.

        Returns:
            EthernetInterfaceCreateModel: The validated model instance.

        Raises:
            ValueError: If zero or more than one container field is set.

        """
        container_fields = ["folder", "snippet", "device"]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


class EthernetInterfaceUpdateModel(EthernetInterfaceBaseModel):
    """Model for updating existing Ethernet Interface resources."""

    id: UUID = Field(
        ...,
        description="The UUID of the ethernet interface",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class EthernetInterfaceResponseModel(EthernetInterfaceBaseModel):
    """Model for Ethernet Interface responses from the API."""

    id: UUID = Field(
        ...,
        description="The UUID of the ethernet interface",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
