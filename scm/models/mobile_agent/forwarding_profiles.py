"""Forwarding Profile models for Strata Cloud Manager SDK.

Contains Pydantic models for representing GlobalProtect forwarding profiles and related data.
"""

# scm/models/mobile_agent/forwarding_profiles.py

# Standard library imports
from enum import Enum
from typing import List, Optional, Union
from uuid import UUID

# External libraries
from pydantic import BaseModel, ConfigDict, Field


class DefinitionMethod(str, Enum):
    """Available definition methods for GlobalProtect forwarding profiles."""

    RULES = "rules"
    PAC_FILE = "pac-file"


class ZtnaTrafficType(str, Enum):
    """Available traffic types for ZTNA agent forwarding rules."""

    DNS = "dns"
    DNS_AND_NETWORK_TRAFFIC = "dns-and-network-traffic"
    NETWORK_TRAFFIC = "network-traffic"


class ForwardingRuleBasic(BaseModel):
    """Forwarding rule for PAC file and GlobalProtect proxy forwarding profiles.

    Attributes:
        name (str): The name of the forwarding rule.
        enabled (Optional[bool]): Enable the forwarding rule.
        user_locations (Optional[str]): The user locations the rule applies to.
        destinations (Optional[str]): The destinations the rule applies to.
        connectivity (Optional[str]): The connectivity method for matching traffic.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    name: str = Field(
        ...,
        description="The name of the forwarding rule",
        max_length=64,
        pattern=r"^[0-9a-zA-Z._-]+$",
    )
    enabled: Optional[bool] = Field(
        default=True,
        description="Enable forwarding rule",
    )
    user_locations: Optional[str] = Field(
        default="Any",
        description="The user locations the rule applies to",
        max_length=64,
    )
    destinations: Optional[str] = Field(
        default="Any",
        description="The destinations the rule applies to",
        max_length=64,
    )
    connectivity: Optional[str] = Field(
        default="direct",
        description="The connectivity method for matching traffic",
        max_length=64,
    )


class ForwardingRuleZtna(BaseModel):
    """Forwarding rule for ZTNA agent forwarding profiles.

    Attributes:
        name (str): The name of the forwarding rule.
        traffic_type (Optional[ZtnaTrafficType]): The type of traffic the rule applies to.
        enabled (Optional[bool]): Enable the forwarding rule.
        user_locations (Optional[str]): The user locations the rule applies to.
        source_applications (Optional[str]): The source applications the rule applies to.
        destinations (Optional[str]): The destinations the rule applies to.
        connectivity (Optional[str]): The connectivity method for matching traffic.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    name: str = Field(
        ...,
        description="The name of the forwarding rule",
        max_length=64,
        pattern=r"^[0-9a-zA-Z._-]+$",
    )
    traffic_type: Optional[ZtnaTrafficType] = Field(
        default=ZtnaTrafficType.DNS,
        description="The type of traffic the rule applies to",
    )
    enabled: Optional[bool] = Field(
        default=True,
        description="Enable forwarding rule",
    )
    user_locations: Optional[str] = Field(
        default="Any",
        description="The user locations the rule applies to",
        max_length=64,
    )
    source_applications: Optional[str] = Field(
        default="Any",
        description="The source applications the rule applies to",
    )
    destinations: Optional[str] = Field(
        default="Any",
        description="The destinations the rule applies to",
        max_length=64,
    )
    connectivity: Optional[str] = Field(
        default="direct",
        description="The connectivity method for matching traffic",
        max_length=64,
    )


class BlockRuleBasicAllowTcp(BaseModel):
    """Allow-TCP settings for a basic block rule.

    Attributes:
        enable_locations (Optional[bool]): Enable locations for allow-tcp.
        locations (Optional[List[str]]): The locations allowed for TCP traffic.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    enable_locations: Optional[bool] = Field(
        default=None,
        description="Enable locations for allow-tcp",
    )
    locations: Optional[List[str]] = Field(
        default=None,
        description="The locations allowed for TCP traffic",
    )


class BlockRuleBasicAllowUdp(BaseModel):
    """Allow-UDP settings for a basic block rule.

    Attributes:
        enable_locations (Optional[bool]): Enable locations for allow-udp.
        enable_destinations (Optional[bool]): Enable destinations for allow-udp.
        locations (Optional[List[str]]): The locations allowed for UDP traffic.
        destinations (Optional[str]): The destinations allowed for UDP traffic.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    enable_locations: Optional[bool] = Field(
        default=None,
        description="Enable locations for allow-udp",
    )
    enable_destinations: Optional[bool] = Field(
        default=None,
        description="Enable destinations for allow-udp",
    )
    locations: Optional[List[str]] = Field(
        default=None,
        description="The locations allowed for UDP traffic",
    )
    destinations: Optional[str] = Field(
        default=None,
        description="The destinations allowed for UDP traffic",
        max_length=64,
    )


