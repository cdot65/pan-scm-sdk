"""Live API tests for Deployment models.

These tests validate that Pydantic models correctly parse real API responses.
They are excluded from CI and only run locally with valid credentials.

Run with: pytest -m api tests/scm/api/test_deployment_api.py -v
"""

import pytest

from scm.exceptions import ObjectNotPresentError
from scm.models.deployment import (
    BandwidthAllocationResponseModel,
    BGPRoutingResponseModel,
    InternalDnsServersResponseModel,
    NetworkLocationModel,
    RemoteNetworkResponseModel,
    ServiceConnectionResponseModel,
)


@pytest.mark.api
class TestBandwidthAllocationAPI:
    """Live API tests for BandwidthAllocation objects."""

    def test_list_bandwidth_allocations(self, live_client, deployment_folder):
        """Verify BandwidthAllocation list responses parse correctly."""
        allocations = live_client.bandwidth_allocation.list(folder=deployment_folder, limit=10)
        assert isinstance(allocations, list)
        for allocation in allocations:
            assert isinstance(allocation, BandwidthAllocationResponseModel)
            assert allocation.id is not None
            assert allocation.name is not None


@pytest.mark.api
class TestBGPRoutingAPI:
    """Live API tests for BGPRouting objects."""

    def test_list_bgp_routing(self, live_client, deployment_folder):
        """Verify BGPRouting list responses parse correctly."""
        routes = live_client.bgp_routing.list(folder=deployment_folder, limit=10)
        assert isinstance(routes, list)
        for route in routes:
            assert isinstance(route, BGPRoutingResponseModel)
            assert route.id is not None


@pytest.mark.api
class TestInternalDnsServersAPI:
    """Live API tests for InternalDnsServers objects."""

    def test_list_internal_dns_servers(self, live_client, deployment_folder):
        """Verify InternalDnsServers list responses parse correctly."""
        servers = live_client.internal_dns_server.list(folder=deployment_folder, limit=10)
        assert isinstance(servers, list)
        for server in servers:
            assert isinstance(server, InternalDnsServersResponseModel)
            assert server.id is not None
            assert server.name is not None


@pytest.mark.api
class TestNetworkLocationsAPI:
    """Live API tests for NetworkLocations objects."""

    def test_list_network_locations(self, live_client):
        """Verify NetworkLocations list responses parse correctly."""
        locations = live_client.network_location.list(limit=10)
        assert isinstance(locations, list)
        for location in locations:
            assert isinstance(location, NetworkLocationModel)
            assert location.value is not None


@pytest.mark.api
class TestRemoteNetworksAPI:
    """Live API tests for RemoteNetworks objects."""

    def test_list_remote_networks(self, live_client, deployment_folder):
        """Verify RemoteNetworks list responses parse correctly."""
        try:
            networks = live_client.remote_network.list(folder=deployment_folder, limit=10)
        except ObjectNotPresentError:
            pytest.skip(f"No remote networks in folder '{deployment_folder}'")
        assert isinstance(networks, list)
        for network in networks:
            assert isinstance(network, RemoteNetworkResponseModel)
            assert network.id is not None
            assert network.name is not None


@pytest.mark.api
class TestServiceConnectionAPI:
    """Live API tests for ServiceConnection objects."""

    def test_list_service_connections(self, live_client, service_connections_folder):
        """Verify ServiceConnection list responses parse correctly."""
        connections = live_client.service_connection.list(folder=service_connections_folder, limit=10)
        assert isinstance(connections, list)
        for connection in connections:
            assert isinstance(connection, ServiceConnectionResponseModel)
            assert connection.id is not None
            assert connection.name is not None
