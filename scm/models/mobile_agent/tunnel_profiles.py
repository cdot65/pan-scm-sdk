"""Tunnel Profiles models for Strata Cloud Manager SDK.

Contains Pydantic models for representing GlobalProtect tunnel settings
(tunnel profiles) and related data.
"""

# scm/models/mobile_agent/tunnel_profiles.py

# Standard library imports
from enum import Enum
from typing import List, Optional

# External libraries
from pydantic import BaseModel, ConfigDict, Field, field_validator


class TunnelOperatingSystem(str, Enum):
    """Available operating systems for GlobalProtect tunnel profiles."""

    ANDROID = "Android"
    CHROME = "Chrome"
    IOT = "IoT"
    LINUX = "Linux"
    MAC = "Mac"
    WINDOWS = "Windows"
    WINDOWS_UWP = "WindowsUWP"
    IOS = "iOS"


class CookieLifetime(BaseModel):
    """Cookie lifetime configuration for authentication override cookies.

    Attributes:
        lifetime_in_days (Optional[int]): Cookie lifetime in days (1-365).
        lifetime_in_hours (Optional[int]): Cookie lifetime in hours (1-72).
        lifetime_in_minutes (Optional[int]): Cookie lifetime in minutes (1-59).

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    lifetime_in_days: Optional[int] = Field(
        None,
        ge=1,
        le=365,
        description="Cookie lifetime in days (1-365)",
    )
    lifetime_in_hours: Optional[int] = Field(
        None,
        ge=1,
        le=72,
        description="Cookie lifetime in hours (1-72)",
    )
    lifetime_in_minutes: Optional[int] = Field(
        None,
        ge=1,
        le=59,
        description="Cookie lifetime in minutes (1-59)",
    )


class AcceptCookie(BaseModel):
    """Accept cookie configuration for authentication override.

    Attributes:
        cookie_lifetime (Optional[CookieLifetime]): The lifetime of the authentication cookie.
        cookie_encrypt_decrypt_cert (Optional[str]): The certificate used to encrypt and
            decrypt the authentication cookie.
        generate_cookie (Optional[bool]): Whether to generate an authentication cookie.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    cookie_lifetime: Optional[CookieLifetime] = Field(
        None,
        description="The lifetime of the authentication cookie",
    )
    cookie_encrypt_decrypt_cert: Optional[str] = Field(
        None,
        description="The certificate used to encrypt and decrypt the authentication cookie",
    )
    generate_cookie: Optional[bool] = Field(
        None,
        description="Whether to generate an authentication cookie",
    )


class AuthenticationOverride(BaseModel):
    """Authentication override configuration for tunnel profiles.

    Attributes:
        accept_cookie (Optional[AcceptCookie]): Accept cookie configuration.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    accept_cookie: Optional[AcceptCookie] = Field(
        None,
        description="Accept cookie configuration",
    )


class SourceAddress(BaseModel):
    """Source address configuration for tunnel profiles.

    Attributes:
        ip_address (Optional[List[str]]): List of source IP addresses.
        region (Optional[List[str]]): List of source regions.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    ip_address: Optional[List[str]] = Field(
        None,
        description="List of source IP addresses",
    )
    region: Optional[List[str]] = Field(
        None,
        description="List of source regions",
    )


class SplitTunnelingDomainEntry(BaseModel):
    """Domain entry for split tunneling include/exclude domain lists.

    Attributes:
        name (Optional[str]): The domain name.
        ports (Optional[List[int]]): The ports for the domain (1-65535).

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    name: Optional[str] = Field(
        None,
        description="The domain name",
    )
    ports: Optional[List[int]] = Field(
        None,
        description="The ports for the domain (1-65535)",
    )

    @field_validator("ports")
    def validate_ports(cls, v):  # noqa
        """Validate that each port is within the valid range (1-65535)."""
        if v is not None:
            for port in v:
                if port < 1 or port > 65535:
                    raise ValueError("Ports must be between 1 and 65535")
        return v


class SplitTunnelingDomains(BaseModel):
    """Domain list container for split tunneling include/exclude domains.

    Attributes:
        list (Optional[List[SplitTunnelingDomainEntry]]): List of domain entries.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    list: Optional[List[SplitTunnelingDomainEntry]] = Field(
        None,
        description="List of domain entries",
    )