class BlockRuleBasic(BaseModel):
    """Block rule for PAC file and GlobalProtect proxy forwarding profiles.

    Attributes:
        enable (Optional[bool]): Enable the block rule.
        allow_tcp (Optional[BlockRuleBasicAllowTcp]): Allow-TCP settings.
        allow_udp (Optional[BlockRuleBasicAllowUdp]): Allow-UDP settings.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    enable: Optional[bool] = Field(
        default=None,
        description="Enable block rule",
    )
    allow_tcp: Optional[BlockRuleBasicAllowTcp] = Field(
        default=None,
        description="Allow-TCP settings for the block rule",
    )
    allow_udp: Optional[BlockRuleBasicAllowUdp] = Field(
        default=None,
        description="Allow-UDP settings for the block rule",
    )


class BlockRuleZtna(BaseModel):
    """Block rule for ZTNA agent forwarding profiles.

    Attributes:
        block_all_other_unmatched_outbound_connections (Optional[bool]): Block all other
            unmatched outbound connections.
        block_outbound_lan_access_when_connected_to_tunnel (Optional[bool]): Block outbound
            LAN access when connected to tunnel.
        block_inbound_access_when_connected_to_tunnel (Optional[bool]): Block inbound access
            when connected to tunnel.
        block_non_tcp_non_udp_based_traffic_when_connected_to_tunnel (Optional[bool]): Block
            non-TCP, non-UDP based traffic when connected to tunnel.
        allow_icmp_for_troubleshooting (Optional[bool]): Allow ICMP for troubleshooting.
        enforcer_fqdn_dns_resolution_via_dns_servers (Optional[bool]): Enforce FQDN DNS
            resolution via tunnel DNS servers.
        resolve_all_fqdns_using_dns_servers_assigned_by_the_tunnel (Optional[bool]): Resolve
            all FQDNs using DNS servers assigned by the tunnel (Windows only).

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    block_all_other_unmatched_outbound_connections: Optional[bool] = Field(
        default=False,
        description="Block all other unmatched outbound connections",
    )
    block_outbound_lan_access_when_connected_to_tunnel: Optional[bool] = Field(
        default=False,
        description="Block outbound LAN access when connected to tunnel",
    )
    block_inbound_access_when_connected_to_tunnel: Optional[bool] = Field(
        default=False,
        description="Block inbound access when connected to tunnel",
    )
    block_non_tcp_non_udp_based_traffic_when_connected_to_tunnel: Optional[bool] = Field(
        default=False,
        description="Block Non-TCP Non UDP based traffic when connected to tunnel",
    )
    allow_icmp_for_troubleshooting: Optional[bool] = Field(
        default=False,
        description="Allow ICMP for troubleshooting",
    )
    enforcer_fqdn_dns_resolution_via_dns_servers: Optional[bool] = Field(
        default=True,
        description="Enforce FQDN DNS resolution via tunnel DNS servers",
    )
    resolve_all_fqdns_using_dns_servers_assigned_by_the_tunnel: Optional[bool] = Field(
        default=True,
        description="Resolve All FQDNs using DNS servers assigned by the tunnel (Windows Only)",
    )


