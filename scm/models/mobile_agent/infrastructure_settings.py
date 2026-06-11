"""Infrastructure Settings models for Strata Cloud Manager SDK.

Contains Pydantic models for representing GlobalProtect infrastructure settings and related data.
"""

# scm/models/mobile_agent/infrastructure_settings.py

# Standard library imports
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

# External libraries
from pydantic import BaseModel, ConfigDict, Field


class DnsServerSelection(BaseModel):
    """Primary or secondary DNS server selection for an internal DNS match entry.

    Attributes:
        dns_server (Optional[Dict[str, Any]]): The DNS server configuration.
        use_cloud_default (Optional[Dict[str, Any]]): Use the cloud default DNS server.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    dns_server: Optional[Dict[str, Any]] = Field(
        None,
        description="The DNS server configuration",
    )
    use_cloud_default: Optional[Dict[str, Any]] = Field(
        None,
        description="Use the cloud default DNS server",
    )


class InternalDnsMatch(BaseModel):
    """Internal DNS match entry for a DNS server configuration.

    Attributes:
        name (Optional[str]): The name of the internal DNS match entry.
        domain_list (Optional[List[str]]): Domains to resolve with internal DNS servers.
        primary (Optional[DnsServerSelection]): The primary DNS server selection.
        secondary (Optional[DnsServerSelection]): The secondary DNS server selection.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    name: Optional[str] = Field(
        None,
        description="The name of the internal DNS match entry",
    )
    domain_list: Optional[List[str]] = Field(
        None,
        description="Domains to resolve with the internal DNS servers",
    )
    primary: Optional[DnsServerSelection] = Field(
        None,
        description="The primary DNS server selection",
    )
    secondary: Optional[DnsServerSelection] = Field(
        None,
        description="The secondary DNS server selection",
    )


class PublicDnsServer(BaseModel):
    """Public DNS server configuration.

    Attributes:
        dns_server (Optional[str]): The IP address of the public DNS server.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    dns_server: Optional[str] = Field(
        None,
        description="The IP address of the public DNS server",
    )


class DnsServerEntry(BaseModel):
    """DNS server entry for GlobalProtect infrastructure settings.

    Attributes:
        name (Optional[str]): The name of the DNS server entry.
        dns_suffix (Optional[List[str]]): DNS suffixes for the mobile users environment.
        internal_dns_match (Optional[List[InternalDnsMatch]]): Internal DNS match entries.
        primary_public_dns (Optional[PublicDnsServer]): The primary public DNS server.
        secondary_public_dns (Optional[PublicDnsServer]): The secondary public DNS server.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    name: Optional[str] = Field(
        None,
        description="The name of the DNS server entry",
    )
    dns_suffix: Optional[List[str]] = Field(
        None,
        description="DNS suffixes for the mobile users environment",
    )
    internal_dns_match: Optional[List[InternalDnsMatch]] = Field(
        None,
        description="Internal DNS match entries",
    )
    primary_public_dns: Optional[PublicDnsServer] = Field(
        None,
        description="The primary public DNS server",
    )
    secondary_public_dns: Optional[PublicDnsServer] = Field(
        None,
        description="The secondary public DNS server",
    )


class WinsServerEntry(BaseModel):
    """WINS server entry for GlobalProtect infrastructure settings.

    Attributes:
        name (Optional[str]): The name of the WINS server entry.
        primary (Optional[str]): The primary WINS server.
        secondary (Optional[str]): The secondary WINS server.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    name: Optional[str] = Field(
        None,
        description="The name of the WINS server entry",
    )
    primary: Optional[str] = Field(
        None,
        description="The primary WINS server",
    )
    secondary: Optional[str] = Field(
        None,
        description="The secondary WINS server",
    )


class EnableWinsYes(BaseModel):
    """Configuration when WINS is enabled.

    Attributes:
        wins_servers (Optional[List[WinsServerEntry]]): The WINS servers.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    wins_servers: Optional[List[WinsServerEntry]] = Field(
        None,
        description="The WINS servers",
    )


class EnableWins(BaseModel):
    """Enable or disable WINS for GlobalProtect infrastructure settings.

    Exactly one of 'yes' or 'no' is expected by the API.

    Attributes:
        no (Optional[Dict[str, Any]]): WINS is disabled.
        yes (Optional[EnableWinsYes]): WINS is enabled with the given WINS servers.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    no: Optional[Dict[str, Any]] = Field(
        None,
        description="WINS is disabled",
    )
    yes: Optional[EnableWinsYes] = Field(
        None,
        description="WINS is enabled with the given WINS servers",
    )


class IpPool(BaseModel):
    """IP pool entry for GlobalProtect infrastructure settings.

    Attributes:
        name (Optional[str]): The name of the IP pool.
        ip_pool (Optional[List[str]]): The IP subnets of the pool.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    name: Optional[str] = Field(
        None,
        description="The name of the IP pool",
    )
    ip_pool: Optional[List[str]] = Field(
        None,
        description="The IP subnets of the pool",
    )


class CustomDomain(BaseModel):
    """Custom domain configuration for the GlobalProtect portal hostname.

    Attributes:
        cname (Optional[str]): The CNAME record of the custom domain.
        hostname (Optional[str]): The hostname of the custom domain.
        ssl_tls_service_profile (Optional[str]): The SSL/TLS service profile name.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    cname: Optional[str] = Field(
        None,
        description="The CNAME record of the custom domain",
    )
    hostname: Optional[str] = Field(
        None,
        description="The hostname of the custom domain",
    )
    ssl_tls_service_profile: Optional[str] = Field(
        None,
        description=(
            "The SSL/TLS service profile name. The value muCustomDomainSSLProfile "
            "references the corresponding certificate under ssl-tls-service-profile "
            "automatically"
        ),
    )


class DefaultDomain(BaseModel):
    """Default domain configuration for the GlobalProtect portal hostname.

    Attributes:
        hostname (Optional[str]): The hostname of the default domain.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    hostname: Optional[str] = Field(
        None,
        description="The hostname of the default domain",
    )