class SplitTunneling(BaseModel):
    """Split tunneling configuration for tunnel profiles.

    Attributes:
        access_route (Optional[List[str]]): Routes included in the tunnel.
        exclude_access_route (Optional[List[str]]): Routes excluded from the tunnel.
        exclude_applications (Optional[List[str]]): Applications excluded from the tunnel.
        exclude_domains (Optional[SplitTunnelingDomains]): Domains excluded from the tunnel.
        include_applications (Optional[List[str]]): Applications included in the tunnel.
        include_domains (Optional[SplitTunnelingDomains]): Domains included in the tunnel.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    access_route: Optional[List[str]] = Field(
        None,
        description="Routes included in the tunnel",
    )
    exclude_access_route: Optional[List[str]] = Field(
        None,
        description="Routes excluded from the tunnel",
    )
    exclude_applications: Optional[List[str]] = Field(
        None,
        description="Applications excluded from the tunnel",
    )
    exclude_domains: Optional[SplitTunnelingDomains] = Field(
        None,
        description="Domains excluded from the tunnel",
    )
    include_applications: Optional[List[str]] = Field(
        None,
        description="Applications included in the tunnel",
    )
    include_domains: Optional[SplitTunnelingDomains] = Field(
        None,
        description="Domains included in the tunnel",
    )


class TunnelProfileBaseModel(BaseModel):
    """Base model for GlobalProtect Tunnel Profiles containing fields common to all CRUD operations.

    Attributes:
        name (str): The name of the tunnel profile.
        authentication_override (Optional[AuthenticationOverride]): Authentication override
            configuration.
        no_direct_access_to_local_network (Optional[bool]): Whether direct access to the
            local network is disabled.
        os (Optional[List[TunnelOperatingSystem]]): The operating systems this tunnel
            profile applies to.
        retrieve_framed_ip_address (Optional[bool]): Whether to retrieve the framed IP
            address from the authentication server.
        source_address (Optional[SourceAddress]): Source address configuration.
        source_user (Optional[List[str]]): The source users this tunnel profile applies to.
        split_tunneling (Optional[SplitTunneling]): Split tunneling configuration.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    name: str = Field(
        ...,
        min_length=1,
        max_length=31,
        description="The name of the tunnel profile",
    )
    authentication_override: Optional[AuthenticationOverride] = Field(
        None,
        description="Authentication override configuration",
    )
    no_direct_access_to_local_network: Optional[bool] = Field(
        None,
        description="Whether direct access to the local network is disabled",
    )
    os: Optional[List[TunnelOperatingSystem]] = Field(
        None,
        description="The operating systems this tunnel profile applies to",
    )
    retrieve_framed_ip_address: Optional[bool] = Field(
        None,
        description="Whether to retrieve the framed IP address from the authentication server",
    )
    source_address: Optional[SourceAddress] = Field(
        None,
        description="Source address configuration",
    )
    source_user: Optional[List[str]] = Field(
        None,
        description="The source users this tunnel profile applies to",
    )
    split_tunneling: Optional[SplitTunneling] = Field(
        None,
        description="Split tunneling configuration",
    )


class TunnelProfileCreateModel(TunnelProfileBaseModel):
    """Represents the creation of a new GlobalProtect Tunnel Profile.

    Tunnel profiles are addressed by name within the 'Mobile Users' folder, which
    is supplied as a query parameter by the service class rather than in the body.
    """


class TunnelProfileUpdateModel(TunnelProfileBaseModel):
    """Represents the update of an existing GlobalProtect Tunnel Profile.

    Tunnel profiles have no unique identifier in the API; updates are addressed
    by the profile name within the 'Mobile Users' folder.
    """


class TunnelProfileResponseModel(TunnelProfileBaseModel):
    """Represents the response model for GlobalProtect Tunnel Profiles.

    This class defines the structure for tunnel profiles returned by the API.

    Attributes:
        folder (Optional[str]): The folder in which the resource is defined.

    """

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    folder: Optional[str] = Field(
        None,
        description="The folder in which the resource is defined",
        examples=["Mobile Users"],
    )
