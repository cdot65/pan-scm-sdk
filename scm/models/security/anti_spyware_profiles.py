# scm/models/security/anti_spyware_profile.py

from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    Field,
    model_validator,
    field_validator,
    ConfigDict,
    RootModel,
)


# Enums
class AntiSpywareInlinePolicyAction(str, Enum):
    """Enumeration of allowed inline policy actions."""

    alert = "alert"
    allow = "allow"
    drop = "drop"
    reset_both = "reset-both"
    reset_client = "reset-client"
    reset_server = "reset-server"


class AntiSpywareExemptIpEntry(BaseModel):
    """
    Represents an entry in the 'exempt_ip' list within a threat exception.

    Attributes:
        name (str): Name of the IP address or range to exempt.
    """

    name: str = Field(
        ...,
        description="Exempt IP name",
    )


class AntiSpywarePacketCapture(str, Enum):
    """Enumeration of packet capture options."""

    disable = "disable"
    single_packet = "single-packet"
    extended_capture = "extended-capture"


class AntiSpywareSeverity(str, Enum):
    """Enumeration of severity levels."""

    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"
    informational = "informational"
    any = "any"


class AntiSpywareCategory(str, Enum):
    """Enumeration of threat categories."""

    dns_proxy = "dns-proxy"
    backdoor = "backdoor"
    data_theft = "data-theft"
    autogen = "autogen"
    spyware = "spyware"
    dns_security = "dns-security"
    downloader = "downloader"
    dns_phishing = "dns-phishing"
    phishing_kit = "phishing-kit"
    cryptominer = "cryptominer"
    hacktool = "hacktool"
    dns_benign = "dns-benign"
    dns_wildfire = "dns-wildfire"
    botnet = "botnet"
    dns_grayware = "dns-grayware"
    inline_cloud_c2 = "inline-cloud-c2"
    keylogger = "keylogger"
    p2p_communication = "p2p-communication"
    domain_edl = "domain-edl"
    webshell = "webshell"
    command_and_control = "command-and-control"
    dns_ddns = "dns-ddns"
    net_worm = "net-worm"
    tls_fingerprint = "tls-fingerprint"
    dns_new_domain = "dns-new-domain"
    dns = "dns"
    fraud = "fraud"
    dns_c2 = "dns-c2"
    adware = "adware"
    post_exploitation = "post-exploitation"
    dns_malware = "dns-malware"
    browser_hijack = "browser-hijack"
    dns_parked = "dns-parked"
    any = "any"


# Component Models
class AntiSpywareMicaEngineSpywareEnabledEntry(BaseModel):
    """Represents an entry in the 'mica_engine_spyware_enabled' list."""

    name: str = Field(
        ...,
        description="Name of the MICA engine spyware detector",
    )
    inline_policy_action: AntiSpywareInlinePolicyAction = Field(
        AntiSpywareInlinePolicyAction.alert,
        description="Inline policy action, defaults to 'alert'",
    )


class AntiSpywareBlockIpAction(BaseModel):
    """Represents the 'block_ip' action configuration."""

    track_by: str = Field(
        ...,
        description="Tracking method",
        pattern="^(source-and-destination|source)$",
    )
    duration: int = Field(
        ...,
        description="Duration in seconds",
        ge=1,
        le=3600,
    )


class AntiSpywareActionRequest(RootModel[dict]):
    """
    Represents the 'action' field in rules and threat exceptions for requests.

    Enforces that exactly one action is provided.
    """

    @model_validator(mode="before")
    @classmethod
    def check_and_transform_action(cls, values):
        if isinstance(values, str):
            # Convert string to dict
            values = {values: {}}
        elif not isinstance(values, dict):
            raise ValueError("Invalid action format; must be a string or dict.")

        action_fields = [
            "allow",
            "alert",
            "drop",
            "reset_client",
            "reset_server",
            "reset_both",
            "block_ip",
            "default",
        ]
        provided_actions = [field for field in action_fields if field in values]

        if len(provided_actions) != 1:
            raise ValueError("Exactly one action must be provided in 'action' field.")

        return values

    def get_action_name(self) -> str:
        return next(iter(self.root.keys()), "unknown")