class PortalHostname(BaseModel):
    """Portal hostname configuration for GlobalProtect infrastructure settings.

    Attributes:
        custom_domain (Optional[CustomDomain]): The custom domain configuration.
        default_domain (Optional[DefaultDomain]): The default domain configuration.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    custom_domain: Optional[CustomDomain] = Field(
        None,
        description="The custom domain configuration",
    )
    default_domain: Optional[DefaultDomain] = Field(
        None,
        description="The default domain configuration",
    )


class UdpQueryRetries(BaseModel):
    """UDP query retry configuration for GlobalProtect infrastructure settings.

    Attributes:
        attempts (Optional[int]): Maximum number of retries before trying the next name server.
        interval (Optional[int]): Time in seconds for another request to be sent.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    attempts: Optional[int] = Field(
        None,
        ge=1,
        le=30,
        description="Maximum number of retries before trying the next name server",
    )
    interval: Optional[int] = Field(
        None,
        ge=1,
        le=30,
        description="Time in seconds for another request to be sent",
    )


class UdpQueries(BaseModel):
    """UDP query configuration for GlobalProtect infrastructure settings.

    Attributes:
        retries (Optional[UdpQueryRetries]): The UDP query retry configuration.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    retries: Optional[UdpQueryRetries] = Field(
        None,
        description="The UDP query retry configuration",
    )


class UserGroup(BaseModel):
    """User group entry for a static IP pool.

    Attributes:
        name (Optional[str]): Distinguished Name of the group.
        directory (Optional[str]): The directory of the group.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    name: Optional[str] = Field(
        None,
        max_length=320,
        description="Distinguished Name of the group",
    )
    directory: Optional[str] = Field(
        None,
        description="The directory of the group",
    )


class StaticIpPool(BaseModel):
    """Static IP pool entry for GlobalProtect infrastructure settings.

    Attributes:
        name (Optional[str]): Name of the static-ip-pool entry.
        pool_type (Optional[Literal["Static-IP"]]): The type of the pool.
        ip_pool (Optional[List[str]]): IP subnets.
        theatres (Optional[List[str]]): IP pools on theatres.
        users (Optional[List[str]]): IP pools on users.
        user_groups (Optional[List[UserGroup]]): IP pools on user groups.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    name: Optional[str] = Field(
        None,
        max_length=128,
        description="Name of the static-ip-pool entry. Alphanumeric string [0-9a-zA-Z._-]",
    )
    pool_type: Optional[Literal["Static-IP"]] = Field(
        None,
        description="The type of the pool",
    )
    ip_pool: Optional[List[str]] = Field(
        None,
        description="IP subnets",
    )
    theatres: Optional[List[str]] = Field(
        None,
        description="IP pools on theatres",
    )
    users: Optional[List[str]] = Field(
        None,
        description="IP pools on users",
    )
    user_groups: Optional[List[UserGroup]] = Field(
        None,
        description="IP pools on user groups",
    )


class InfrastructureSettingsBaseModel(BaseModel):
    """Base model for GlobalProtect Infrastructure Settings containing fields common to all CRUD operations.

    Infrastructure settings are addressed by name within the 'Mobile Users' folder,
    which is passed as a query parameter rather than a body field.

    Attributes:
        name (str): The name of the infrastructure settings.
        dns_servers (List[DnsServerEntry]): The DNS server entries.
        ip_pools (List[IpPool]): The IP pools.
        portal_hostname (PortalHostname): The portal hostname configuration.
        enable_wins (Optional[EnableWins]): The WINS configuration.
        ipv6 (Optional[bool]): Whether IPv6 is enabled.
        udp_queries (Optional[UdpQueries]): The UDP query configuration.
        static_ip_pools (Optional[List[StaticIpPool]]): The static IP pools.

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
        description="The name of the infrastructure settings",
    )
    dns_servers: List[DnsServerEntry] = Field(
        ...,
        description="The DNS server entries",
    )
    ip_pools: List[IpPool] = Field(
        ...,
        description="The IP pools",
    )
    portal_hostname: PortalHostname = Field(
        ...,
        description="The portal hostname configuration",
    )

    # Optional fields
    enable_wins: Optional[EnableWins] = Field(
        None,
        description="The WINS configuration",
    )
    ipv6: Optional[bool] = Field(
        None,
        description="Whether IPv6 is enabled",
    )
    udp_queries: Optional[UdpQueries] = Field(
        None,
        description="The UDP query configuration",
    )
    static_ip_pools: Optional[List[StaticIpPool]] = Field(
        None,
        description="The static IP pools",
    )


class InfrastructureSettingsCreateModel(InfrastructureSettingsBaseModel):
    """Represents the creation of a new GlobalProtect Infrastructure Settings.

    The target folder ('Mobile Users') is passed as a query parameter by the
    service class, not as a body field.
    """


class InfrastructureSettingsUpdateModel(InfrastructureSettingsBaseModel):
    """Represents the update of an existing GlobalProtect Infrastructure Settings.

    Infrastructure settings are addressed by name and folder rather than by ID,
    so the update payload uses the same shape as the create payload.
    """


class InfrastructureSettingsResponseModel(InfrastructureSettingsBaseModel):
    """Represents the response model for GlobalProtect Infrastructure Settings.

    Attributes:
        id (UUID): The UUID of the resource.

    """

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    id: UUID = Field(
        ...,
        description="The UUID of the resource",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