class BasicForwardingConfig(BaseModel):
    """Forwarding configuration for PAC file and GlobalProtect proxy profile types.

    Attributes:
        pac_upload (Optional[bool]): User upload PAC file.
        forwarding_rules (Optional[List[ForwardingRuleBasic]]): The forwarding rules.
        block_rule (Optional[BlockRuleBasic]): The block rule.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    pac_upload: Optional[bool] = Field(
        default=False,
        description="User upload PAC file",
    )
    forwarding_rules: Optional[List[ForwardingRuleBasic]] = Field(
        default=None,
        description="The forwarding rules for the profile",
    )
    block_rule: Optional[BlockRuleBasic] = Field(
        default=None,
        description="The block rule for the profile",
    )


class ZtnaForwardingConfig(BaseModel):
    """Forwarding configuration for the ZTNA agent profile type.

    Attributes:
        pac_upload (Optional[bool]): User upload PAC file.
        forwarding_rules (Optional[List[ForwardingRuleZtna]]): The forwarding rules.
        block_rule (Optional[BlockRuleZtna]): The block rule.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    pac_upload: Optional[bool] = Field(
        default=False,
        description="User upload PAC file",
    )
    forwarding_rules: Optional[List[ForwardingRuleZtna]] = Field(
        default=None,
        description="The forwarding rules for the profile",
    )
    block_rule: Optional[BlockRuleZtna] = Field(
        default=None,
        description="The block rule for the profile",
    )


class ForwardingProfilePacFile(BaseModel):
    """PAC file forwarding profile type.

    Attributes:
        pac_file (BasicForwardingConfig): The PAC file forwarding configuration.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    pac_file: BasicForwardingConfig = Field(
        ...,
        description="The PAC file forwarding configuration",
    )


class ForwardingProfileGlobalProtectProxy(BaseModel):
    """GlobalProtect proxy forwarding profile type.

    Attributes:
        global_protect_proxy (BasicForwardingConfig): The GlobalProtect proxy forwarding
            configuration.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    global_protect_proxy: BasicForwardingConfig = Field(
        ...,
        description="The GlobalProtect proxy forwarding configuration",
    )


class ForwardingProfileZtnaAgent(BaseModel):
    """ZTNA agent forwarding profile type.

    Attributes:
        ztna_agent (ZtnaForwardingConfig): The ZTNA agent forwarding configuration.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    ztna_agent: ZtnaForwardingConfig = Field(
        ...,
        description="The ZTNA agent forwarding configuration",
    )


class ForwardingProfileBaseModel(BaseModel):
    """Base model for GlobalProtect Forwarding Profiles containing fields common to all CRUD operations.

    Attributes:
        name (str): The name of the forwarding profile.
        description (Optional[str]): The description of the forwarding profile.
        definition_method (Optional[DefinitionMethod]): How the profile is defined (rules or pac-file).
        type (Optional[Union[ForwardingProfilePacFile, ForwardingProfileGlobalProtectProxy,
            ForwardingProfileZtnaAgent]]): The forwarding profile type configuration.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    name: str = Field(
        ...,
        description="The name of the forwarding profile",
        max_length=64,
        pattern=r"^[0-9a-zA-Z._-]+$",
    )
    description: Optional[str] = Field(
        default=None,
        description="The description of the forwarding profile",
        max_length=1023,
    )
    definition_method: Optional[DefinitionMethod] = Field(
        default=DefinitionMethod.RULES,
        description="How the forwarding profile is defined (rules or pac-file)",
    )
    type: Optional[
        Union[
            ForwardingProfilePacFile,
            ForwardingProfileGlobalProtectProxy,
            ForwardingProfileZtnaAgent,
        ]
    ] = Field(
        default=None,
        description="The forwarding profile type configuration",
    )


class ForwardingProfileCreateModel(ForwardingProfileBaseModel):
    """Represents the creation of a new GlobalProtect Forwarding Profile.

    This class defines the structure and validation rules for creating forwarding profiles.
    The folder is supplied as a query parameter by the service class, not in the request body.
    """


class ForwardingProfileUpdateModel(ForwardingProfileBaseModel):
    """Represents the update of an existing GlobalProtect Forwarding Profile.

    This class defines the structure and validation rules for updating forwarding profiles.
    The object ID is supplied in the URL path by the service class; if provided here it is
    removed from the request payload.

    Attributes:
        id (Optional[UUID]): The UUID of the forwarding profile.

    """

    id: Optional[UUID] = Field(
        default=None,
        description="The UUID of the forwarding profile",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class ForwardingProfileResponseModel(ForwardingProfileBaseModel):
    """Represents the response model for GlobalProtect Forwarding Profiles.

    This class defines the structure for forwarding profiles returned by the API.

    Attributes:
        id (Optional[UUID]): The UUID of the forwarding profile.

    """

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    id: Optional[UUID] = Field(
        default=None,
        description="The UUID of the forwarding profile",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