class AntiSpywareActionResponse(RootModel[dict]):
    """
    Represents the 'action' field in rules and threat exceptions for responses.

    Accepts empty dictionaries.
    """

    @model_validator(mode="before")
    def check_action(cls, values):
        if isinstance(values, str):
            # Convert string to dict
            values = {values: {}}
        elif not isinstance(values, dict):
            raise ValueError("Invalid action format; must be a string or dict.")

        action_fields = [
            "allow",
            "alert",
            "drop",
            "reset_client",
            "reset_server",
            "reset_both",
            "block_ip",
            "default",
        ]
        provided_actions = [field for field in action_fields if field in values]

        if len(provided_actions) > 1:
            raise ValueError("At most one action must be provided in 'action' field.")

        # Accept empty dicts (no action specified)
        return values

    def get_action_name(self) -> str:
        return next(iter(self.root.keys()), "unknown")


class AntiSpywareRuleBaseModel(BaseModel):
    """Base model for rules."""

    name: str = Field(
        ...,
        description="Rule name",
    )
    severity: List[AntiSpywareSeverity] = Field(
        ...,
        description="List of severities",
    )
    category: AntiSpywareCategory = Field(
        ...,
        description="Category",
    )
    threat_name: Optional[str] = Field(
        None,
        description="Threat name",
        min_length=3,
    )
    packet_capture: Optional[AntiSpywarePacketCapture] = Field(
        None,
        description="Packet capture setting",
    )

    @field_validator(
        "threat_name",
        mode="before",
    )
    def default_threat_name(cls, v):
        return v or "any"


class AntiSpywareThreatExceptionBase(BaseModel):
    """Base model for threat exceptions."""

    name: str = Field(
        ...,
        description="Threat exception name",
    )
    packet_capture: AntiSpywarePacketCapture = Field(
        ...,
        description="Packet capture setting",
    )
    exempt_ip: Optional[List[AntiSpywareExemptIpEntry]] = Field(
        None,
        description="Exempt IP list",
    )
    notes: Optional[str] = Field(
        None,
        description="Notes",
    )


class AntiSpywareProfileBase(BaseModel):
    """
    Base model for Anti-Spyware Profile containing common fields across all operations.
    """

    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    name: str = Field(
        ...,
        description="Profile name",
        pattern=r"^[a-zA-Z0-9][a-zA-Z0-9_\-. ]*$",
    )
    description: Optional[str] = Field(
        None,
        description="Description",
    )
    cloud_inline_analysis: Optional[bool] = Field(
        False,
        description="Cloud inline analysis",
    )
    inline_exception_edl_url: Optional[List[str]] = Field(
        None,
        description="Inline exception EDL URLs",
    )
    inline_exception_ip_address: Optional[List[str]] = Field(
        None,
        description="Inline exception IP addresses",
    )
    mica_engine_spyware_enabled: Optional[
        List[AntiSpywareMicaEngineSpywareEnabledEntry]
    ] = Field(
        None,
        description="List of MICA engine spyware enabled entries",
    )
    rules: List[AntiSpywareRuleBaseModel] = Field(
        ...,
        description="List of rules",
    )
    threat_exception: Optional[List[AntiSpywareThreatExceptionBase]] = Field(
        None,
        description="List of threat exceptions",
    )

    folder: Optional[str] = Field(
        None,
        description="Folder in which the resource is defined",
        max_length=64,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
    )
    snippet: Optional[str] = Field(
        None,
        description="Snippet in which the resource is defined",
        max_length=64,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
    )
    device: Optional[str] = Field(
        None,
        description="Device in which the resource is defined",
        max_length=64,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
    )


class AntiSpywareProfileCreateModel(AntiSpywareProfileBase):
    """
    Model for creating a new Anti-Spyware Profile.
    Inherits from base model and adds create-specific validation.
    """

    @model_validator(mode="after")
    def validate_container(self) -> "AntiSpywareProfileCreateModel":
        container_fields = [
            "folder",
            "snippet",
            "device",
        ]
        provided = [
            field for field in container_fields if getattr(self, field) is not None
        ]
        if len(provided) != 1:
            raise ValueError(
                "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            )
        return self


class AntiSpywareProfileUpdateModel(AntiSpywareProfileBase):
    """
    Model for updating an existing Anti-Spyware Profile.
    All fields are optional to allow partial updates.
    """

    id: Optional[UUID] = Field(
        ...,
        description="Profile ID",
    )


class AntiSpywareProfileResponseModel(AntiSpywareProfileBase):
    """
    Model for Anti-Spyware Profile API responses.
    Includes all base fields plus the id field.
    """

    id: UUID = Field(
        ...,
        description="Profile ID",
    )
