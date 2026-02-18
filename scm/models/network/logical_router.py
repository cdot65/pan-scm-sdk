"""Logical Router models for Strata Cloud Manager SDK.

Contains Pydantic models for representing logical router objects and related data.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


# --- Admin Distance Models ---


class AdminDists(BaseModel):
    """Administrative distance settings for a logical router."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    static: Optional[int] = Field(None, description="Static route admin distance")
    static_ipv6: Optional[int] = Field(None, description="Static IPv6 route admin distance")
    ospf_inter: Optional[int] = Field(None, description="OSPF inter-area admin distance")
    ospf_intra: Optional[int] = Field(None, description="OSPF intra-area admin distance")
    ospf_ext: Optional[int] = Field(None, description="OSPF external admin distance")
    ospfv3_inter: Optional[int] = Field(None, description="OSPFv3 inter-area admin distance")
    ospfv3_intra: Optional[int] = Field(None, description="OSPFv3 intra-area admin distance")
    ospfv3_ext: Optional[int] = Field(None, description="OSPFv3 external admin distance")
    bgp_internal: Optional[int] = Field(None, description="BGP internal admin distance")
    bgp_external: Optional[int] = Field(None, description="BGP external admin distance")
    bgp_local: Optional[int] = Field(None, description="BGP local admin distance")
    rip: Optional[int] = Field(None, description="RIP admin distance")


class VrAdminDists(BaseModel):
    """VR administrative distance settings."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    static: Optional[int] = Field(None, description="Static route admin distance")
    static_ipv6: Optional[int] = Field(None, description="Static IPv6 route admin distance")
    ospf_int: Optional[int] = Field(None, description="OSPF internal admin distance")
    ospf_ext: Optional[int] = Field(None, description="OSPF external admin distance")
    ospfv3_int: Optional[int] = Field(None, description="OSPFv3 internal admin distance")
    ospfv3_ext: Optional[int] = Field(None, description="OSPFv3 external admin distance")
    ibgp: Optional[int] = Field(None, description="iBGP admin distance")
    ebgp: Optional[int] = Field(None, description="eBGP admin distance")
    rip: Optional[int] = Field(None, description="RIP admin distance")


# --- RIB Filter Models ---


class RibFilterProtocol(BaseModel):
    """RIB filter protocol entry with route map reference."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    route_map: Optional[str] = Field(None, description="Route map name")


class RibFilterIpv4(BaseModel):
    """RIB filter configuration for IPv4 protocols."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    static: Optional[RibFilterProtocol] = Field(None, description="Static route RIB filter")
    bgp: Optional[RibFilterProtocol] = Field(None, description="BGP RIB filter")
    ospf: Optional[RibFilterProtocol] = Field(None, description="OSPF RIB filter")
    rip: Optional[RibFilterProtocol] = Field(None, description="RIP RIB filter")


class RibFilterIpv6(BaseModel):
    """RIB filter configuration for IPv6 protocols."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    static: Optional[RibFilterProtocol] = Field(None, description="Static route RIB filter")
    bgp: Optional[RibFilterProtocol] = Field(None, description="BGP RIB filter")
    ospfv3: Optional[RibFilterProtocol] = Field(None, description="OSPFv3 RIB filter")


class RibFilter(BaseModel):
    """RIB filter configuration for IPv4 and IPv6."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    ipv4: Optional[RibFilterIpv4] = Field(None, description="IPv4 RIB filters")
    ipv6: Optional[RibFilterIpv6] = Field(None, description="IPv6 RIB filters")


# --- BFD / Path Monitor Models ---


class BfdProfile(BaseModel):
    """BFD profile reference."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    profile: Optional[str] = Field(None, description="BFD profile name")


class MonitorDestination(BaseModel):
    """Path monitor destination entry."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(..., description="Monitor destination name")
    enable: Optional[bool] = Field(None, description="Enable this monitor destination")
    source: Optional[str] = Field(None, description="Source address")
    destination: Optional[str] = Field(None, description="Destination address")
    destination_fqdn: Optional[str] = Field(None, description="Destination FQDN")
    interval: Optional[int] = Field(None, description="Monitor interval")
    count: Optional[int] = Field(None, description="Monitor count")


class PathMonitor(BaseModel):
    """Path monitor configuration for static routes."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    enable: Optional[bool] = Field(None, description="Enable path monitoring")
    failure_condition: Optional[str] = Field(
        None,
        description="Failure condition (any or all)",
        pattern=r"^(any|all)$",
    )
    hold_time: Optional[int] = Field(None, description="Hold time")
    monitor_destinations: Optional[List[MonitorDestination]] = Field(
        None,
        description="List of monitor destinations",
    )


# --- Static Route Models (IPv4) ---


class IPv4Nexthop(BaseModel):
    """IPv4 static route nexthop configuration (oneOf)."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    receive: Optional[Dict[str, Any]] = Field(None, description="Receive nexthop")
    discard: Optional[Dict[str, Any]] = Field(None, description="Discard nexthop")
    ip_address: Optional[str] = Field(None, description="IP address nexthop")
    ipv6_address: Optional[str] = Field(None, description="IPv6 address nexthop")
    fqdn: Optional[str] = Field(None, description="FQDN nexthop")
    next_lr: Optional[str] = Field(None, description="Next logical router nexthop")
    next_vr: Optional[str] = Field(None, description="Next virtual router nexthop")
    tunnel: Optional[str] = Field(None, description="Tunnel nexthop")

    @model_validator(mode="after")
    def validate_nexthop_type(self) -> "IPv4Nexthop":
        """Enforce at most one nexthop type is set."""
        nexthop_fields = [
            self.receive,
            self.discard,
            self.ip_address,
            self.ipv6_address,
            self.fqdn,
            self.next_lr,
            self.next_vr,
            self.tunnel,
        ]
        provided = [f for f in nexthop_fields if f is not None]
        if len(provided) > 1:
            raise ValueError(
                "At most one nexthop type can be set: "
                "receive, discard, ip_address, ipv6_address, fqdn, next_lr, next_vr, or tunnel."
            )
        return self


class IPv4RouteTable(BaseModel):
    """IPv4 static route table selection (oneOf)."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    unicast: Optional[Dict[str, Any]] = Field(None, description="Unicast route table")
    multicast: Optional[Dict[str, Any]] = Field(None, description="Multicast route table")
    both: Optional[Dict[str, Any]] = Field(None, description="Both route tables")
    no_install: Optional[Dict[str, Any]] = Field(None, description="No install route table")

    @model_validator(mode="after")
    def validate_route_table(self) -> "IPv4RouteTable":
        """Enforce at most one route table type is set."""
        fields = [self.unicast, self.multicast, self.both, self.no_install]
        provided = [f for f in fields if f is not None]
        if len(provided) > 1:
            raise ValueError(
                "At most one route table type can be set: unicast, multicast, both, or no_install."
            )
        return self


