"""Shared models for network interfaces in Palo Alto Networks' Strata Cloud Manager.

This module provides common Pydantic models that are reused across multiple
network interface types including DHCP, ARP, IPv6, LACP, and DDNS configurations.
"""

from enum import Enum
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


# =============================================================================
# Enums
# =============================================================================


class LinkSpeed(str, Enum):
    """Link speed options for ethernet interfaces."""

    AUTO = "auto"
    TEN = "10"
    HUNDRED = "100"
    THOUSAND = "1000"
    TEN_THOUSAND = "10000"
    FORTY_THOUSAND = "40000"
    HUNDRED_THOUSAND = "100000"


class LinkDuplex(str, Enum):
    """Link duplex options for ethernet interfaces."""

    AUTO = "auto"
    HALF = "half"
    FULL = "full"


class LinkState(str, Enum):
    """Link state options for ethernet interfaces."""

    AUTO = "auto"
    UP = "up"
    DOWN = "down"


class PppoeAuthentication(str, Enum):
    """PPPoE authentication methods."""

    CHAP = "CHAP"
    PAP = "PAP"
    AUTO = "auto"


class LacpMode(str, Enum):
    """LACP modes for aggregate interfaces."""

    PASSIVE = "passive"
    ACTIVE = "active"


class LacpTransmissionRate(str, Enum):
    """LACP transmission rate options."""

    FAST = "fast"
    SLOW = "slow"


# =============================================================================
# Static IP Configuration
# =============================================================================


class StaticIpEntry(BaseModel):
    """Static IP address entry for interfaces."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(
        ...,
        description="IP address with optional netmask (e.g., 192.168.1.1/24)",
    )


# =============================================================================
# DHCP Client Configuration
# =============================================================================


class SendHostname(BaseModel):
    """Send hostname configuration for DHCP client."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    enable: Optional[bool] = Field(
        default=True,
        description="Enable sending hostname to DHCP server",
    )
    hostname: Optional[str] = Field(
        default="system-hostname",
        max_length=64,
        pattern=r"^[a-zA-Z0-9._-]+$",
        description="Hostname to send to DHCP server",
    )


class DhcpClient(BaseModel):
    """DHCP client configuration for interfaces."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    enable: Optional[bool] = Field(
        default=True,
        description="Enable DHCP client",
    )
    create_default_route: Optional[bool] = Field(
        default=True,
        description="Create default route from DHCP server",
    )
    default_route_metric: Optional[int] = Field(
        default=10,
        ge=1,
        le=65535,
        description="Metric for the default route",
    )
    send_hostname: Optional[SendHostname] = Field(
        default=None,
        description="Send hostname configuration",
    )


# =============================================================================
# ARP Configuration
# =============================================================================


class ArpEntry(BaseModel):
    """ARP entry for static ARP configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(
        ...,
        description="IP address for the ARP entry",
    )
    hw_address: Optional[str] = Field(
        default=None,
        description="MAC address (hardware address)",
    )


class ArpEntryWithInterface(BaseModel):
    """ARP entry with interface specification (for VLAN interfaces)."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(
        ...,
        description="IP address for the ARP entry",
    )
    hw_address: Optional[str] = Field(
        default=None,
        description="MAC address (hardware address)",
    )
    interface: Optional[str] = Field(
        default=None,
        description="ARP interface",
    )


# =============================================================================
# IPv6 Configuration
# =============================================================================


class Ipv6Address(BaseModel):
    """IPv6 address configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(
        ...,
        description="IPv6 address (e.g., 2001:DB8::1/128)",
    )
    enable_on_interface: Optional[bool] = Field(
        default=True,
        description="Enable address on interface",
    )


class Ipv6Config(BaseModel):
    """IPv6 configuration for interfaces."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    enabled: Optional[bool] = Field(
        default=False,
        description="Enable IPv6 on the interface",
    )
    address: Optional[List[Ipv6Address]] = Field(
        default=None,
        description="List of IPv6 addresses",
    )


# =============================================================================
# DDNS Configuration
# =============================================================================


class DdnsConfig(BaseModel):
    """Dynamic DNS (DDNS) configuration for interfaces."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    ddns_enabled: Optional[bool] = Field(
        default=False,
        description="Enable dynamic DNS",
    )
    ddns_vendor: Optional[str] = Field(
        default=None,
        max_length=127,
        description="DDNS vendor name",
    )
    ddns_update_interval: Optional[int] = Field(
        default=1,
        ge=1,
        le=30,
        description="DDNS update interval in hours",
    )
    ddns_cert_profile: Optional[str] = Field(
        default=None,
        description="Certificate profile for DDNS",
    )
    ddns_hostname: Optional[str] = Field(
        default=None,
        max_length=255,
        pattern=r"^[a-zA-Z0-9_.\-]+$",
        description="Hostname for DDNS registration",
    )
    ddns_ip: Optional[str] = Field(
        default=None,
        description="IP address to register (for static IP only)",
    )
    ddns_vendor_config: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Vendor-specific configuration",
    )


# =============================================================================
# LACP Configuration
# =============================================================================


