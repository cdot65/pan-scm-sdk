"""Security Zone models for Strata Cloud Manager SDK.

Contains Pydantic models for representing security zone objects and related data.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class NetworkInterfaceType(str, Enum):
    """Types of network interfaces for security zones."""

    TAP = "tap"
    VIRTUAL_WIRE = "virtual_wire"
    LAYER2 = "layer2"
    LAYER3 = "layer3"
    TUNNEL = "tunnel"
    EXTERNAL = "external"


class UserAcl(BaseModel):
    """User access control list configuration."""

    include_list: Optional[List[str]] = Field(
        default_factory=list,
        description="List of users to include",
    )
    exclude_list: Optional[List[str]] = Field(
        default_factory=list,
        description="List of users to exclude",
    )


class DeviceAcl(BaseModel):
    """Device access control list configuration."""

    include_list: Optional[List[str]] = Field(
        default_factory=list,
        description="List of devices to include",
    )
    exclude_list: Optional[List[str]] = Field(
        default_factory=list,
        description="List of devices to exclude",
    )


class NetworkConfig(BaseModel):
    """Network configuration for security zones."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    zone_protection_profile: Optional[str] = Field(
        None,
        description="Zone protection profile name",
    )
    enable_packet_buffer_protection: Optional[bool] = Field(
        None,
        description="Enable packet buffer protection",
    )
    log_setting: Optional[str] = Field(
        None,
        description="Log setting name",
    )

    # Network interface configurations - only one can be used at a time
    tap: Optional[List[str]] = None
    virtual_wire: Optional[List[str]] = None
    layer2: Optional[List[str]] = None
    layer3: Optional[List[str]] = None
    tunnel: Optional[Dict[str, Any]] = None
    external: Optional[List[str]] = None

    @model_validator(mode="after")
    def validate_network_type(self) -> "NetworkConfig":
        """Validate that only one network interface type is configured."""
        network_types = [
            self.tap,
            self.virtual_wire,
            self.layer2,
            self.layer3,
            self.tunnel,
            self.external,
        ]

        # Filter out None values
        configured_types = [t for t in network_types if t is not None]

        # Check if more than one type is configured
        if len(configured_types) > 1:
            raise ValueError("Only one network interface type can be configured at a time")

        return self


class SecurityZoneBaseModel(BaseModel):
    """Base model for Security Zones containing fields common to all operations."""

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    name: str = Field(
        ...,
        description="The name of the security zone",
        pattern=r"^[0-9a-zA-Z._\- ]+$",  # Pattern includes whitespace
        max_length=63,
    )
    enable_user_identification: Optional[bool] = Field(
        None,
        description="Enable user identification",
    )
    enable_device_identification: Optional[bool] = Field(
        None,
        description="Enable device identification",
    )
    dos_profile: Optional[str] = Field(
        None,
        description="DoS profile name",
    )
    dos_log_setting: Optional[str] = Field(
        None,
        description="DoS log setting name",
    )
    network: Optional[NetworkConfig] = Field(
        None,
        description="Network configuration",
    )
    user_acl: Optional[UserAcl] = Field(
        None,
        description="User access control list",
    )
    device_acl: Optional[DeviceAcl] = Field(
        None,
        description="Device access control list",
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


class SecurityZoneCreateModel(SecurityZoneBaseModel):
    """Model for creating new Security Zones."""

    @model_validator(mode="after")
    def validate_container_type(self) -> "SecurityZoneCreateModel":
        """Ensure exactly one container field (folder, snippet, or device) is set.

        Returns:
            SecurityZoneCreateModel: The validated model instance.

        Raises:
            ValueError: If zero or more than one container field is set.

        """
        container_fields = ["folder", "snippet", "device"]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


class SecurityZoneUpdateModel(SecurityZoneBaseModel):
    """Model for updating existing Security Zones."""

    id: UUID = Field(
        ...,
        description="The UUID of the security zone",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class SecurityZoneResponseModel(SecurityZoneBaseModel):
    """Model for Security Zone responses."""

    id: UUID = Field(
        ...,
        description="The UUID of the security zone",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
