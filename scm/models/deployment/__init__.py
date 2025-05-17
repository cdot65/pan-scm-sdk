"""scm.models.deployment: Deployment-related models."""
# scm/models/deployment/__init__.py

from .bandwidth_allocations import (
    BandwidthAllocationCreateModel,
    BandwidthAllocationListResponseModel,
    BandwidthAllocationResponseModel,
    BandwidthAllocationUpdateModel,
)
from .bandwidth_allocations import QosModel as BandwidthQosModel
from .bgp_routing import (
    BackboneRoutingEnum,
    BGPRoutingBaseModel,
    BGPRoutingCreateModel,
    BGPRoutingResponseModel,
    BGPRoutingUpdateModel,
    DefaultRoutingModel,
    HotPotatoRoutingModel,
)
from .internal_dns_servers import (
    InternalDnsServersBaseModel,
    InternalDnsServersCreateModel,
    InternalDnsServersResponseModel,
    InternalDnsServersUpdateModel,
)
from .network_locations import NetworkLocationModel
from .remote_networks import (
    EcmpLoadBalancingEnum,
    RemoteNetworkCreateModel,
    RemoteNetworkResponseModel,
    RemoteNetworkUpdateModel,
)
from .service_connections import (
    BgpPeerModel,
    BgpProtocolModel,
    NoExportCommunity,
    OnboardingType,
    ProtocolModel,
    QosModel,
    ServiceConnectionCreateModel,
    ServiceConnectionResponseModel,
    ServiceConnectionUpdateModel,
)

__all__ = [
    "NetworkLocationModel",
    "RemoteNetworkCreateModel",
    "RemoteNetworkUpdateModel",
    "RemoteNetworkResponseModel",
    "EcmpLoadBalancingEnum",
    "ServiceConnectionCreateModel",
    "ServiceConnectionUpdateModel",
    "ServiceConnectionResponseModel",
    "OnboardingType",
    "NoExportCommunity",
    "BgpPeerModel",
    "BgpProtocolModel",
    "ProtocolModel",
    "QosModel",
    "BandwidthAllocationCreateModel",
    "BandwidthAllocationUpdateModel",
    "BandwidthAllocationResponseModel",
    "BandwidthAllocationListResponseModel",
    "BandwidthQosModel",
    "BGPRoutingBaseModel",
    "BGPRoutingCreateModel",
    "BGPRoutingUpdateModel",
    "BGPRoutingResponseModel",
    "DefaultRoutingModel",
    "HotPotatoRoutingModel",
    "BackboneRoutingEnum",
    "InternalDnsServersBaseModel",
    "InternalDnsServersCreateModel",
    "InternalDnsServersUpdateModel",
    "InternalDnsServersResponseModel",
]
