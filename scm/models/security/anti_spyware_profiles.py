"""Anti-Spyware Profiles security models for Strata Cloud Manager SDK.

Contains Pydantic models for representing anti-spyware profile objects and related data.
"""

# scm/models/security/anti_spyware_profile.py

from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    field_validator,
    model_validator,
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
    """Represents an entry in the 'exempt_ip' list within a threat exception.

    Attributes:
        name (str): Name of the IP address or range to exempt.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

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

    # ADNS categories
    adns_adtracking = "adns-adtracking"
    adns_benign = "adns-benign"
    adns_c2 = "adns-c2"
    adns_ddns = "adns-ddns"
    adns_dnsmisconfig = "adns-dnsmisconfig"
    adns_grayware = "adns-grayware"
    adns_hijacking = "adns-hijacking"
    adns_malware = "adns-malware"
    adns_new_domain = "adns-new-domain"
    adns_parked = "adns-parked"
    adns_phishing = "adns-phishing"
    adns_proxy = "adns-proxy"
    # Standard categories
    adware = "adware"
    any = "any"
    autogen = "autogen"
    backdoor = "backdoor"
    botnet = "botnet"
    browser_hijack = "browser-hijack"
    command_and_control = "command-and-control"
    cryptominer = "cryptominer"
    data_theft = "data-theft"
    dns = "dns"
    dns_adtracking = "dns-adtracking"
    dns_benign = "dns-benign"
    dns_c2 = "dns-c2"
    dns_ddns = "dns-ddns"
    dns_grayware = "dns-grayware"
    dns_malware = "dns-malware"
    dns_new_domain = "dns-new-domain"
    dns_parked = "dns-parked"
    dns_phishing = "dns-phishing"
    dns_proxy = "dns-proxy"
    dns_security = "dns-security"
    dns_wildfire = "dns-wildfire"
    domain_edl = "domain-edl"
    downloader = "downloader"
    fraud = "fraud"
    hacktool = "hacktool"
    inline_cloud_c2 = "inline-cloud-c2"
    keylogger = "keylogger"
    net_worm = "net-worm"
    p2p_communication = "p2p-communication"
    phishing_kit = "phishing-kit"
    post_exploitation = "post-exploitation"
    spyware = "spyware"
    tls_fingerprint = "tls-fingerprint"
    webshell = "webshell"


# Component Models
class AntiSpywareMicaEngineSpywareEnabledEntry(BaseModel):
    """Represents an entry in the 'mica_engine_spyware_enabled' list."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

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

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

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
    """Represents the 'action' field in rules and threat exceptions for requests.

    Enforces that exactly one action is provided.
    """

    @model_validator(mode="before")
    @classmethod
    def convert_action(cls, values):
        """Convert and validate the action field, ensuring exactly one action is provided.

        Args:
            values (Any): The action value to validate and convert.

        Returns:
            dict: The validated action dictionary.

        Raises:
            ValueError: If the action is not a string or dict, or if not exactly one action is provided.

        """
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
        """Return the name of the action in the root dictionary.

        Returns:
            str: The action name, or 'unknown' if not set.

        """
        return next(iter(self.root.keys()), "unknown")


class AntiSpywareActionResponse(RootModel[dict]):
    """Represents the 'action' field in rules and threat exceptions for responses.

    Accepts empty dictionaries.
    """

    @model_validator(mode="before")
    @classmethod
    def validate_action(cls, values):
        """Convert and validate the action field for response models.

        Args:
            values (Any): The action value to validate and convert.

        Returns:
            dict: The validated action dictionary.

        Raises:
            ValueError: If the action is not a string or dict, or if not exactly one action is provided.

        """
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
        """Return the name of the action in the root dictionary.

        Returns:
            str: The action name, or 'unknown' if not set.

        """
        return next(iter(self.root.keys()), "unknown")


class AntiSpywareRuleBaseModel(BaseModel):
    """Base model for rules."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

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
    action: Optional[AntiSpywareActionResponse] = Field(
        None,
        description="Action to take when rule matches",
    )

    @field_validator(
        "threat_name",
        mode="before",
    )
    @classmethod
    def default_threat_name(cls, v):
        """Set the default threat name to 'any' if not provided.

        Args:
            v (Optional[str]): The threat name value.

        Returns:
            str: The threat name, or 'any' if not provided.

        """
        return v or "any"


class AntiSpywareThreatExceptionBase(BaseModel):
    """Base model for threat exceptions."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(
        ...,
        description="Threat exception name",
    )
    packet_capture: AntiSpywarePacketCapture = Field(
        ...,
        description="Packet capture setting",
    )
    action: Optional[AntiSpywareActionResponse] = Field(
        None,
        description="Action to take for this threat exception",
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
    """Base model for Anti-Spyware Profile containing common fields across all operations."""

    model_config = ConfigDict(
        extra="forbid",
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
    mica_engine_spyware_enabled: Optional[List[AntiSpywareMicaEngineSpywareEnabledEntry]] = Field(
        None,
        description="List of MICA engine spyware enabled entries",
    )
    rules: Optional[List[AntiSpywareRuleBaseModel]] = Field(
        None,
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
    """Model for creating a new Anti-Spyware Profile.

    Inherits from base model and adds create-specific validation.
    """

    @model_validator(mode="after")
    def validate_container_type(self) -> "AntiSpywareProfileCreateModel":
        """Ensure exactly one container field (folder, snippet, or device) is set.

        Returns:
            AntiSpywareProfileCreateModel: The validated model instance.

        Raises:
            ValueError: If zero or more than one container field is set.

        """
        container_fields = [
            "folder",
            "snippet",
            "device",
        ]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


class AntiSpywareProfileUpdateModel(AntiSpywareProfileBase):
    """Model for updating an existing Anti-Spyware Profile.

    All fields are optional to allow partial updates.
    """

    id: UUID = Field(
        ...,
        description="Profile ID",
    )


class AntiSpywareProfileResponseModel(AntiSpywareProfileBase):
    """Model for Anti-Spyware Profile API responses.

    Includes all base fields plus the id field.
    """

    id: UUID = Field(
        ...,
        description="Profile ID",
    )