class IPv4StaticRoute(BaseModel):
    """IPv4 static route configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(..., description="Static route name")
    destination: Optional[str] = Field(None, description="Destination network")
    interface: Optional[str] = Field(None, description="Egress interface")
    nexthop: Optional[IPv4Nexthop] = Field(None, description="Nexthop configuration")
    route_table: Optional[IPv4RouteTable] = Field(None, description="Route table selection")
    admin_dist: Optional[int] = Field(None, description="Administrative distance")
    metric: Optional[int] = Field(None, description="Route metric")
    bfd: Optional[BfdProfile] = Field(None, description="BFD profile")
    path_monitor: Optional[PathMonitor] = Field(None, description="Path monitor configuration")


# --- Static Route Models (IPv6) ---


class IPv6Nexthop(BaseModel):
    """IPv6 static route nexthop configuration (oneOf)."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    receive: Optional[Dict[str, Any]] = Field(None, description="Receive nexthop")
    discard: Optional[Dict[str, Any]] = Field(None, description="Discard nexthop")
    ipv6_address: Optional[str] = Field(None, description="IPv6 address nexthop")
    fqdn: Optional[str] = Field(None, description="FQDN nexthop")
    next_lr: Optional[str] = Field(None, description="Next logical router nexthop")
    next_vr: Optional[str] = Field(None, description="Next virtual router nexthop")
    tunnel: Optional[str] = Field(None, description="Tunnel nexthop")

    @model_validator(mode="after")
    def validate_nexthop_type(self) -> "IPv6Nexthop":
        """Enforce at most one nexthop type is set."""
        nexthop_fields = [
            self.receive,
            self.discard,
            self.ipv6_address,
            self.fqdn,
            self.next_lr,
            self.next_vr,
            self.tunnel,
        ]
        provided = [f for f in nexthop_fields if f is not None]
        if len(provided) > 1:
            raise ValueError(
                "At most one nexthop type can be set: "
                "receive, discard, ipv6_address, fqdn, next_lr, next_vr, or tunnel."
            )
        return self


class IPv6RouteTable(BaseModel):
    """IPv6 static route table selection (oneOf)."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    unicast: Optional[Dict[str, Any]] = Field(None, description="Unicast route table")
    multicast: Optional[Dict[str, Any]] = Field(None, description="Multicast route table")
    both: Optional[Dict[str, Any]] = Field(None, description="Both route tables")
    no_install: Optional[Dict[str, Any]] = Field(None, description="No install route table")

    @model_validator(mode="after")
    def validate_route_table(self) -> "IPv6RouteTable":
        """Enforce at most one route table type is set."""
        fields = [self.unicast, self.multicast, self.both, self.no_install]
        provided = [f for f in fields if f is not None]
        if len(provided) > 1:
            raise ValueError(
                "At most one route table type can be set: unicast, multicast, both, or no_install."
            )
        return self


class IPv6StaticRoute(BaseModel):
    """IPv6 static route configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(..., description="Static route name")
    destination: Optional[str] = Field(None, description="Destination network")
    interface: Optional[str] = Field(None, description="Egress interface")
    nexthop: Optional[IPv6Nexthop] = Field(None, description="Nexthop configuration")
    route_table: Optional[IPv6RouteTable] = Field(None, description="Route table selection")
    admin_dist: Optional[int] = Field(None, description="Administrative distance")
    metric: Optional[int] = Field(None, description="Route metric")
    option: Optional[Dict[str, Any]] = Field(None, description="Route option")
    bfd: Optional[BfdProfile] = Field(None, description="BFD profile")
    path_monitor: Optional[PathMonitor] = Field(None, description="Path monitor configuration")


# --- Routing Table Models ---


class RoutingTableIp(BaseModel):
    """IPv4 routing table configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    static_route: Optional[List[IPv4StaticRoute]] = Field(
        None,
        description="List of IPv4 static routes",
    )


class RoutingTableIpv6(BaseModel):
    """IPv6 routing table configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    static_route: Optional[List[IPv6StaticRoute]] = Field(
        None,
        description="List of IPv6 static routes",
    )


class RoutingTable(BaseModel):
    """Routing table configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    ip: Optional[RoutingTableIp] = Field(None, description="IPv4 routing table")
    ipv6: Optional[RoutingTableIpv6] = Field(None, description="IPv6 routing table")


# --- OSPF Models ---


class OspfMd5Key(BaseModel):
    """OSPF MD5 authentication key."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(..., description="MD5 key ID")
    key: Optional[str] = Field(None, description="MD5 key value")
    preferred: Optional[bool] = Field(None, description="Whether this is the preferred key")


class OspfAuthProfile(BaseModel):
    """OSPF authentication profile (oneOf: password or md5)."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(..., description="Auth profile name")
    password: Optional[str] = Field(None, description="Simple password authentication")
    md5: Optional[List[OspfMd5Key]] = Field(None, description="MD5 authentication keys")

    @model_validator(mode="after")
    def validate_auth_type(self) -> "OspfAuthProfile":
        """Enforce password and md5 are mutually exclusive."""
        if self.password is not None and self.md5 is not None:
            raise ValueError("'password' and 'md5' are mutually exclusive.")
        return self


class OspfFloodPreventionEntry(BaseModel):
    """OSPF flood prevention entry configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    enable: Optional[bool] = Field(None, description="Enable flood prevention")
    max_packet: Optional[int] = Field(None, description="Maximum packets")


class OspfFloodPrevention(BaseModel):
    """OSPF flood prevention configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    hello: Optional[OspfFloodPreventionEntry] = Field(
        None,
        description="Hello flood prevention",
    )
    lsa: Optional[OspfFloodPreventionEntry] = Field(
        None,
        description="LSA flood prevention",
    )


class OspfVrTimers(BaseModel):
    """OSPF VR timer settings."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    spf_calculation_delay: Optional[int] = Field(
        None,
        description="SPF calculation delay",
    )
    lsa_interval: Optional[int] = Field(None, description="LSA interval")


