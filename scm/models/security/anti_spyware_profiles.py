# scm/models/security/anti_spyware_profile.py

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


class InlinePolicyAction(str, Enum):
    """Enumeration of allowed inline policy actions."""

    alert = "alert"
    allow = "allow"
    drop = "drop"
    reset_both = "reset-both"
    reset_client = "reset-client"
    reset_server = "reset-server"


class MicaEngineSpywareEnabledEntry(BaseModel):
    """
    Represents an entry in the 'mica_engine_spyware_enabled' list.

    Attributes:
        name (str): Name of the MICA engine spyware detector.
        inline_policy_action (InlinePolicyAction): Action to be taken by the inline policy.
    """

    name: str = Field(
        ...,
        description="Name of the MICA engine spyware detector",
    )
    inline_policy_action: InlinePolicyAction = Field(
        InlinePolicyAction.alert,
        description="Inline policy action, defaults to 'alert'",
    )


class BlockIpAction(BaseModel):
    """
    Represents the 'block_ip' action with additional properties.

    Attributes:
        track_by (str): Method of tracking ('source-and-destination' or 'source').
        duration (int): Duration in seconds (1 to 3600).
    """

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


class ActionRequest(RootModel[dict]):
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


class ActionResponse(RootModel[dict]):
    """
    Represents the 'action' field in rules and threat exceptions for responses.

    Accepts empty dictionaries.
    """

    @model_validator(mode="before")
    @classmethod
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


class PacketCapture(str, Enum):
    """Enumeration of packet capture options."""

    disable = "disable"
    single_packet = "single-packet"
    extended_capture = "extended-capture"


class Severity(str, Enum):
    """Enumeration of severity levels."""

    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"
    informational = "informational"
    any = "any"


class Category(str, Enum):
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


class ExemptIpEntry(BaseModel):
    """
    Represents an entry in the 'exempt_ip' list within a threat exception.

    Attributes:
        name (str): Name of the IP address or range to exempt.
    """

    name: str = Field(
        ...,
        description="Exempt IP name",
    )


class RuleBase(BaseModel):
    """
    Base class for Rule.
    """

    name: str = Field(
        ...,
        description="Rule name",
    )
    severity: List[Severity] = Field(
        ...,
        description="List of severities",
    )
    category: Category = Field(
        ...,
        description="Category",
    )
    threat_name: Optional[str] = Field(
        None,
        description="Threat name",
        min_length=3,
    )
    packet_capture: Optional[PacketCapture] = Field(
        None,
        description="Packet capture setting",
    )

    @field_validator("threat_name", mode="before")
    @classmethod
    def default_threat_name(cls, v):
        return v or "any"


class RuleRequest(RuleBase):
    action: Optional[ActionRequest] = Field(
        None,
        description="Action",
    )


class RuleResponse(RuleBase):
    action: Optional[ActionResponse] = Field(
        None,
        description="Action",
    )


class ThreatExceptionBase(BaseModel):
    """
    Base class for ThreatException.
    """

    name: str = Field(
        ...,
        description="Threat exception name",
    )
    packet_capture: PacketCapture = Field(
        ...,
        description="Packet capture setting",
    )
    exempt_ip: Optional[List[ExemptIpEntry]] = Field(
        None,
        description="Exempt IP list",
    )
    notes: Optional[str] = Field(
        None,
        description="Notes",
    )


class ThreatExceptionRequest(ThreatExceptionBase):
    action: ActionRequest = Field(
        ...,
        description="Action",
    )


class ThreatExceptionResponse(ThreatExceptionBase):
    action: ActionResponse = Field(
        ...,
        description="Action",
    )


class AntiSpywareProfileBaseModel(BaseModel):
    """
    Base model for AntiSpywareProfile, containing common fields.
    """

    name: str = Field(
        ...,
        description="Profile name",
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
    mica_engine_spyware_enabled: Optional[List[MicaEngineSpywareEnabledEntry]] = Field(
        None,
        description="List of MICA engine spyware enabled entries",
    )


class AntiSpywareProfileRequestModel(AntiSpywareProfileBaseModel):
    """
    Represents an anti-spyware profile for API requests.
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
    rules: List[RuleRequest] = Field(
        ...,
        description="List of rules",
    )
    threat_exception: Optional[List[ThreatExceptionRequest]] = Field(
        None,
        description="List of threat exceptions",
    )

    model_config = ConfigDict(validate_assignment=True, arbitrary_types_allowed=True)

    @model_validator(mode="after")
    def validate_container(self) -> "AntiSpywareProfileRequestModel":
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


class AntiSpywareProfileResponseModel(AntiSpywareProfileBaseModel):
    """
    Represents an anti-spyware profile for API responses.
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
    rules: List[RuleResponse] = Field(
        ...,
        description="List of rules",
    )
    threat_exception: Optional[List[ThreatExceptionResponse]] = Field(
        None,
        description="List of threat exceptions",
    )

    @field_validator("id")
    @classmethod
    def validate_id(cls, v):
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError("Invalid UUID format for 'id'")
        return v


class AntiSpywareProfilesResponse(BaseModel):
    """
    Represents the API response containing a list of anti-spyware profiles.

    Attributes:
        data (List[AntiSpywareProfileResponseModel]): List of anti-spyware profiles.
        offset (int): Offset used in pagination.
        total (int): Total number of profiles available.
        limit (int): Maximum number of profiles returned.
    """

    data: List[AntiSpywareProfileResponseModel]
    offset: int
    total: int
    limit: int