class LacpConfig(BaseModel):
    """LACP configuration for aggregate interfaces."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    enable: Optional[bool] = Field(
        default=False,
        description="Enable LACP",
    )
    fast_failover: Optional[bool] = Field(
        default=False,
        description="Enable fast failover",
    )
    mode: Optional[Literal["passive", "active"]] = Field(
        default="passive",
        description="LACP mode",
    )
    transmission_rate: Optional[Literal["fast", "slow"]] = Field(
        default="slow",
        description="LACP transmission rate",
    )
    system_priority: Optional[int] = Field(
        default=32768,
        ge=1,
        le=65535,
        description="LACP system priority",
    )
    max_ports: Optional[int] = Field(
        default=8,
        ge=1,
        le=8,
        description="Maximum number of ports",
    )


# =============================================================================
# LLDP Configuration
# =============================================================================


class LldpConfig(BaseModel):
    """LLDP configuration for interfaces."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    enable: Optional[bool] = Field(
        default=False,
        description="Enable LLDP",
    )


# =============================================================================
# PPPoE Configuration
# =============================================================================


class PppoePassive(BaseModel):
    """PPPoE passive mode configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    enable: bool = Field(
        default=False,
        description="Enable passive mode",
    )


class PppoeStaticAddress(BaseModel):
    """Static IP address for PPPoE."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    ip: str = Field(
        ...,
        max_length=63,
        description="Static IP address",
    )


class PppoeConfig(BaseModel):
    """PPPoE configuration for ethernet interfaces."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    enable: Optional[bool] = Field(
        default=True,
        description="Enable PPPoE",
    )
    username: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="PPPoE username",
    )
    password: str = Field(
        ...,
        max_length=255,
        description="PPPoE password",
    )
    authentication: Optional[Literal["CHAP", "PAP", "auto"]] = Field(
        default=None,
        description="Authentication method",
    )
    static_address: Optional[PppoeStaticAddress] = Field(
        default=None,
        description="Static IP address configuration",
    )
    default_route_metric: Optional[int] = Field(
        default=10,
        ge=1,
        le=65535,
        description="Metric for the default route",
    )
    access_concentrator: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Access concentrator name",
    )
    service: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Service name",
    )
    passive: Optional[PppoePassive] = Field(
        default=None,
        description="Passive mode configuration",
    )


# =============================================================================
# PoE Configuration
# =============================================================================


class PoeConfig(BaseModel):
    """Power over Ethernet configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    poe_enabled: Optional[bool] = Field(
        default=False,
        description="Enable Power over Ethernet",
    )
    poe_rsvd_pwr: Optional[int] = Field(
        default=0,
        ge=0,
        le=90,
        description="PoE reserved power in watts",
    )


# =============================================================================
# TCP MSS Adjustment Configuration
# =============================================================================


class AdjustTcpMss(BaseModel):
    """TCP MSS adjustment configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    enable: Optional[bool] = Field(
        default=False,
        description="Enable TCP MSS adjustment",
    )
    ipv4_mss_adjustment: Optional[int] = Field(
        default=None,
        ge=40,
        le=300,
        description="IPv4 MSS adjustment size",
    )
    ipv6_mss_adjustment: Optional[int] = Field(
        default=None,
        ge=60,
        le=300,
        description="IPv6 MSS adjustment size",
    )


# =============================================================================
# Bonjour Configuration
# =============================================================================


class BonjourConfig(BaseModel):
    """Bonjour/mDNS configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    enable: Optional[bool] = Field(
        default=False,
        description="Enable Bonjour",
    )


# =============================================================================
# NDP Proxy Configuration
# =============================================================================


class NdpProxyConfig(BaseModel):
    """NDP (Neighbor Discovery Protocol) proxy configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    enabled: Optional[bool] = Field(
        default=False,
        description="Enable NDP proxy",
    )


# =============================================================================
# Extended IPv6 Configuration (for Ethernet interfaces)
# =============================================================================


class Ipv6NeighborDiscovery(BaseModel):
    """IPv6 Neighbor Discovery configuration."""

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )

    router_advertisement: Optional[dict] = Field(
        default=None,
        description="Router advertisement settings",
    )
    neighbor: Optional[dict] = Field(
        default=None,
        description="Neighbor settings",
    )
    enable_ndp_monitor: Optional[bool] = Field(
        default=False,
        description="Enable NDP monitor",
    )
    enable_dad: Optional[bool] = Field(
        default=True,
        description="Enable duplicate address detection",
    )
    dad_attempts: Optional[int] = Field(
        default=1,
        ge=0,
        le=10,
        description="DAD attempts",
    )
    ns_interval: Optional[int] = Field(
        default=1,
        ge=1,
        le=3600,
        description="NS interval in seconds",
    )
    reachable_time: Optional[int] = Field(
        default=30,
        ge=10,
        le=36000,
        description="Reachable time in seconds",
    )
    enable: Optional[bool] = Field(
        default=False,
        description="Enable neighbor discovery",
    )


class Ipv6ConfigExtended(BaseModel):
    """Extended IPv6 configuration for ethernet interfaces."""

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )

    enabled: Optional[bool] = Field(
        default=False,
        description="Enable IPv6 on the interface",
    )
    interface_id: Optional[str] = Field(
        default=None,
        description="Interface identifier",
    )
    address: Optional[list] = Field(
        default=None,
        description="List of IPv6 addresses",
    )
    neighbor_discovery: Optional[Ipv6NeighborDiscovery] = Field(
        default=None,
        description="Neighbor discovery configuration",
    )