class OspfGracefulRestart(BaseModel):
    """OSPF graceful restart configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    enable: Optional[bool] = Field(None, description="Enable graceful restart")
    grace_period: Optional[int] = Field(None, description="Grace period in seconds")
    helper_enable: Optional[bool] = Field(None, description="Enable helper mode")
    strict_LSA_checking: Optional[bool] = Field(None, description="Enable strict LSA checking")
    max_neighbor_restart_time: Optional[int] = Field(
        None,
        description="Maximum neighbor restart time",
    )


class OspfP2mpNeighbor(BaseModel):
    """OSPF point-to-multipoint neighbor."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(..., description="Neighbor name/address")
    priority: Optional[int] = Field(None, description="Neighbor priority")


class OspfLinkType(BaseModel):
    """OSPF interface link type (oneOf: broadcast, p2p, p2mp)."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    broadcast: Optional[Dict[str, Any]] = Field(None, description="Broadcast link type")
    p2p: Optional[Dict[str, Any]] = Field(None, description="Point-to-point link type")
    p2mp: Optional[Dict[str, Any]] = Field(None, description="Point-to-multipoint link type")

    @model_validator(mode="after")
    def validate_link_type(self) -> "OspfLinkType":
        """Enforce at most one link type is set."""
        fields = [self.broadcast, self.p2p, self.p2mp]
        provided = [f for f in fields if f is not None]
        if len(provided) > 1:
            raise ValueError("At most one link type can be set: broadcast, p2p, or p2mp.")
        return self


class OspfInterfaceVrTiming(BaseModel):
    """OSPF interface VR timing settings."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    hello_interval: Optional[int] = Field(None, description="Hello interval")
    dead_counts: Optional[int] = Field(None, description="Dead counts")
    retransmit_interval: Optional[int] = Field(None, description="Retransmit interval")
    transit_delay: Optional[int] = Field(None, description="Transit delay")
    gr_delay: Optional[int] = Field(None, description="Graceful restart delay")


class OspfInterface(BaseModel):
    """OSPF interface configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(..., description="Interface name")
    enable: Optional[bool] = Field(None, description="Enable OSPF on interface")
    mtu_ignore: Optional[bool] = Field(None, description="Ignore MTU mismatch")
    passive: Optional[bool] = Field(None, description="Passive interface")
    priority: Optional[int] = Field(None, description="Router priority")
    metric: Optional[int] = Field(None, description="Interface metric")
    authentication: Optional[str] = Field(None, description="Authentication profile name")
    link_type: Optional[OspfLinkType] = Field(None, description="Link type")
    bfd: Optional[BfdProfile] = Field(None, description="BFD profile")
    timing: Optional[str] = Field(None, description="Timer profile name")
    vr_timing: Optional[OspfInterfaceVrTiming] = Field(None, description="VR timing settings")


class OspfVirtualLinkVrTiming(BaseModel):
    """OSPF virtual link VR timing settings (no gr_delay)."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    hello_interval: Optional[int] = Field(None, description="Hello interval")
    dead_counts: Optional[int] = Field(None, description="Dead counts")
    retransmit_interval: Optional[int] = Field(None, description="Retransmit interval")
    transit_delay: Optional[int] = Field(None, description="Transit delay")


class OspfVirtualLink(BaseModel):
    """OSPF virtual link configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(..., description="Virtual link name")
    neighbor_id: Optional[str] = Field(None, description="Neighbor router ID")
    transit_area_id: Optional[str] = Field(None, description="Transit area ID")
    enable: Optional[bool] = Field(None, description="Enable virtual link")
    interface_id: Optional[int] = Field(None, description="Interface ID")
    instance_id: Optional[int] = Field(None, description="Instance ID")
    timing: Optional[str] = Field(None, description="Timer profile name")
    passive: Optional[bool] = Field(None, description="Passive virtual link")
    authentication: Optional[str] = Field(None, description="Authentication profile name")
    bfd: Optional[BfdProfile] = Field(None, description="BFD profile")
    vr_timing: Optional[OspfVirtualLinkVrTiming] = Field(
        None,
        description="VR timing settings",
    )


class OspfAreaRange(BaseModel):
    """OSPF area range configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(..., description="Range network address")
    substitute: Optional[str] = Field(None, description="Substitute network address")
    advertise: Optional[bool] = Field(None, description="Advertise this range")


class OspfAreaVrRange(BaseModel):
    """OSPF area VR range configuration (oneOf: advertise or suppress)."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(..., description="Range network address")
    advertise: Optional[Dict[str, Any]] = Field(None, description="Advertise action")
    suppress: Optional[Dict[str, Any]] = Field(None, description="Suppress action")

    @model_validator(mode="after")
    def validate_action(self) -> "OspfAreaVrRange":
        """Enforce advertise and suppress are mutually exclusive."""
        if self.advertise is not None and self.suppress is not None:
            raise ValueError("'advertise' and 'suppress' are mutually exclusive.")
        return self


class OspfStubDefaultRoute(BaseModel):
    """OSPF stub area default route (oneOf: disable or advertise)."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    disable: Optional[Dict[str, Any]] = Field(None, description="Disable default route")
    advertise: Optional[Dict[str, Any]] = Field(None, description="Advertise default route")

    @model_validator(mode="after")
    def validate_default_route(self) -> "OspfStubDefaultRoute":
        """Enforce disable and advertise are mutually exclusive."""
        if self.disable is not None and self.advertise is not None:
            raise ValueError("'disable' and 'advertise' are mutually exclusive.")
        return self


class OspfNssaDefaultRoute(BaseModel):
    """OSPF NSSA area default route (oneOf: disable or advertise)."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    disable: Optional[Dict[str, Any]] = Field(None, description="Disable default route")
    advertise: Optional[Dict[str, Any]] = Field(None, description="Advertise default route")

    @model_validator(mode="after")
    def validate_default_route(self) -> "OspfNssaDefaultRoute":
        """Enforce disable and advertise are mutually exclusive."""
        if self.disable is not None and self.advertise is not None:
            raise ValueError("'disable' and 'advertise' are mutually exclusive.")
        return self


class OspfNssaExtRange(BaseModel):
    """OSPF NSSA external range (oneOf: advertise or suppress)."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(..., description="External range network address")
    advertise: Optional[Dict[str, Any]] = Field(None, description="Advertise action")
    suppress: Optional[Dict[str, Any]] = Field(None, description="Suppress action")

    @model_validator(mode="after")
    def validate_action(self) -> "OspfNssaExtRange":
        """Enforce advertise and suppress are mutually exclusive."""
        if self.advertise is not None and self.suppress is not None:
            raise ValueError("'advertise' and 'suppress' are mutually exclusive.")
        return self


