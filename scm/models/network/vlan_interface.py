"""Models for VLAN Interface in Palo Alto Networks' Strata Cloud Manager.

This module defines the Pydantic models used for creating, updating, and
representing VLAN Interface resources in the Strata Cloud Manager.
"""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from scm.models.network._interface_common import (
    ArpEntryWithInterface,
    DdnsConfig,
    DhcpClient,
    StaticIpEntry,
)


class VlanInterfaceBaseModel(BaseModel):
    """Base model for VLAN Interface resources containing common fields."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(
        ...,
        description="VLAN interface name",
    )
    default_value: Optional[str] = Field(
        default=None,
        pattern=r"^vlan\.([1-9]\d{0,2}|[1-3]\d{3}|40[0-8]\d|409[0-6])$",
        description="Default interface assignment (e.g., vlan.100)",
    )
    vlan_tag: Optional[str] = Field(
        default=None,
        pattern=r"^([1-9]\d{0,2}|[1-3]\d{3}|40[0-8]\d|409[0-6])$",
        description="VLAN tag (1-4096)",
    )
    comment: Optional[str] = Field(
        default=None,
        description="Interface description/comment",
    )
    mtu: Optional[int] = Field(
        default=None,
        ge=576,
        le=9216,
        description="Maximum transmission unit (MTU)",
    )
    interface_management_profile: Optional[str] = Field(
        default=None,
        description="Interface management profile name",
    )
    ip: Optional[List[StaticIpEntry]] = Field(
        default=None,
        description="List of static IP addresses",
    )
    dhcp_client: Optional[DhcpClient] = Field(
        default=None,
        description="DHCP client configuration",
    )
    arp: Optional[List[ArpEntryWithInterface]] = Field(
        default=None,
        description="Static ARP entries",
    )
    ddns_config: Optional[DdnsConfig] = Field(
        default=None,
        description="Dynamic DNS configuration",
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
    def validate_ip_mode(self) -> "VlanInterfaceBaseModel":
        """Ensure only one IP addressing mode is configured.

        Returns:
            VlanInterfaceBaseModel: The validated model instance.

        Raises:
            ValueError: If both static IP and DHCP are configured.

        """
        if self.ip and self.dhcp_client:
            raise ValueError("Only one IP addressing mode allowed: static IP or DHCP")
        return self


class VlanInterfaceCreateModel(VlanInterfaceBaseModel):
    """Model for creating new VLAN Interface resources."""

    @model_validator(mode="after")
    def validate_container_type(self) -> "VlanInterfaceCreateModel":
        """Ensure exactly one container field is set.

        Returns:
            VlanInterfaceCreateModel: The validated model instance.

        Raises:
            ValueError: If zero or more than one container field is set.

        """
        container_fields = ["folder", "snippet", "device"]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


class VlanInterfaceUpdateModel(VlanInterfaceBaseModel):
    """Model for updating existing VLAN Interface resources."""

    id: UUID = Field(
        ...,
        description="The UUID of the VLAN interface",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class VlanInterfaceResponseModel(VlanInterfaceBaseModel):
    """Model for VLAN Interface responses from the API."""

    id: UUID = Field(
        ...,
        description="The UUID of the VLAN interface",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
