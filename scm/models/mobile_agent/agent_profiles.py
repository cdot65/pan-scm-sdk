"""Agent Profiles (Application Settings) models for Strata Cloud Manager SDK.

Contains Pydantic models for representing GlobalProtect agent profiles and their
nested configuration structures. The SCM UI refers to this resource as
"App Settings" / "Application Settings".
"""

# scm/models/mobile_agent/agent_profiles.py

# Standard library imports
from enum import Enum
from typing import Annotated, Any, Dict, List, Literal, Optional, Union

# External libraries
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class AgentProfileOperatingSystem(str, Enum):
    """Available operating systems for GlobalProtect agent profiles."""

    ANDROID = "Android"
    CHROME = "Chrome"
    IOT = "IoT"
    LINUX = "Linux"
    MAC = "Mac"
    WINDOWS = "Windows"
    WINDOWS_UWP = "WindowsUWP"
    IOS = "iOS"


class SaveUserCredentials(str, Enum):
    """Available save user credential options for GlobalProtect agent profiles.

    Values map to the GlobalProtect agent behavior:
        "0": No
        "1": Yes
        "2": Save username only
        "3": Only with user fingerprint
    """

    NO = "0"
    YES = "1"
    SAVE_USERNAME_ONLY = "2"
    ONLY_WITH_USER_FINGERPRINT = "3"


class ThirdPartyVpnClient(str, Enum):
    """Supported third party VPN clients for GlobalProtect agent profiles."""

    PAN_VIRTUAL_ETHERNET_ADAPTER = "PAN Virtual Ethernet Adapter"
    JUNIPER_NETWORK_VIRTUAL_ADAPTER = "Juniper Network Virtual Adapter"
    CISCO_SYSTEMS_VPN_ADAPTER = "Cisco Systems VPN Adapter"


class ConnectMethodValue(str, Enum):
    """Available connect methods for the GlobalProtect app configuration."""

    USER_LOGON = "user-logon"
    PRE_LOGON = "pre-logon"
    ON_DEMAND = "on-demand"
    PRE_LOGON_THEN_ON_DEMAND = "pre-logon-then-on-demand"


class GatewayPriority(str, Enum):
    """Available priority values for external gateway priority rules."""

    HIGHEST = "0"
    HIGH = "1"
    MEDIUM = "2"
    LOW = "3"
    LOWEST = "4"
    MANUAL_ONLY = "5"


class WelcomePage(BaseModel):
    """The welcome page displayed upon login."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    page: Optional[str] = Field(
        None,
        description="The name of the welcome page",
    )


class AgentUI(BaseModel):
    """Agent UI configuration settings for a GlobalProtect agent profile."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    agent_user_override_timeout: Optional[int] = Field(
        None,
        ge=0,
        le=65535,
        description=(
            "Agent disabled duration (minutes). A value of `0` means the agent will "
            "remain disabled until manually enabled."
        ),
    )
    max_agent_user_overrides: Optional[int] = Field(
        None,
        ge=0,
        le=25,
        description=(
            "The maximum number of times the agent can be disabled. A value of `0` "
            "means there are no limits to the number of times the agent can be disabled."
        ),
    )
    passcode: Optional[str] = Field(
        None,
        min_length=6,
        max_length=64,
        description="The passcode used to disable the agent",
    )
    uninstall_password: Optional[str] = Field(
        None,
        min_length=6,
        max_length=32,
        description="The password used to uninstall the agent",
    )
    welcome_page: Optional[WelcomePage] = Field(
        None,
        description="The welcome page displayed upon login",
    )


class CookieLifetime(BaseModel):
    """Authentication cookie lifetime configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    lifetime_in_days: Optional[float] = Field(
        None,
        ge=1,
        le=365,
        description="Cookie lifetime in days",
    )
    lifetime_in_hours: Optional[float] = Field(
        None,
        ge=1,
        le=72,
        description="Cookie lifetime in hours",
    )
    lifetime_in_minutes: Optional[float] = Field(
        None,
        ge=1,
        le=59,
        description="Cookie lifetime in minutes",
    )


class AcceptCookie(BaseModel):
    """Accept cookie configuration for authentication override."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    cookie_lifetime: Optional[CookieLifetime] = Field(
        None,
        description="The lifetime of the authentication override cookie",
    )


