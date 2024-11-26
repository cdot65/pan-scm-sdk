# scm/models/security/dns_security_profiles.py

from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    Field,
    model_validator,
    ConfigDict,
    RootModel,
)


# Enums
class ActionEnum(str, Enum):
    """Enumeration of allowed actions for DNS security categories."""

    default = "default"
    allow = "allow"
    block = "block"
    sinkhole = "sinkhole"


class LogLevelEnum(str, Enum):
    """Enumeration of log levels."""

    default = "default"
    none = "none"
    low = "low"
    informational = "informational"
    medium = "medium"
    high = "high"
    critical = "critical"


class PacketCaptureEnum(str, Enum):
    """Enumeration of packet capture options."""

    disable = "disable"
    single_packet = "single-packet"
    extended_capture = "extended-capture"


class IPv4AddressEnum(str, Enum):
    """Enumeration of allowed IPv4 sinkhole addresses."""

    default_ip = "pan-sinkhole-default-ip"
    localhost = "127.0.0.1"


class IPv6AddressEnum(str, Enum):
    """Enumeration of allowed IPv6 sinkhole addresses."""

    localhost = "::1"


# Component Models
class ListActionBaseModel(RootModel[dict]):
    """Base class for list actions with common validation logic."""

    def get_action_name(self) -> str:
        return next(iter(self.root.keys()), "unknown")


class ListActionRequestModel(ListActionBaseModel):
    """Action field validator for requests requiring exactly one action."""

    @model_validator(mode="before")
    def check_and_transform_action(cls, values):
        if isinstance(values, str):
            values = {values: {}}
        elif not isinstance(values, dict):
            raise ValueError("Invalid action format; must be a string or dict.")

        action_fields = ["alert", "allow", "block", "sinkhole"]
        provided_actions = [field for field in action_fields if field in values]

        if len(provided_actions) != 1:
            raise ValueError("Exactly one action must be provided in 'action' field.")

        action_name = provided_actions[0]
        if values[action_name] != {}:
            raise ValueError(f"Action '{action_name}' does not take any parameters.")

        return values


class DNSSecurityCategoryEntryModel(BaseModel):
    """DNS Security Category configuration."""

    name: str = Field(
        ...,
        description="DNS Security Category Name",
    )
    action: ActionEnum = Field(
        default=ActionEnum.default,
        description="Action to be taken",
    )
    log_level: Optional[LogLevelEnum] = Field(
        default=LogLevelEnum.default,
        description="Log level",
    )
    packet_capture: Optional[PacketCaptureEnum] = Field(
        None,
        description="Packet capture setting",
    )


class ListEntryBaseModel(BaseModel):
    """Base configuration for list entries."""

    name: str = Field(
        ...,
        description="List name",
    )
    packet_capture: Optional[PacketCaptureEnum] = Field(
        None,
        description="Packet capture setting",
    )
    action: ListActionRequestModel = Field(
        ...,
        description="Action",
    )


class SinkholeSettingsModel(BaseModel):
    """Sinkhole configuration settings."""

    ipv4_address: IPv4AddressEnum = Field(
        ...,
        description="IPv4 address for sinkhole",
    )
    ipv6_address: IPv6AddressEnum = Field(
        ...,
        description="IPv6 address for sinkhole",
    )


class WhitelistEntryModel(BaseModel):
    """Whitelist entry configuration."""

    name: str = Field(
        ...,
        description="DNS domain or FQDN to be whitelisted",
    )
    description: Optional[str] = Field(
        None,
        description="Description",
    )


class BotnetDomainsModel(BaseModel):
    """Botnet domains configuration."""

    dns_security_categories: Optional[List[DNSSecurityCategoryEntryModel]] = Field(
        None,
        description="DNS security categories",
    )
    lists: Optional[List[ListEntryBaseModel]] = Field(
        None,
        description="Lists of DNS domains",
    )
    sinkhole: Optional[SinkholeSettingsModel] = Field(
        None,
        description="DNS sinkhole settings",
    )
    whitelist: Optional[List[WhitelistEntryModel]] = Field(
        None,
        description="DNS security overrides",
    )


class DNSSecurityProfileBaseModel(BaseModel):
    """Base model for DNS Security Profile containing common fields."""

    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    name: str = Field(
        ...,
        description="Profile name",
        pattern=r"^[a-zA-Z0-9][a-zA-Z0-9_\-\.\s]*$",
    )
    description: Optional[str] = Field(
        None,
        description="Description",
    )
    botnet_domains: Optional[BotnetDomainsModel] = Field(
        None,
        description="Botnet domains settings",
    )
    folder: Optional[str] = Field(
        None,
        description="Folder",
        max_length=64,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
    )
    snippet: Optional[str] = Field(
        None,
        description="Snippet",
        max_length=64,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
    )
    device: Optional[str] = Field(
        None,
        description="Device",
        max_length=64,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
    )


class DNSSecurityProfileCreateModel(DNSSecurityProfileBaseModel):
    """Model for creating a new DNS Security Profile."""

    @model_validator(mode="after")
    def validate_container(self) -> "DNSSecurityProfileCreateModel":
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


class DNSSecurityProfileUpdateModel(DNSSecurityProfileBaseModel):
    """Model for updating an existing DNS Security Profile."""

    id: Optional[UUID] = Field(
        ...,
        description="UUID of the resource",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class DNSSecurityProfileResponseModel(DNSSecurityProfileBaseModel):
    """Model for DNS Security Profile API responses."""

    id: UUID = Field(
        ...,
        description="UUID of the resource",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
