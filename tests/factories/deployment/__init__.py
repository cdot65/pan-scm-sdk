# tests/factories/deployment/__init__.py

from tests.factories.deployment.bandwidth_allocations import (
    BandwidthAllocationBaseFactory,
    BandwidthAllocationCreateApiFactory,
    BandwidthAllocationCreateModelFactory,
    BandwidthAllocationResponseFactory,
    BandwidthAllocationUpdateApiFactory,
    QosModelFactory,
)
from tests.factories.deployment.bgp_routing import (
    BGPRoutingBaseFactory,
    BGPRoutingCreateApiFactory,
    BGPRoutingCreateModelFactory,
    BGPRoutingResponseFactory,
    BGPRoutingResponseModelFactory,
    BGPRoutingUpdateApiFactory,
    BGPRoutingUpdateModelFactory,
    DefaultRoutingModelFactory,
    HotPotatoRoutingModelFactory,
)
from tests.factories.deployment.internal_dns_servers import (
    InternalDnsServersBaseFactory,
    InternalDnsServersCreateApiFactory,
    InternalDnsServersCreateModelFactory,
    InternalDnsServersResponseFactory,
    InternalDnsServersResponseModelFactory,
    InternalDnsServersUpdateApiFactory,
    InternalDnsServersUpdateModelFactory,
)
from tests.factories.deployment.network_locations import (
    NetworkLocationApiFactory,
    NetworkLocationBaseFactory,
    NetworkLocationModelFactory,
)
from tests.factories.deployment.remote_networks import (
    RemoteNetworkBaseFactory,
    RemoteNetworkCreateApiFactory,
    RemoteNetworkCreateModelFactory,
    RemoteNetworkResponseFactory,
    RemoteNetworkUpdateApiFactory,
    RemoteNetworkUpdateModelFactory,
)
from tests.factories.deployment.service_connections import (
    BgpPeerModelFactory,
    BgpProtocolModelFactory,
    ProtocolModelFactory,
)
from tests.factories.deployment.service_connections import (
    QosModelFactory as ServiceConnectionQosModelFactory,
)
from tests.factories.deployment.service_connections import (
    ServiceConnectionBaseFactory,
    ServiceConnectionCreateApiFactory,
    ServiceConnectionCreateModelFactory,
    ServiceConnectionResponseFactory,
    ServiceConnectionResponseModelFactory,
    ServiceConnectionUpdateApiFactory,
    ServiceConnectionUpdateModelFactory,
)

__all__ = [
    # Bandwidth Allocation factories
    "BandwidthAllocationBaseFactory",
    "BandwidthAllocationCreateApiFactory",
    "BandwidthAllocationResponseFactory",
    "BandwidthAllocationUpdateApiFactory",
    "BandwidthAllocationCreateModelFactory",
    "QosModelFactory",
    # BGP Routing factories
    "BGPRoutingBaseFactory",
    "BGPRoutingCreateApiFactory",
    "BGPRoutingResponseFactory",
    "BGPRoutingUpdateApiFactory",
    "BGPRoutingCreateModelFactory",
    "BGPRoutingUpdateModelFactory",
    "BGPRoutingResponseModelFactory",
    "DefaultRoutingModelFactory",
    "HotPotatoRoutingModelFactory",
    # Internal DNS Servers factories
    "InternalDnsServersBaseFactory",
    "InternalDnsServersCreateApiFactory",
    "InternalDnsServersResponseFactory",
    "InternalDnsServersUpdateApiFactory",
    "InternalDnsServersCreateModelFactory",
    "InternalDnsServersUpdateModelFactory",
    "InternalDnsServersResponseModelFactory",
    # Network Locations factories
    "NetworkLocationApiFactory",
    "NetworkLocationBaseFactory",
    "NetworkLocationModelFactory",
    # Remote Networks factories
    "RemoteNetworkBaseFactory",
    "RemoteNetworkCreateApiFactory",
    "RemoteNetworkResponseFactory",
    "RemoteNetworkUpdateApiFactory",
    "RemoteNetworkCreateModelFactory",
    "RemoteNetworkUpdateModelFactory",
    # Service Connections factories
    "BgpPeerModelFactory",
    "BgpProtocolModelFactory",
    "ProtocolModelFactory",
    "ServiceConnectionQosModelFactory",
    "ServiceConnectionBaseFactory",
    "ServiceConnectionCreateApiFactory",
    "ServiceConnectionCreateModelFactory",
    "ServiceConnectionResponseFactory",
    "ServiceConnectionResponseModelFactory",
    "ServiceConnectionUpdateApiFactory",
    "ServiceConnectionUpdateModelFactory",
]