class AuthenticationOverride(BaseModel):
    """Authentication override settings for a GlobalProtect agent profile."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    accept_cookie: Optional[AcceptCookie] = Field(
        None,
        description="Accept an authentication override cookie",
    )
    cookie_encrypt_decrypt_cert: Optional[str] = Field(
        None,
        description="The certificate used to encrypt and decrypt the cookie",
    )
    generate_cookie: Optional[bool] = Field(
        None,
        description="Generate an authentication override cookie",
    )


class CertificateCriteria(BaseModel):
    """Certificate criteria for a GlobalProtect agent profile."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    certificate_profile: Optional[str] = Field(
        None,
        description="The certificate profile used to match this agent profile",
    )


class AgentProfileCertificate(BaseModel):
    """Certificate settings for a GlobalProtect agent profile."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    criteria: Optional[CertificateCriteria] = Field(
        None,
        description="The certificate matching criteria",
    )


class ClientCertificate(BaseModel):
    """Client certificate settings for a GlobalProtect agent profile."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    local: Optional[str] = Field(
        None,
        description="The local client certificate",
    )
    scep: Optional[str] = Field(
        None,
        max_length=255,
        description="The SCEP profile used to obtain the client certificate",
    )


class PlistKeyEntry(BaseModel):
    """A plist key entry within a custom checks plist."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: Optional[str] = Field(
        None,
        description="The name of the plist key",
    )
    negate: Optional[bool] = Field(
        None,
        description="Whether to negate the key match",
    )
    value: Optional[str] = Field(
        None,
        max_length=1024,
        description="The value of the plist key",
    )


class PlistEntry(BaseModel):
    """A plist entry for custom checks criteria (macOS)."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: Optional[str] = Field(
        None,
        description="The name of the preference list",
    )
    key: Optional[List[PlistKeyEntry]] = Field(
        None,
        description="The plist keys to match",
    )
    negate: Optional[bool] = Field(
        None,
        description="Whether to negate the plist match",
    )


class RegistryValueEntry(BaseModel):
    """A registry value entry within a custom checks registry key."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: Optional[str] = Field(
        None,
        description="The name of the registry value",
    )
    negate: Optional[bool] = Field(
        None,
        description="Whether to negate the registry value match",
    )
    value_data: Optional[str] = Field(
        None,
        description="The data of the registry value",
    )


class RegistryKeyEntry(BaseModel):
    """A registry key entry for custom checks criteria (Windows)."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: Optional[str] = Field(
        None,
        max_length=1023,
        description="The name of the registry key",
    )
    default_value_data: Optional[str] = Field(
        None,
        max_length=1024,
        description="The default value data of the registry key",
    )
    negate: Optional[bool] = Field(
        None,
        description="Whether to negate the registry key match",
    )
    registry_value: Optional[List[RegistryValueEntry]] = Field(
        None,
        description="The registry values to match",
    )


class CustomChecksCriteria(BaseModel):
    """Custom checks criteria for a GlobalProtect agent profile."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    plist: Optional[List[PlistEntry]] = Field(
        None,
        description="The plist entries to match (macOS)",
    )
    registry_key: Optional[List[RegistryKeyEntry]] = Field(
        None,
        description="The registry keys to match (Windows)",
    )


class CustomChecks(BaseModel):
    """Custom checks settings for a GlobalProtect agent profile."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    criteria: Optional[CustomChecksCriteria] = Field(
        None,
        description="The custom checks matching criteria",
    )


class GatewayAddress(BaseModel):
    """IP address of a GlobalProtect gateway."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    ipv4: Optional[str] = Field(
        None,
        pattern=r"^([:0-9.])+$",
        max_length=100,
        description="The IPv4 address of the gateway",
    )
    ipv6: Optional[str] = Field(
        None,
        max_length=100,
        description="The IPv6 address of the gateway",
    )


class GatewayChoice(BaseModel):
    """Address of a GlobalProtect gateway, as either an FQDN or an IP address."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    fqdn: Optional[str] = Field(
        None,
        description="The FQDN of the gateway",
    )
    ip: Optional[GatewayAddress] = Field(
        None,
        description="The IP address of the gateway",
    )

    @model_validator(mode="after")
    def validate_fqdn_or_ip(self) -> "GatewayChoice":
        """Validate that exactly one of fqdn or ip is provided."""
        if self.fqdn is not None and self.ip is not None:
            raise ValueError("Exactly one of 'fqdn' or 'ip' must be provided, not both")
        if self.fqdn is None and self.ip is None:
            raise ValueError("Exactly one of 'fqdn' or 'ip' must be provided")
        return self