class OspfNormalArea(BaseModel):
    """OSPF normal area type (empty object)."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    pass


class OspfStubArea(BaseModel):
    """OSPF stub area configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    accept_summary: Optional[bool] = Field(None, description="Accept summary LSAs")
    default_route: Optional[OspfStubDefaultRoute] = Field(
        None,
        description="Default route configuration",
    )


class OspfNssaArea(BaseModel):
    """OSPF NSSA area configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    accept_summary: Optional[bool] = Field(None, description="Accept summary LSAs")
    default_route: Optional[OspfNssaDefaultRoute] = Field(
        None,
        description="Default route configuration",
    )
    nssa_ext_range: Optional[List[OspfNssaExtRange]] = Field(
        None,
        description="NSSA external ranges",
    )


class OspfAreaType(BaseModel):
    """OSPF area type (oneOf: normal, stub, nssa)."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    normal: Optional[OspfNormalArea] = Field(None, description="Normal area type")
    stub: Optional[OspfStubArea] = Field(None, description="Stub area type")
    nssa: Optional[OspfNssaArea] = Field(None, description="NSSA area type")

    @model_validator(mode="after")
    def validate_area_type(self) -> "OspfAreaType":
        """Enforce at most one area type is set."""
        fields = [self.normal, self.stub, self.nssa]
        provided = [f for f in fields if f is not None]
        if len(provided) > 1:
            raise ValueError("At most one area type can be set: normal, stub, or nssa.")
        return self


class OspfArea(BaseModel):
    """OSPF area configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(..., description="Area ID")
    authentication: Optional[str] = Field(None, description="Authentication profile name")
    type: Optional[OspfAreaType] = Field(None, description="Area type configuration")
    range: Optional[List[OspfAreaRange]] = Field(None, description="Area ranges")
    vr_range: Optional[List[OspfAreaVrRange]] = Field(None, description="VR area ranges")
    interface: Optional[List[OspfInterface]] = Field(None, description="OSPF interfaces")
    virtual_link: Optional[List[OspfVirtualLink]] = Field(
        None,
        description="OSPF virtual links",
    )


class OspfExportRule(BaseModel):
    """OSPF export rule configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(..., description="Export rule name")
    new_path_type: Optional[str] = Field(
        None,
        description="New path type (ext-1 or ext-2)",
        pattern=r"^(ext-1|ext-2)$",
    )
    new_tag: Optional[str] = Field(None, description="New tag value")
    metric: Optional[int] = Field(None, description="Metric value")


class OspfConfig(BaseModel):
    """OSPF routing protocol configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    router_id: Optional[str] = Field(None, description="OSPF router ID")
    enable: Optional[bool] = Field(None, description="Enable OSPF")
    rfc1583: Optional[bool] = Field(None, description="RFC 1583 compatibility")
    reject_default_route: Optional[bool] = Field(
        None,
        description="Reject default route",
    )
    allow_redist_default_route: Optional[bool] = Field(
        None,
        description="Allow redistribution of default route",
    )
    spf_timer: Optional[str] = Field(None, description="SPF timer profile")
    global_if_timer: Optional[str] = Field(None, description="Global interface timer profile")
    redistribution_profile: Optional[str] = Field(
        None,
        description="Redistribution profile name",
    )
    global_bfd: Optional[BfdProfile] = Field(None, description="Global BFD profile")
    flood_prevention: Optional[OspfFloodPrevention] = Field(
        None,
        description="Flood prevention configuration",
    )
    vr_timers: Optional[OspfVrTimers] = Field(None, description="VR timer settings")
    auth_profile: Optional[List[OspfAuthProfile]] = Field(
        None,
        description="Authentication profiles",
    )
    area: Optional[List[OspfArea]] = Field(None, description="OSPF areas")
    export_rules: Optional[List[OspfExportRule]] = Field(
        None,
        description="Export rules",
    )
    graceful_restart: Optional[OspfGracefulRestart] = Field(
        None,
        description="Graceful restart configuration",
    )


# --- ECMP Models ---


class EcmpIpHash(BaseModel):
    """ECMP IP hash algorithm configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    src_only: Optional[bool] = Field(None, description="Hash source only")
    use_port: Optional[bool] = Field(None, description="Include port in hash")
    hash_seed: Optional[int] = Field(None, description="Hash seed value")


class EcmpWeightedInterface(BaseModel):
    """ECMP weighted round-robin interface entry."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(..., description="Interface name")
    weight: Optional[int] = Field(None, description="Interface weight")


class EcmpWeightedRoundRobin(BaseModel):
    """ECMP weighted round-robin configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    interface: Optional[List[EcmpWeightedInterface]] = Field(
        None,
        description="Weighted interfaces",
    )


class EcmpAlgorithm(BaseModel):
    """ECMP algorithm selection (oneOf)."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    ip_modulo: Optional[Dict[str, Any]] = Field(None, description="IP modulo algorithm")
    ip_hash: Optional[EcmpIpHash] = Field(None, description="IP hash algorithm")
    weighted_round_robin: Optional[EcmpWeightedRoundRobin] = Field(
        None,
        description="Weighted round-robin algorithm",
    )
    balanced_round_robin: Optional[Dict[str, Any]] = Field(
        None,
        description="Balanced round-robin algorithm",
    )

    @model_validator(mode="after")
    def validate_algorithm(self) -> "EcmpAlgorithm":
        """Enforce at most one algorithm is set."""
        fields = [
            self.ip_modulo,
            self.ip_hash,
            self.weighted_round_robin,
            self.balanced_round_robin,
        ]
        provided = [f for f in fields if f is not None]
        if len(provided) > 1:
            raise ValueError(
                "At most one ECMP algorithm can be set: "
                "ip_modulo, ip_hash, weighted_round_robin, or balanced_round_robin."
            )
        return self


class EcmpConfig(BaseModel):
    """ECMP configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    enable: Optional[bool] = Field(None, description="Enable ECMP")
    algorithm: Optional[EcmpAlgorithm] = Field(None, description="ECMP algorithm")
    max_path: Optional[int] = Field(None, description="Maximum number of ECMP paths")
    symmetric_return: Optional[bool] = Field(None, description="Enable symmetric return")
    strict_source_path: Optional[bool] = Field(None, description="Enable strict source path")


