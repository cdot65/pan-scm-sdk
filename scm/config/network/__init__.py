"""scm.config.network: Network-related service classes."""
# scm/config/network/__init__.py

from .aggregate_interface import AggregateInterface
from .dhcp_interface import DhcpInterface
from .ethernet_interface import EthernetInterface
from .ike_crypto_profile import IKECryptoProfile
from .ike_gateway import IKEGateway
from .interface_management_profile import InterfaceManagementProfile
from .ipsec_crypto_profile import IPsecCryptoProfile
from .ipsec_tunnel import IPsecTunnel
from .layer2_subinterface import Layer2Subinterface
from .logical_router import LogicalRouter
from .layer3_subinterface import Layer3Subinterface
from .loopback_interface import LoopbackInterface
from .nat_rules import NatRule
from .security_zone import SecurityZone
from .tunnel_interface import TunnelInterface
from .vlan_interface import VlanInterface
from .zone_protection_profile import ZoneProtectionProfile
from .bgp_address_family_profile import BgpAddressFamilyProfile
from .bgp_auth_profile import BgpAuthProfile
from .ospf_auth_profile import OspfAuthProfile
from .route_access_list import RouteAccessList
from .route_prefix_list import RoutePrefixList
from .bgp_filtering_profile import BgpFilteringProfile
from .bgp_redistribution_profile import BgpRedistributionProfile
from .bgp_route_map import BgpRouteMap
from .bgp_route_map_redistribution import BgpRouteMapRedistribution
from .dns_proxy import DnsProxy
from .pbf_rule import PbfRule
from .qos_profile import QosProfile
from .qos_rule import QosRule

__all__ = [
    # Network Interfaces
    "AggregateInterface",
    "EthernetInterface",
    "Layer2Subinterface",
    "Layer3Subinterface",
    "LoopbackInterface",
    "TunnelInterface",
    "VlanInterface",
    # DHCP
    "DhcpInterface",
    # Other Network Services
    "InterfaceManagementProfile",
    "NatRule",
    "SecurityZone",
    "IKECryptoProfile",
    "IKEGateway",
    "IPsecCryptoProfile",
    "IPsecTunnel",
    "LogicalRouter",
    "ZoneProtectionProfile",
    # Routing Profiles (v0.8.0)
    "BgpAddressFamilyProfile",
    "BgpAuthProfile",
    "OspfAuthProfile",
    "RouteAccessList",
    "RoutePrefixList",
    # Routing Profiles (v0.9.0)
    "BgpFilteringProfile",
    "BgpRedistributionProfile",
    "BgpRouteMap",
    "BgpRouteMapRedistribution",
    # Advanced Networking (v0.10.0)
    "QosProfile",
    "QosRule",
    "DnsProxy",
    "PbfRule",
]