class GatewayPriorityRule(BaseModel):
    """A priority rule for an external GlobalProtect gateway."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: Optional[str] = Field(
        None,
        description="The name of the priority rule",
    )
    priority: Optional[GatewayPriority] = Field(
        None,
        description="The priority of the gateway ('0' highest through '5' manual only)",
    )


class ExternalGatewayEntry(BaseModel):
    """An external gateway entry for a GlobalProtect agent profile."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: Optional[str] = Field(
        None,
        description="The name of the external gateway",
    )
    choice: Optional[GatewayChoice] = Field(
        None,
        description="The address of the gateway, as either an FQDN or an IP address",
    )
    manual: Optional[bool] = Field(
        None,
        description="If this GlobalProtect gateway can be manually selected",
    )
    priority_rule: Optional[List[GatewayPriorityRule]] = Field(
        None,
        description="The priority rules for the gateway",
    )


class ExternalGateways(BaseModel):
    """External gateways configuration for a GlobalProtect agent profile."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    list: Optional[List[ExternalGatewayEntry]] = Field(  # noqa: A003
        None,
        description="The list of external gateways",
    )


class InternalGatewayEntry(BaseModel):
    """An internal gateway entry for a GlobalProtect agent profile."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: Optional[str] = Field(
        None,
        description="The name of the internal gateway",
    )
    choice: Optional[GatewayChoice] = Field(
        None,
        description="The address of the gateway, as either an FQDN or an IP address",
    )
    source_ip: Optional[List[str]] = Field(
        None,
        description="The source IP addresses used to match this internal gateway",
    )


class InternalGateways(BaseModel):
    """Internal gateways configuration for a GlobalProtect agent profile."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    list: Optional[List[InternalGatewayEntry]] = Field(  # noqa: A003
        None,
        description="The list of internal gateways",
    )


class Gateways(BaseModel):
    """Gateways configuration for a GlobalProtect agent profile."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    external: Optional[ExternalGateways] = Field(
        None,
        description="The external gateways configuration",
    )
    internal: Optional[InternalGateways] = Field(
        None,
        description="The internal gateways configuration",
    )


class ConnectMethodAppConfig(BaseModel):
    """The connect-method GlobalProtect app configuration entry."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: Literal["connect-method"] = Field(
        "connect-method",
        description="The name of the app configuration entry",
    )
    value: Optional[List[ConnectMethodValue]] = Field(
        None,
        min_length=1,
        max_length=1,
        description="The connect method",
    )


class TunnelMtuAppConfig(BaseModel):
    """The tunnel-mtu GlobalProtect app configuration entry."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: Literal["tunnel-mtu"] = Field(
        "tunnel-mtu",
        description="The name of the app configuration entry",
    )
    value: Optional[List[Annotated[float, Field(ge=1000, le=1420)]]] = Field(
        None,
        min_length=1,
        max_length=1,
        description="GlobalProtect Connection MTU (bytes)",
    )


GPAppConfigEntry = Annotated[
    Union[ConnectMethodAppConfig, TunnelMtuAppConfig],
    Field(discriminator="name"),
]


class GPAppConfig(BaseModel):
    """GlobalProtect app configuration for an agent profile.

    Currently only connect-method and tunnel-mtu are supported as app-config.
    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    config: Optional[List[GPAppConfigEntry]] = Field(
        None,
        description="The app configuration entries (connect-method and tunnel-mtu)",
    )


class HipLinuxCustomChecks(BaseModel):
    """Linux custom checks for HIP collection."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    process_list: Optional[List[str]] = Field(
        None,
        description="The processes to check for",
    )


class HipMacOsPlistEntry(BaseModel):
    """A macOS plist entry for HIP collection custom checks."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(
        ...,
        max_length=1023,
        description="Preference list",
    )
    key: Optional[List[str]] = Field(
        None,
        description="The plist keys to collect",
    )


class HipMacOsCustomChecks(BaseModel):
    """macOS custom checks for HIP collection."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    plist: Optional[List[HipMacOsPlistEntry]] = Field(
        None,
        description="The preference lists to collect",
    )
    process_list: Optional[List[str]] = Field(
        None,
        description="The processes to check for",
    )


class HipWindowsRegistryKey(BaseModel):
    """A Windows registry key entry for HIP collection custom checks."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(
        ...,
        max_length=1023,
        description="Registry key",
    )
    registry_value: Optional[List[str]] = Field(
        None,
        description="The registry values to collect",
    )


class HipWindowsCustomChecks(BaseModel):
    """Windows custom checks for HIP collection."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    process_list: Optional[List[str]] = Field(
        None,
        description="The processes to check for",
    )
    registry_key: Optional[List[HipWindowsRegistryKey]] = Field(
        None,
        description="The registry keys to collect",
    )