# --- RIP Models ---


class RipDistributeList(BaseModel):
    """RIP distribute list configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    access_list: Optional[str] = Field(None, description="Access list name")
    metric: Optional[int] = Field(None, description="Metric value")


class RipInterface(BaseModel):
    """RIP interface configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(..., description="Interface name")
    enable: Optional[bool] = Field(None, description="Enable RIP on interface")
    mode: Optional[str] = Field(
        None,
        description="RIP mode (active, passive, or send-only)",
        pattern=r"^(active|passive|send-only)$",
    )
    split_horizon: Optional[str] = Field(
        None,
        description="Split horizon mode",
        pattern=r"^(split-horizon|no-split-horizon|no-split-horizon-with-poison-reverse)$",
    )
    authentication: Optional[str] = Field(None, description="Authentication profile name")
    bfd: Optional[BfdProfile] = Field(None, description="BFD profile")
    interface_inbound_distribute_list: Optional[RipDistributeList] = Field(
        None,
        description="Inbound distribute list",
    )
    interface_outbound_distribute_list: Optional[RipDistributeList] = Field(
        None,
        description="Outbound distribute list",
    )


class RipConfig(BaseModel):
    """RIP routing protocol configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    enable: Optional[bool] = Field(None, description="Enable RIP")
    default_information_originate: Optional[bool] = Field(
        None,
        description="Originate default information",
    )
    global_timer: Optional[str] = Field(None, description="Global timer profile")
    auth_profile: Optional[str] = Field(None, description="Authentication profile name")
    redistribution_profile: Optional[str] = Field(
        None,
        description="Redistribution profile name",
    )
    global_bfd: Optional[BfdProfile] = Field(None, description="Global BFD profile")
    global_inbound_distribute_list: Optional[RipDistributeList] = Field(
        None,
        description="Global inbound distribute list",
    )
    global_outbound_distribute_list: Optional[RipDistributeList] = Field(
        None,
        description="Global outbound distribute list",
    )
    interface: Optional[List[RipInterface]] = Field(
        None,
        description="RIP interfaces",
    )


# --- BGP Models ---


class BgpMed(BaseModel):
    """BGP MED configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    always_compare_med: Optional[bool] = Field(None, description="Always compare MED")
    deterministic_med_comparison: Optional[bool] = Field(
        None,
        description="Deterministic MED comparison",
    )


class BgpAggregate(BaseModel):
    """BGP aggregate configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    aggregate_med: Optional[bool] = Field(None, description="Aggregate MED")


class BgpGracefulRestart(BaseModel):
    """BGP graceful restart configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    enable: Optional[bool] = Field(None, description="Enable graceful restart")
    stale_route_time: Optional[int] = Field(None, description="Stale route time")
    max_peer_restart_time: Optional[int] = Field(None, description="Max peer restart time")
    local_restart_time: Optional[int] = Field(None, description="Local restart time")


class BgpPeerAddress(BaseModel):
    """BGP peer address (oneOf: ip or fqdn)."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    ip: Optional[str] = Field(None, description="Peer IP address")
    fqdn: Optional[str] = Field(None, description="Peer FQDN")

    @model_validator(mode="after")
    def validate_peer_address(self) -> "BgpPeerAddress":
        """Enforce ip and fqdn are mutually exclusive."""
        if self.ip is not None and self.fqdn is not None:
            raise ValueError("'ip' and 'fqdn' are mutually exclusive.")
        return self


class BgpPeerLocalAddress(BaseModel):
    """BGP peer local address configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    interface: Optional[str] = Field(None, description="Local interface")
    ip: Optional[str] = Field(None, description="Local IP address")


class BgpPeerSubsequentAfi(BaseModel):
    """BGP peer subsequent address family identifier."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    unicast: Optional[bool] = Field(None, description="Enable unicast SAFI")
    multicast: Optional[bool] = Field(None, description="Enable multicast SAFI")


class BgpPeerIncomingBgpConnection(BaseModel):
    """BGP peer incoming connection settings."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    remote_port: Optional[int] = Field(None, description="Remote port")
    allow: Optional[bool] = Field(None, description="Allow incoming connections")


class BgpPeerOutgoingBgpConnection(BaseModel):
    """BGP peer outgoing connection settings."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    local_port: Optional[int] = Field(None, description="Local port")
    allow: Optional[bool] = Field(None, description="Allow outgoing connections")


class BgpPeerConnectionOptions(BaseModel):
    """BGP peer connection options."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    keep_alive_interval: Optional[str] = Field(None, description="Keep-alive interval")
    hold_time: Optional[str] = Field(None, description="Hold time")
    idle_hold_time: Optional[int] = Field(None, description="Idle hold time")
    min_route_adv_interval: Optional[int] = Field(
        None,
        description="Minimum route advertisement interval",
    )
    multihop: Optional[str] = Field(None, description="Multihop TTL")
    open_delay_time: Optional[int] = Field(None, description="Open delay time")
    incoming_bgp_connection: Optional[BgpPeerIncomingBgpConnection] = Field(
        None,
        description="Incoming BGP connection settings",
    )
    outgoing_bgp_connection: Optional[BgpPeerOutgoingBgpConnection] = Field(
        None,
        description="Outgoing BGP connection settings",
    )
    timers: Optional[str] = Field(None, description="Timer profile")
    authentication: Optional[str] = Field(None, description="Authentication profile")
    dampening: Optional[str] = Field(None, description="Dampening profile")


class BgpPeerBfd(BaseModel):
    """BGP peer BFD configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    profile: Optional[str] = Field(None, description="BFD profile name")
    multihop: Optional[Dict[str, Any]] = Field(None, description="Multihop BFD settings")


class BgpPeerInherit(BaseModel):
    """BGP peer inherit configuration (oneOf: ipv4 or no)."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    ipv4: Optional[Dict[str, Any]] = Field(None, description="IPv4 inherit settings")
    no: Optional[Dict[str, Any]] = Field(None, description="No inherit settings")

    @model_validator(mode="after")
    def validate_inherit(self) -> "BgpPeerInherit":
        """Enforce ipv4 and no are mutually exclusive."""
        if self.ipv4 is not None and self.no is not None:
            raise ValueError("'ipv4' and 'no' are mutually exclusive.")
        return self


class BgpPeer(BaseModel):
    """BGP peer configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(..., description="Peer name")
    enable: Optional[bool] = Field(None, description="Enable peer")
    passive: Optional[bool] = Field(None, description="Passive mode")
    peer_as: Optional[str] = Field(None, description="Peer AS number")
    peering_type: Optional[str] = Field(None, description="Peering type")
    reflector_client: Optional[str] = Field(None, description="Route reflector client")
    subsequent_address_family_identifier: Optional[BgpPeerSubsequentAfi] = Field(
        None,
        description="Subsequent AFI configuration",
    )
    enable_sender_side_loop_detection: Optional[bool] = Field(
        None,
        description="Enable sender-side loop detection",
    )
    enable_mp_bgp: Optional[bool] = Field(None, description="Enable MP-BGP")
    max_prefixes: Optional[str] = Field(None, description="Maximum prefixes")
    inherit: Optional[BgpPeerInherit] = Field(None, description="Inherit configuration")
    local_address: Optional[BgpPeerLocalAddress] = Field(
        None,
        description="Local address configuration",
    )
    peer_address: Optional[BgpPeerAddress] = Field(
        None,
        description="Peer address configuration",
    )
    connection_options: Optional[BgpPeerConnectionOptions] = Field(
        None,
        description="Connection options",
    )
    bfd: Optional[BgpPeerBfd] = Field(None, description="BFD configuration")


class BgpPeerGroupType(BaseModel):
    """BGP peer group type (oneOf: ibgp, ebgp_confed, ibgp_confed, ebgp)."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    ibgp: Optional[Dict[str, Any]] = Field(None, description="iBGP type")
    ebgp_confed: Optional[Dict[str, Any]] = Field(None, description="eBGP confederation type")
    ibgp_confed: Optional[Dict[str, Any]] = Field(None, description="iBGP confederation type")
    ebgp: Optional[Dict[str, Any]] = Field(None, description="eBGP type")

    @model_validator(mode="after")
    def validate_type(self) -> "BgpPeerGroupType":
        """Enforce at most one peer group type is set."""
        fields = [self.ibgp, self.ebgp_confed, self.ibgp_confed, self.ebgp]
        provided = [f for f in fields if f is not None]
        if len(provided) > 1:
            raise ValueError(
                "At most one peer group type can be set: ibgp, ebgp_confed, ibgp_confed, or ebgp."
            )
        return self


class BgpPeerGroupConnectionOptions(BaseModel):
    """BGP peer group connection options."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    timers: Optional[str] = Field(None, description="Timer profile")
    multihop: Optional[int] = Field(None, description="Multihop TTL")
    authentication: Optional[str] = Field(None, description="Authentication profile")
    dampening: Optional[str] = Field(None, description="Dampening profile")


class BgpPeerGroupAddressFamily(BaseModel):
    """BGP peer group address family configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    ipv4: Optional[str] = Field(None, description="IPv4 address family profile")
    ipv6: Optional[str] = Field(None, description="IPv6 address family profile")


class BgpPeerGroupFilteringProfile(BaseModel):
    """BGP peer group filtering profile configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    ipv4: Optional[str] = Field(None, description="IPv4 filtering profile")
    ipv6: Optional[str] = Field(None, description="IPv6 filtering profile")


class BgpPeerGroup(BaseModel):
    """BGP peer group configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(..., description="Peer group name")
    enable: Optional[bool] = Field(None, description="Enable peer group")
    aggregated_confed_as_path: Optional[bool] = Field(
        None,
        description="Aggregated confederation AS path",
    )
    soft_reset_with_stored_info: Optional[bool] = Field(
        None,
        description="Soft reset with stored info",
    )
    type: Optional[BgpPeerGroupType] = Field(None, description="Peer group type")
    address_family: Optional[BgpPeerGroupAddressFamily] = Field(
        None,
        description="Address family configuration",
    )
    filtering_profile: Optional[BgpPeerGroupFilteringProfile] = Field(
        None,
        description="Filtering profile configuration",
    )
    connection_options: Optional[BgpPeerGroupConnectionOptions] = Field(
        None,
        description="Connection options",
    )
    peer: Optional[List[BgpPeer]] = Field(None, description="Peers in this group")


class BgpAggregateRouteType(BaseModel):
    """BGP aggregate route type (oneOf: ipv4 or ipv6)."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    ipv4: Optional[Dict[str, Any]] = Field(None, description="IPv4 aggregate route type")
    ipv6: Optional[Dict[str, Any]] = Field(None, description="IPv6 aggregate route type")

    @model_validator(mode="after")
    def validate_type(self) -> "BgpAggregateRouteType":
        """Enforce ipv4 and ipv6 are mutually exclusive."""
        if self.ipv4 is not None and self.ipv6 is not None:
            raise ValueError("'ipv4' and 'ipv6' are mutually exclusive.")
        return self


class BgpAggregateRoute(BaseModel):
    """BGP aggregate route configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(..., description="Aggregate route name")
    description: Optional[str] = Field(None, description="Description")
    enable: Optional[bool] = Field(None, description="Enable aggregate route")
    summary_only: Optional[bool] = Field(None, description="Summary only")
    as_set: Optional[bool] = Field(None, description="Generate AS set")
    same_med: Optional[bool] = Field(None, description="Same MED")
    type: Optional[BgpAggregateRouteType] = Field(None, description="Aggregate route type")


class BgpRedistProfile(BaseModel):
    """BGP redistribution profile configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    ipv4: Optional[Dict[str, Any]] = Field(None, description="IPv4 redistribution profile")
    ipv6: Optional[Dict[str, Any]] = Field(None, description="IPv6 redistribution profile")


class BgpAdvertiseNetworkEntry(BaseModel):
    """BGP advertise network entry."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(..., description="Network address")


class BgpAdvertiseNetworkFamily(BaseModel):
    """BGP advertise network family configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    network: Optional[List[BgpAdvertiseNetworkEntry]] = Field(
        None,
        description="Networks to advertise",
    )


class BgpAdvertiseNetwork(BaseModel):
    """BGP advertise network configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    ipv4: Optional[BgpAdvertiseNetworkFamily] = Field(
        None,
        description="IPv4 advertise networks",
    )
    ipv6: Optional[BgpAdvertiseNetworkFamily] = Field(
        None,
        description="IPv6 advertise networks",
    )


