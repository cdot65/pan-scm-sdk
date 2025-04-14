# tests/test_factories/deployment/__init__.py

from tests.test_factories.deployment.bandwidth_allocations import (
    BandwidthAllocationBaseFactory,
    BandwidthAllocationCreateApiFactory,
    BandwidthAllocationCreateModelFactory,
    BandwidthAllocationResponseFactory,
    BandwidthAllocationUpdateApiFactory,
    QosModelFactory,
)
from tests.test_factories.deployment.remote_networks import (
    RemoteNetworkBaseFactory,
    RemoteNetworkCreateApiFactory,
    RemoteNetworkCreateModelFactory,
    RemoteNetworkResponseFactory,
    RemoteNetworkUpdateApiFactory,
    RemoteNetworkUpdateModelFactory,
)

__all__ = [
    # Bandwidth Allocation factories
    "BandwidthAllocationBaseFactory",
    "BandwidthAllocationCreateApiFactory",
    "BandwidthAllocationResponseFactory",
    "BandwidthAllocationUpdateApiFactory",
    "BandwidthAllocationCreateModelFactory",
    "QosModelFactory",
    # Remote Networks factories
    "RemoteNetworkBaseFactory",
    "RemoteNetworkCreateApiFactory",
    "RemoteNetworkResponseFactory",
    "RemoteNetworkUpdateApiFactory",
    "RemoteNetworkCreateModelFactory",
    "RemoteNetworkUpdateModelFactory",
]