class HipCustomChecks(BaseModel):
    """Custom checks for HIP collection, by operating system."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    linux: Optional[HipLinuxCustomChecks] = Field(
        None,
        description="Linux custom checks",
    )
    mac_os: Optional[HipMacOsCustomChecks] = Field(
        None,
        description="macOS custom checks",
    )
    windows: Optional[HipWindowsCustomChecks] = Field(
        None,
        description="Windows custom checks",
    )


class HipExclusionVendor(BaseModel):
    """A vendor entry for a HIP collection exclusion category."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: Optional[str] = Field(
        None,
        description="The name of the vendor",
    )
    product: Optional[List[str]] = Field(
        None,
        description="The products of the vendor to exclude",
    )


class HipExclusionCategory(BaseModel):
    """A category entry for HIP collection exclusion."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: Optional[str] = Field(
        None,
        description="The name of the category",
    )
    vendor: Optional[List[HipExclusionVendor]] = Field(
        None,
        description="The vendors to exclude",
    )


class HipExclusion(BaseModel):
    """Exclusion settings for HIP collection."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    category: Optional[List[HipExclusionCategory]] = Field(
        None,
        description="The categories to exclude from HIP collection",
    )


class HipCollection(BaseModel):
    """HIP collection settings for a GlobalProtect agent profile."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    certificate_profile: Optional[str] = Field(
        None,
        description="The certificate profile used for HIP collection",
    )
    collect_hip_data: Optional[bool] = Field(
        None,
        description="Whether to collect HIP data",
    )
    custom_checks: Optional[HipCustomChecks] = Field(
        None,
        description="Custom checks for HIP collection",
    )
    exclusion: Optional[HipExclusion] = Field(
        None,
        description="Exclusion settings for HIP collection",
    )
    max_wait_time: Optional[float] = Field(
        None,
        ge=10,
        le=60,
        description="The maximum time (seconds) to wait for HIP data collection",
    )


class InternalHostDetection(BaseModel):
    """Internal host detection (IPv4) settings for a GlobalProtect agent profile."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    hostname: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z0-9._-]+$",
        max_length=256,
        description="Host name of the IPv4 in DNS record",
    )
    ip_address: Optional[str] = Field(
        None,
        description="Internal IPv4 address of a host",
    )


class InternalHostDetectionV6(BaseModel):
    """Internal host detection (IPv6) settings for a GlobalProtect agent profile."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    hostname: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z0-9._-]+$",
        max_length=256,
        description="Host name of the IPv4 in DNS record",
    )
    ip_address: Optional[str] = Field(
        None,
        description="Internal IPv6 address of a host",
    )


class MachineAccountExistsWithSerialno(BaseModel):
    """Machine account exists with serial number setting.

    Exactly one of `yes` or `no` is expected to be set (each is an empty object
    in the API payload).
    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    yes: Optional[Dict[str, Any]] = Field(
        None,
        description="The machine account exists with the serial number",
    )
    no: Optional[Dict[str, Any]] = Field(
        None,
        description="The machine account does not exist with the serial number",
    )