class BgpRedistRule(BaseModel):
    """BGP redistribution rule configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(..., description="Redistribution rule name")
    address_family_identifier: Optional[str] = Field(
        None,
        description="Address family identifier (ipv4 or ipv6)",
        pattern=r"^(ipv4|ipv6)$",
    )
    route_table: Optional[str] = Field(
        None,
        description="Route table (unicast, multicast, or both)",
        pattern=r"^(unicast|multicast|both)$",
    )
    enable: Optional[bool] = Field(None, description="Enable redistribution rule")
    set_origin: Optional[str] = Field(
        None,
        description="Set origin (igp, egp, or incomplete)",
        pattern=r"^(igp|egp|incomplete)$",
    )
    set_med: Optional[int] = Field(None, description="Set MED value")
    set_local_preference: Optional[int] = Field(None, description="Set local preference")
    set_as_path_limit: Optional[int] = Field(None, description="Set AS path limit")
    set_community: Optional[List[str]] = Field(None, description="Set community values")
    set_extended_community: Optional[List[str]] = Field(
        None,
        description="Set extended community values",
    )
    metric: Optional[int] = Field(None, description="Metric value")


class BgpPolicyMatchAddressPrefix(BaseModel):
    """BGP policy match address prefix entry."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(..., description="Address prefix")
    exact: Optional[bool] = Field(None, description="Exact match")


class BgpPolicyMatchAsPath(BaseModel):
    """BGP policy match AS path configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    regex: Optional[str] = Field(None, description="AS path regex")


class BgpPolicyMatchCommunity(BaseModel):
    """BGP policy match community configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    regex: Optional[str] = Field(None, description="Community regex")


class BgpPolicyMatch(BaseModel):
    """BGP policy match criteria."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    afi: Optional[str] = Field(
        None,
        description="Address family identifier (ip or ipv6)",
        pattern=r"^(ip|ipv6)$",
    )
    safi: Optional[str] = Field(
        None,
        description="Subsequent address family identifier (ip or ipv6)",
        pattern=r"^(ip|ipv6)$",
    )
    route_table: Optional[str] = Field(
        None,
        description="Route table (unicast, multicast, or both)",
        pattern=r"^(unicast|multicast|both)$",
    )
    address_prefix: Optional[List[BgpPolicyMatchAddressPrefix]] = Field(
        None,
        description="Address prefix match entries",
    )
    nexthop: Optional[List[str]] = Field(None, description="Nexthop addresses to match")
    from_peer: Optional[List[str]] = Field(None, description="Peers to match")
    med: Optional[int] = Field(None, description="MED value to match")
    as_path: Optional[BgpPolicyMatchAsPath] = Field(None, description="AS path match")
    community: Optional[BgpPolicyMatchCommunity] = Field(
        None,
        description="Community match",
    )
    extended_community: Optional[BgpPolicyMatchCommunity] = Field(
        None,
        description="Extended community match",
    )


class BgpPolicyUpdateAsPath(BaseModel):
    """BGP policy update AS path action (oneOf)."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    none: Optional[Dict[str, Any]] = Field(None, description="No AS path modification")
    remove: Optional[Dict[str, Any]] = Field(None, description="Remove AS path")
    prepend: Optional[int] = Field(None, description="Prepend AS path count")
    remove_and_prepend: Optional[int] = Field(
        None,
        description="Remove and prepend AS path count",
    )

    @model_validator(mode="after")
    def validate_as_path_action(self) -> "BgpPolicyUpdateAsPath":
        """Enforce at most one AS path action is set."""
        fields = [self.none, self.remove, self.prepend, self.remove_and_prepend]
        provided = [f for f in fields if f is not None]
        if len(provided) > 1:
            raise ValueError(
                "At most one AS path action can be set: "
                "none, remove, prepend, or remove_and_prepend."
            )
        return self


class BgpPolicyUpdateCommunity(BaseModel):
    """BGP policy update community action (oneOf). Used for both community and extended_community."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    none: Optional[Dict[str, Any]] = Field(None, description="No community modification")
    remove_all: Optional[Dict[str, Any]] = Field(None, description="Remove all communities")
    remove_regex: Optional[str] = Field(None, description="Remove communities matching regex")
    append: Optional[List[str]] = Field(None, description="Append community values")
    overwrite: Optional[List[str]] = Field(None, description="Overwrite community values")

    @model_validator(mode="after")
    def validate_community_action(self) -> "BgpPolicyUpdateCommunity":
        """Enforce at most one community action is set."""
        fields = [self.none, self.remove_all, self.remove_regex, self.append, self.overwrite]
        provided = [f for f in fields if f is not None]
        if len(provided) > 1:
            raise ValueError(
                "At most one community action can be set: "
                "none, remove_all, remove_regex, append, or overwrite."
            )
        return self


class BgpPolicyUpdate(BaseModel):
    """BGP policy update actions."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    local_preference: Optional[int] = Field(None, description="Set local preference")
    med: Optional[int] = Field(None, description="Set MED")
    weight: Optional[int] = Field(None, description="Set weight")
    nexthop: Optional[str] = Field(None, description="Set nexthop")
    origin: Optional[str] = Field(
        None,
        description="Set origin (igp, egp, or incomplete)",
        pattern=r"^(igp|egp|incomplete)$",
    )
    as_path_limit: Optional[int] = Field(None, description="Set AS path limit")
    as_path: Optional[BgpPolicyUpdateAsPath] = Field(None, description="AS path action")
    community: Optional[BgpPolicyUpdateCommunity] = Field(
        None,
        description="Community action",
    )
    extended_community: Optional[BgpPolicyUpdateCommunity] = Field(
        None,
        description="Extended community action",
    )
    dampening: Optional[str] = Field(None, description="Dampening profile")


class BgpPolicyActionAllow(BaseModel):
    """BGP policy allow action with optional update."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    update: Optional[BgpPolicyUpdate] = Field(None, description="Update actions for allow")


class BgpPolicyAction(BaseModel):
    """BGP policy action (oneOf: deny or allow)."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    deny: Optional[Dict[str, Any]] = Field(None, description="Deny action")
    allow: Optional[BgpPolicyActionAllow] = Field(None, description="Allow action")

    @model_validator(mode="after")
    def validate_action(self) -> "BgpPolicyAction":
        """Enforce deny and allow are mutually exclusive."""
        if self.deny is not None and self.allow is not None:
            raise ValueError("'deny' and 'allow' are mutually exclusive.")
        return self


