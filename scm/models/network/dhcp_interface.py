"""DHCP Interface models for Strata Cloud Manager SDK.

Contains Pydantic models for representing DHCP server and relay configurations
on firewall interfaces.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class DhcpServerMode(str, Enum):
    """DHCP server operation modes."""

    AUTO = "auto"
    ENABLED = "enabled"
    DISABLED = "disabled"


class DhcpDualServer(BaseModel):
    """Dual server configuration for DNS, WINS, NIS, and NTP servers."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    primary: Optional[str] = Field(
        None,
        description="Primary server address",
    )
    secondary: Optional[str] = Field(
        None,
        description="Secondary server address",
    )


class DhcpLease(BaseModel):
    """DHCP lease configuration. Only one of unlimited or timeout may be set."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    unlimited: Optional[Dict[str, Any]] = Field(
        None,
        description="Unlimited lease duration",
    )
    timeout: Optional[int] = Field(
        None,
        description="Lease timeout in minutes",
    )

    @model_validator(mode="after")
    def validate_lease_type(self) -> "DhcpLease":
        """Validate that only one of unlimited or timeout is set."""
        if self.unlimited is not None and self.timeout is not None:
            raise ValueError(
                "Only one of 'unlimited' or 'timeout' can be specified in lease configuration"
            )
        return self


class DhcpInheritance(BaseModel):
    """DHCP inheritance configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    source: Optional[str] = Field(
        None,
        description="Inheritance source",
    )


class DhcpReserved(BaseModel):
    """DHCP reserved address entry."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(
        ...,
        description="Reserved address name",
    )
    mac: str = Field(
        ...,
        description="MAC address for the reservation",
    )
    description: Optional[str] = Field(
        None,
        description="Description of the reservation",
    )


class DhcpServerOption(BaseModel):
    """DHCP server option configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    lease: Optional[DhcpLease] = Field(
        None,
        description="Lease configuration",
    )
    inheritance: Optional[DhcpInheritance] = Field(
        None,
        description="Inheritance configuration",
    )
    gateway: Optional[str] = Field(
        None,
        description="Gateway address",
    )
    subnet_mask: Optional[str] = Field(
        None,
        description="Subnet mask",
    )
    dns: Optional[DhcpDualServer] = Field(
        None,
        description="DNS server configuration",
    )
    wins: Optional[DhcpDualServer] = Field(
        None,
        description="WINS server configuration",
    )
    nis: Optional[DhcpDualServer] = Field(
        None,
        description="NIS server configuration",
    )
    ntp: Optional[DhcpDualServer] = Field(
        None,
        description="NTP server configuration",
    )
    pop3_server: Optional[str] = Field(
        None,
        description="POP3 server address",
    )
    smtp_server: Optional[str] = Field(
        None,
        description="SMTP server address",
    )
    dns_suffix: Optional[str] = Field(
        None,
        description="DNS suffix",
    )


class DhcpServer(BaseModel):
    """DHCP server configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    probe_ip: Optional[bool] = Field(
        None,
        description="Enable IP probe before assignment",
    )
    mode: Optional[DhcpServerMode] = Field(
        None,
        description="DHCP server mode",
    )
    option: Optional[DhcpServerOption] = Field(
        None,
        description="DHCP server options",
    )
    ip_pool: Optional[List[str]] = Field(
        None,
        description="List of IP pool ranges",
    )
    reserved: Optional[List[DhcpReserved]] = Field(
        None,
        description="List of reserved address entries",
    )


class DhcpRelayIp(BaseModel):
    """DHCP relay IP configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    enabled: bool = Field(
        True,
        description="Enable DHCP relay",
    )
    server: List[str] = Field(
        ...,
        description="List of DHCP relay server addresses",
    )


class DhcpRelay(BaseModel):
    """DHCP relay configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    ip: DhcpRelayIp = Field(
        ...,
        description="DHCP relay IP configuration",
    )


class DhcpInterfaceBaseModel(BaseModel):
    """Base model for DHCP Interface containing fields common to all operations."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    name: str = Field(
        ...,
        description="The interface name",
    )
    server: Optional[DhcpServer] = Field(
        None,
        description="DHCP server configuration",
    )
    relay: Optional[DhcpRelay] = Field(
        None,
        description="DHCP relay configuration",
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

    @model_validator(mode="after")
    def validate_server_relay_exclusivity(self) -> "DhcpInterfaceBaseModel":
        """Validate that server and relay are mutually exclusive."""
        if self.server is not None and self.relay is not None:
            raise ValueError(
                "Only one of 'server' or 'relay' can be specified for a DHCP interface"
            )
        return self


class DhcpInterfaceCreateModel(DhcpInterfaceBaseModel):
    """Model for creating new DHCP Interface configurations."""

    @model_validator(mode="after")
    def validate_container_type(self) -> "DhcpInterfaceCreateModel":
        """Ensure exactly one container field (folder, snippet, or device) is set.

        Returns:
            DhcpInterfaceCreateModel: The validated model instance.

        Raises:
            ValueError: If zero or more than one container field is set.

        """
        container_fields = ["folder", "snippet", "device"]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


class DhcpInterfaceUpdateModel(DhcpInterfaceBaseModel):
    """Model for updating existing DHCP Interface configurations."""

    id: UUID = Field(
        ...,
        description="The UUID of the DHCP interface configuration",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class DhcpInterfaceResponseModel(DhcpInterfaceBaseModel):
    """Model for DHCP Interface responses."""

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    id: UUID = Field(
        ...,
        description="The UUID of the DHCP interface configuration",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