class AgentProfilesBaseModel(BaseModel):
    """Base model for GlobalProtect Agent Profiles containing fields common to all CRUD operations.

    The SCM UI refers to this resource as "App Settings" / "Application Settings".

    Attributes:
        name (str): The name of the agent profile.
        folder (Optional[str]): The folder in which the resource is defined (must be
            'Mobile Users').
        agent_ui (Optional[AgentUI]): Agent UI configuration settings.
        authentication_override (Optional[AuthenticationOverride]): Authentication
            override settings.
        certificate (Optional[AgentProfileCertificate]): Certificate settings.
        client_certificate (Optional[ClientCertificate]): Client certificate settings.
        custom_checks (Optional[CustomChecks]): Custom checks settings.
        gateways (Optional[Gateways]): Gateways configuration.
        gp_app_config (Optional[GPAppConfig]): GlobalProtect app configuration.
        hip_collection (Optional[HipCollection]): HIP collection settings.
        internal_host_detection (Optional[InternalHostDetection]): Internal host
            detection (IPv4) settings.
        internal_host_detection_v6 (Optional[InternalHostDetectionV6]): Internal host
            detection (IPv6) settings.
        machine_account_exists_with_serialno (Optional[MachineAccountExistsWithSerialno]):
            Machine account exists with serial number setting.
        os (Optional[List[AgentProfileOperatingSystem]]): The operating systems this
            agent profile applies to.
        save_user_credentials (Optional[SaveUserCredentials]): Save user credentials
            behavior.
        source_user (Optional[List[str]]): The source users this agent profile
            applies to.
        third_party_vpn_clients (Optional[List[ThirdPartyVpnClient]]): The third party
            VPN clients supported by this agent profile.

    Error:
        ValueError: Raised when validation fails for any field or when folder is not
            'Mobile Users'.

    """

    # Pydantic model configuration
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    # Required fields
    name: str = Field(
        ...,
        description="The name of the agent profile",
    )

    # Container fields
    folder: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        description="The folder in which the resource is defined",
        examples=["Mobile Users"],
    )

    # Optional fields
    agent_ui: Optional[AgentUI] = Field(
        None,
        description="Agent UI configuration settings",
    )
    authentication_override: Optional[AuthenticationOverride] = Field(
        None,
        description="Authentication override settings",
    )
    certificate: Optional[AgentProfileCertificate] = Field(
        None,
        description="Certificate settings",
    )
    client_certificate: Optional[ClientCertificate] = Field(
        None,
        description="Client certificate settings",
    )
    custom_checks: Optional[CustomChecks] = Field(
        None,
        description="Custom checks settings",
    )
    gateways: Optional[Gateways] = Field(
        None,
        description="Gateways configuration",
    )
    gp_app_config: Optional[GPAppConfig] = Field(
        None,
        description="GlobalProtect app configuration",
    )
    hip_collection: Optional[HipCollection] = Field(
        None,
        description="HIP collection settings",
    )
    internal_host_detection: Optional[InternalHostDetection] = Field(
        None,
        description="Internal host detection (IPv4) settings",
    )
    internal_host_detection_v6: Optional[InternalHostDetectionV6] = Field(
        None,
        description="Internal host detection (IPv6) settings",
    )
    machine_account_exists_with_serialno: Optional[MachineAccountExistsWithSerialno] = Field(
        None,
        description="Machine account exists with serial number setting",
    )
    os: Optional[List[AgentProfileOperatingSystem]] = Field(
        None,
        description="The operating systems this agent profile applies to",
    )
    save_user_credentials: Optional[SaveUserCredentials] = Field(
        None,
        description="Save user credentials behavior",
    )
    source_user: Optional[List[str]] = Field(
        None,
        description="The source users this agent profile applies to",
    )
    third_party_vpn_clients: Optional[List[ThirdPartyVpnClient]] = Field(
        None,
        description="The third party VPN clients supported by this agent profile",
    )

    @field_validator("folder")
    def validate_folder(cls, v):  # noqa
        """Validate that folder is 'Mobile Users' if provided."""
        if v is not None and v != "Mobile Users":
            raise ValueError("Folder must be 'Mobile Users' for GlobalProtect Agent Profiles")
        return v


class AgentProfilesCreateModel(AgentProfilesBaseModel):
    """Represents the creation of a new GlobalProtect Agent Profile.

    This class defines the structure and validation rules for creating agent profiles,
    ensuring that folder is set to 'Mobile Users'.

    Error:
        ValueError: Raised when folder is not provided or not set to 'Mobile Users'.

    """

    @model_validator(mode="after")
    def validate_container_type(self) -> "AgentProfilesCreateModel":
        """Validate that folder is provided and set to 'Mobile Users'."""
        if not self.folder:
            raise ValueError("Folder is required for GlobalProtect Agent Profiles")
        return self


class AgentProfilesUpdateModel(AgentProfilesBaseModel):
    """Represents the update of an existing GlobalProtect Agent Profile.

    Agent profiles are addressed by name within the 'Mobile Users' folder (there is
    no id in the update path), so both name and folder are required for updates.

    Error:
        ValueError: Raised when folder is not provided or not set to 'Mobile Users'.

    """

    @model_validator(mode="after")
    def validate_container_type(self) -> "AgentProfilesUpdateModel":
        """Validate that folder is provided and set to 'Mobile Users'."""
        if not self.folder:
            raise ValueError("Folder is required for GlobalProtect Agent Profiles")
        return self


class AgentProfilesResponseModel(AgentProfilesBaseModel):
    """Represents the response model for GlobalProtect Agent Profiles.

    This class defines the structure for agent profiles returned by the API.
    """

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )
