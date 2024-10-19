# scm/models/security/dns_security_profiles.py

from typing import List, Optional
from pydantic import (
    BaseModel,
    Field,
    model_validator,
    field_validator,
    ConfigDict,
    RootModel,
)
from enum import Enum
import uuid


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


# Action classes for 'lists' entries
class ListActionRequest(RootModel[dict]):
    """
    Represents the 'action' field in 'lists' entries for requests.
    Enforces that exactly one action is provided.
    """

    @model_validator(mode="before")
    @classmethod
    def check_and_transform_action(cls, values):
        if isinstance(values, str):
            values = {values: {}}
        elif not isinstance(values, dict):
            raise ValueError("Invalid action format; must be a string or dict.")

        action_fields = [
            "alert",
            "allow",
            "block",
            "sinkhole",
        ]

        provided_actions = [field for field in action_fields if field in values]

        if len(provided_actions) != 1:
            raise ValueError("Exactly one action must be provided in 'action' field.")

        action_name = provided_actions[0]
        action_value = values[action_name]

        if action_value != {}:
            raise ValueError(f"Action '{action_name}' does not take any parameters.")

        return values

    def get_action_name(self) -> str:
        return next(iter(self.root.keys()), "unknown")


class ListActionResponse(RootModel[dict]):
    """
    Represents the 'action' field in 'lists' entries for responses.
    Accepts empty dictionaries.
    """

    @model_validator(mode="before")
    @classmethod
    def check_action(cls, values):
        if isinstance(values, str):
            values = {values: {}}
        elif not isinstance(values, dict):
            raise ValueError("Invalid action format; must be a string or dict.")

        action_fields = [
            "alert",
            "allow",
            "block",
            "sinkhole",
        ]

        provided_actions = [field for field in action_fields if field in values]

        if len(provided_actions) > 1:
            raise ValueError("At most one action must be provided in 'action' field.")

        if provided_actions:
            action_name = provided_actions[0]
            action_value = values[action_name]

            if action_value != {}:
                raise ValueError(
                    f"Action '{action_name}' does not take any parameters."
                )
        else:
            # Accept empty dicts (no action specified)
            if values != {}:
                raise ValueError("Invalid action format.")

        return values

    def get_action_name(self) -> str:
        return next(iter(self.root.keys()), "unknown")


# Model for DNS Security Categories
class DNSSecurityCategoryEntry(BaseModel):
    """
    Represents an entry in 'dns_security_categories'.
    """

    name: str = Field(..., description="DNS Security Category Name")
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


# Models for 'lists' entries
class ListEntryBase(BaseModel):
    """
    Base class for 'lists' entries.
    """

    name: str = Field(..., description="List name")
    packet_capture: Optional[PacketCaptureEnum] = Field(
        None,
        description="Packet capture setting",
    )


class ListEntryRequest(ListEntryBase):
    """
    Represents a 'lists' entry for requests.
    """

    action: ListActionRequest = Field(..., description="Action")


class ListEntryResponse(ListEntryBase):
    """
    Represents a 'lists' entry for responses.
    """

    action: ListActionResponse = Field(..., description="Action")


# Model for Sinkhole Settings
class SinkholeSettings(BaseModel):
    """
    Represents the 'sinkhole' settings.
    """

    ipv4_address: IPv4AddressEnum = Field(..., description="IPv4 address for sinkhole")
    ipv6_address: IPv6AddressEnum = Field(..., description="IPv6 address for sinkhole")


# Model for Whitelist entries
class WhitelistEntry(BaseModel):
    """
    Represents an entry in the 'whitelist'.
    """

    name: str = Field(..., description="DNS domain or FQDN to be whitelisted")
    description: Optional[str] = Field(None, description="Description")


# Botnet Domains models
class BotnetDomainsRequest(BaseModel):
    """
    Represents 'botnet_domains' in requests.
    """

    dns_security_categories: Optional[List[DNSSecurityCategoryEntry]] = Field(
        None, description="DNS security categories"
    )
    lists: Optional[List[ListEntryRequest]] = Field(
        None, description="Lists of DNS domains"
    )
    sinkhole: Optional[SinkholeSettings] = Field(
        None, description="DNS sinkhole settings"
    )
    whitelist: Optional[List[WhitelistEntry]] = Field(
        None, description="DNS security overrides"
    )


class BotnetDomainsResponse(BaseModel):
    """
    Represents 'botnet_domains' in responses.
    """

    dns_security_categories: Optional[List[DNSSecurityCategoryEntry]] = Field(
        None, description="DNS security categories"
    )
    lists: Optional[List[ListEntryResponse]] = Field(
        None, description="Lists of DNS domains"
    )
    sinkhole: Optional[SinkholeSettings] = Field(
        None, description="DNS sinkhole settings"
    )
    whitelist: Optional[List[WhitelistEntry]] = Field(
        None, description="DNS security overrides"
    )


# Base model for DNS Security Profile
class DNSSecurityProfileBaseModel(BaseModel):
    """
    Base model for DNS Security Profile.
    """

    name: str = Field(
        ...,
        description="Profile name",
    )
    description: Optional[str] = Field(
        None,
        description="Description",
    )
    botnet_domains: Optional[BotnetDomainsRequest] = Field(
        None,
        description="Botnet domains settings",
    )


# Request model
class DNSSecurityProfileRequestModel(DNSSecurityProfileBaseModel):
    """
    Represents a DNS Security Profile for API requests.
    """

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
    botnet_domains: Optional[BotnetDomainsRequest] = Field(
        None,
        description="Botnet domains settings",
    )

    model_config = ConfigDict(validate_assignment=True, arbitrary_types_allowed=True)

    @model_validator(mode="after")
    def validate_container(self) -> "DNSSecurityProfileRequestModel":
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


# Response model
class DNSSecurityProfileResponseModel(DNSSecurityProfileBaseModel):
    """
    Represents a DNS Security Profile for API responses.
    """

    id: str = Field(
        ...,
        description="Profile ID",
    )
    folder: Optional[str] = Field(
        None,
        description="Folder",
    )
    snippet: Optional[str] = Field(
        None,
        description="Snippet",
    )
    device: Optional[str] = Field(
        None,
        description="Device",
    )
    botnet_domains: Optional[BotnetDomainsResponse] = Field(
        None,
        description="Botnet domains settings",
    )

    @field_validator("id")
    @classmethod
    def validate_id(cls, v):
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError("Invalid UUID format for 'id'")
        return v


# Response model for list of profiles
class DNSSecurityProfilesResponse(BaseModel):
    """
    Represents the API response containing a list of DNS Security Profiles.
    """

    data: List[DNSSecurityProfileResponseModel]
    offset: int
    total: int
    limit: int