class BgpPolicyRule(BaseModel):
    """BGP policy rule configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(..., description="Rule name")
    enable: Optional[bool] = Field(None, description="Enable rule")
    used_by: Optional[List[str]] = Field(None, description="Used by peer groups")
    match: Optional[BgpPolicyMatch] = Field(None, description="Match criteria")
    action: Optional[BgpPolicyAction] = Field(None, description="Rule action")


class BgpPolicyImportExport(BaseModel):
    """BGP policy import or export rule container."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    rules: Optional[List[BgpPolicyRule]] = Field(None, description="Policy rules")


class BgpPolicy(BaseModel):
    """BGP policy configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    import_: Optional[BgpPolicyImportExport] = Field(
        None,
        alias="import",
        description="Import policy rules",
    )
    export: Optional[BgpPolicyImportExport] = Field(
        None,
        description="Export policy rules",
    )
    conditional_advertisement: Optional[Dict[str, Any]] = Field(
        None,
        description="Conditional advertisement configuration",
    )
    aggregation: Optional[Dict[str, Any]] = Field(
        None,
        description="Aggregation policy configuration",
    )


class BgpConfig(BaseModel):
    """BGP routing protocol configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    enable: Optional[bool] = Field(None, description="Enable BGP")
    router_id: Optional[str] = Field(None, description="BGP router ID")
    local_as: Optional[str] = Field(None, description="Local AS number")
    confederation_member_as: Optional[str] = Field(
        None,
        description="Confederation member AS",
    )
    install_route: Optional[bool] = Field(None, description="Install routes")
    enforce_first_as: Optional[bool] = Field(None, description="Enforce first AS")
    fast_external_failover: Optional[bool] = Field(
        None,
        description="Fast external failover",
    )
    ecmp_multi_as: Optional[bool] = Field(None, description="ECMP multi-AS")
    default_local_preference: Optional[int] = Field(
        None,
        description="Default local preference",
    )
    graceful_shutdown: Optional[bool] = Field(None, description="Graceful shutdown")
    always_advertise_network_route: Optional[bool] = Field(
        None,
        description="Always advertise network route",
    )
    reject_default_route: Optional[bool] = Field(
        None,
        description="Reject default route",
    )
    allow_redist_default_route: Optional[bool] = Field(
        None,
        description="Allow redistribution of default route",
    )
    as_format: Optional[str] = Field(None, description="AS number format")
    med: Optional[BgpMed] = Field(None, description="MED configuration")
    aggregate: Optional[BgpAggregate] = Field(None, description="Aggregate configuration")
    graceful_restart: Optional[BgpGracefulRestart] = Field(
        None,
        description="Graceful restart configuration",
    )
    global_bfd: Optional[BfdProfile] = Field(None, description="Global BFD profile")
    peer_group: Optional[List[BgpPeerGroup]] = Field(None, description="Peer groups")
    aggregate_routes: Optional[List[BgpAggregateRoute]] = Field(
        None,
        description="Aggregate routes",
    )
    redistribution_profile: Optional[BgpRedistProfile] = Field(
        None,
        description="Redistribution profile",
    )
    advertise_network: Optional[BgpAdvertiseNetwork] = Field(
        None,
        description="Advertise network configuration",
    )
    policy: Optional[BgpPolicy] = Field(None, description="BGP policy configuration")
    redist_rules: Optional[List[BgpRedistRule]] = Field(
        None,
        description="Redistribution rules",
    )


# --- VRF Model ---


class VrfConfig(BaseModel):
    """VRF (Virtual Routing and Forwarding) configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(..., description="VRF name")
    interface: Optional[List[str]] = Field(None, description="Interfaces in this VRF")
    global_vrid: Optional[int] = Field(None, description="Global VRID")
    zone_name: Optional[str] = Field(None, description="Zone name")
    sdwan_type: Optional[str] = Field(None, description="SD-WAN type")
    admin_dists: Optional[AdminDists] = Field(
        None,
        description="Administrative distances",
    )
    vr_admin_dists: Optional[VrAdminDists] = Field(
        None,
        description="VR administrative distances",
    )
    rib_filter: Optional[RibFilter] = Field(None, description="RIB filter configuration")
    routing_table: Optional[RoutingTable] = Field(
        None,
        description="Routing table configuration",
    )
    ospf: Optional[OspfConfig] = Field(None, description="OSPF configuration")
    ospfv3: Optional[Dict[str, Any]] = Field(None, description="OSPFv3 configuration")
    ecmp: Optional[EcmpConfig] = Field(None, description="ECMP configuration")
    multicast: Optional[Dict[str, Any]] = Field(None, description="Multicast configuration")
    rip: Optional[RipConfig] = Field(None, description="RIP configuration")
    bgp: Optional[BgpConfig] = Field(None, description="BGP configuration")


# --- Logical Router Top-Level Models ---


class RoutingStackEnum(str, Enum):
    """Routing stack type for logical routers."""

    LEGACY = "legacy"
    ADVANCED = "advanced"


class LogicalRouterBaseModel(BaseModel):
    """Base model for Logical Routers containing fields common to all operations."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    name: str = Field(..., description="The name of the logical router")
    routing_stack: Optional[RoutingStackEnum] = Field(
        None,
        description="Routing stack type (legacy or advanced)",
    )
    vrf: Optional[List[VrfConfig]] = Field(None, description="VRF configurations")

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


class LogicalRouterCreateModel(LogicalRouterBaseModel):
    """Model for creating new Logical Routers."""

    @model_validator(mode="after")
    def validate_container_type(self) -> "LogicalRouterCreateModel":
        """Ensure exactly one container field (folder, snippet, or device) is set.

        Returns:
            LogicalRouterCreateModel: The validated model instance.

        Raises:
            ValueError: If zero or more than one container field is set.

        """
        container_fields = ["folder", "snippet", "device"]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


class LogicalRouterUpdateModel(LogicalRouterBaseModel):
    """Model for updating existing Logical Routers."""

    id: UUID = Field(
        ...,
        description="The UUID of the logical router",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class LogicalRouterResponseModel(LogicalRouterBaseModel):
    """Model for Logical Router responses."""

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    id: UUID = Field(
        ...,
        description="The UUID of the logical router",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
