"""scm.config.deployment: Deployment-related service classes."""
# scm/config/deployment/__init__.py

from .bandwidth_allocations import BandwidthAllocations
from .bgp_routing import BGPRouting
from .internal_dns_servers import InternalDnsServers
from .network_locations import NetworkLocations
from .remote_networks import RemoteNetworks
from .service_connections import ServiceConnection

__all__ = [
    "RemoteNetworks",
    "ServiceConnection",
    "BandwidthAllocations",
    "BGPRouting",
    "InternalDnsServers",
    "NetworkLocations",
]
