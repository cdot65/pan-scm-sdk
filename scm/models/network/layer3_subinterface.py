"""Models for Layer3 Subinterface in Palo Alto Networks' Strata Cloud Manager.

This module defines the Pydantic models used for creating, updating, and
representing Layer3 Subinterface resources in the Strata Cloud Manager.
"""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from scm.models.network._interface_common import ArpEntry, DdnsConfig, DhcpClient, StaticIpEntry


class Layer3SubinterfaceBaseModel(BaseModel):
    """Base model for Layer3 Subinterface resources containing common fields."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(
        ...,
        description="Layer3 subinterface name (e.g., ethernet1/1.100)",
    )
    tag: Optional[int] = Field(
        default=None,
        ge=1,
        le=4096,
        description="VLAN tag (1-4096)",
    )
    parent_interface: Optional[str] = Field(
        default=None,
        description="Parent interface name",
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
    arp: Optional[List[ArpEntry]] = Field(
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
    def validate_ip_mode(self) -> "Layer3SubinterfaceBaseModel":
        """Ensure only one IP addressing mode is configured.

        Returns:
            Layer3SubinterfaceBaseModel: The validated model instance.

        Raises:
            ValueError: If both static IP and DHCP are configured.

        """
        if self.ip and self.dhcp_client:
            raise ValueError("Only one IP addressing mode allowed: static IP or DHCP")
        return self


class Layer3SubinterfaceCreateModel(Layer3SubinterfaceBaseModel):
    """Model for creating new Layer3 Subinterface resources."""

    @model_validator(mode="after")
    def validate_container_type(self) -> "Layer3SubinterfaceCreateModel":
        """Ensure exactly one container field is set.

        Returns:
            Layer3SubinterfaceCreateModel: The validated model instance.

        Raises:
            ValueError: If zero or more than one container field is set.

        """
        container_fields = ["folder", "snippet", "device"]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


class Layer3SubinterfaceUpdateModel(Layer3SubinterfaceBaseModel):
    """Model for updating existing Layer3 Subinterface resources."""

    id: UUID = Field(
        ...,
        description="The UUID of the layer3 subinterface",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class Layer3SubinterfaceResponseModel(Layer3SubinterfaceBaseModel):
    """Model for Layer3 Subinterface responses from the API."""

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
    )

    id: UUID = Field(
        ...,
        description="The UUID of the layer3 subinterface",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
