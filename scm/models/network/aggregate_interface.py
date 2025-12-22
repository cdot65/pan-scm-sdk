"""Models for Aggregate Interface in Palo Alto Networks' Strata Cloud Manager.

This module defines the Pydantic models used for creating, updating, and
representing Aggregate Interface resources in the Strata Cloud Manager.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from scm.models.network._interface_common import (
    ArpEntry,
    DdnsConfig,
    DhcpClient,
    LacpConfig,
    StaticIpEntry,
)


class AggregateLayer2(BaseModel):
    """Layer2 configuration for aggregate interfaces."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    vlan_tag: Optional[str] = Field(
        default=None,
        pattern=r"^([1-9]\d{0,2}|[1-3]\d{3}|40[0-8]\d|409[0-6])$",
        description="VLAN tag (1-4096)",
    )
    lacp: Optional[LacpConfig] = Field(
        default=None,
        description="LACP configuration",
    )


class AggregateLayer3(BaseModel):
    """Layer3 configuration for aggregate interfaces."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    ip: Optional[List[StaticIpEntry]] = Field(
        default=None,
        description="List of static IP addresses",
    )
    dhcp_client: Optional[DhcpClient] = Field(
        default=None,
        description="DHCP client configuration",
    )
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
    lacp: Optional[LacpConfig] = Field(
        default=None,
        description="LACP configuration",
    )

    @model_validator(mode="after")
    def validate_ip_mode(self) -> "AggregateLayer3":
        """Ensure only one IP addressing mode is configured.

        Returns:
            AggregateLayer3: The validated model instance.

        Raises:
            ValueError: If both static IP and DHCP are configured.

        """
        if self.ip and self.dhcp_client:
            raise ValueError("Only one IP addressing mode allowed: static IP or DHCP")
        return self


class AggregateInterfaceBaseModel(BaseModel):
    """Base model for Aggregate Interface resources containing common fields."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(
        ...,
        description="Aggregate interface name",
    )
    default_value: Optional[str] = Field(
        default=None,
        description="Default interface assignment",
    )
    comment: Optional[str] = Field(
        default=None,
        max_length=1023,
        description="Interface description/comment",
    )
    layer2: Optional[AggregateLayer2] = Field(
        default=None,
        description="Layer2 configuration",
    )
    layer3: Optional[AggregateLayer3] = Field(
        default=None,
        description="Layer3 configuration",
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
    def validate_interface_mode(self) -> "AggregateInterfaceBaseModel":
        """Ensure only one interface mode is configured.

        Returns:
            AggregateInterfaceBaseModel: The validated model instance.

        Raises:
            ValueError: If more than one interface mode is configured.

        """
        modes = [self.layer2, self.layer3]
        configured = [m for m in modes if m is not None]
        if len(configured) > 1:
            raise ValueError("Only one interface mode allowed: layer2 or layer3")
        return self


class AggregateInterfaceCreateModel(AggregateInterfaceBaseModel):
    """Model for creating new Aggregate Interface resources."""

    @model_validator(mode="after")
    def validate_container_type(self) -> "AggregateInterfaceCreateModel":
        """Ensure exactly one container field is set.

        Returns:
            AggregateInterfaceCreateModel: The validated model instance.

        Raises:
            ValueError: If zero or more than one container field is set.

        """
        container_fields = ["folder", "snippet", "device"]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


class AggregateInterfaceUpdateModel(AggregateInterfaceBaseModel):
    """Model for updating existing Aggregate Interface resources."""

    id: UUID = Field(
        ...,
        description="The UUID of the aggregate interface",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class AggregateInterfaceResponseModel(AggregateInterfaceBaseModel):
    """Model for Aggregate Interface responses from the API."""

    id: UUID = Field(
        ...,
        description="The UUID of the aggregate interface",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
