"""Live API tests for Network models.

These tests validate that Pydantic models correctly parse real API responses.
They are excluded from CI and only run locally with valid credentials.

Run with: pytest -m api tests/scm/api/test_network_api.py -v
"""

import pytest

from scm.models.network import (
    BgpAddressFamilyProfileResponseModel,
    BgpAuthProfileResponseModel,
    BgpFilteringProfileResponseModel,
    BgpRedistributionProfileResponseModel,
    BgpRouteMapRedistributionResponseModel,
    BgpRouteMapResponseModel,
    IKECryptoProfileResponseModel,
    IKEGatewayResponseModel,
    IPsecCryptoProfileResponseModel,
    NatRuleResponseModel,
    OspfAuthProfileResponseModel,
    RouteAccessListResponseModel,
    RoutePrefixListResponseModel,
    SecurityZoneResponseModel,
)


@pytest.mark.api
class TestIKECryptoProfileAPI:
    """Live API tests for IKECryptoProfile objects."""

    def test_list_ike_crypto_profiles(self, live_client, folder):
        """Verify IKECryptoProfile list responses parse correctly."""
        profiles = live_client.ike_crypto_profile.list(folder=folder)
        assert isinstance(profiles, list)
        for profile in profiles:
            assert isinstance(profile, IKECryptoProfileResponseModel)
            assert profile.id is not None
            assert profile.name is not None


@pytest.mark.api
class TestIKEGatewayAPI:
    """Live API tests for IKEGateway objects."""

    def test_list_ike_gateways(self, live_client, folder):
        """Verify IKEGateway list responses parse correctly."""
        gateways = live_client.ike_gateway.list(folder=folder)
        assert isinstance(gateways, list)
        for gateway in gateways:
            assert isinstance(gateway, IKEGatewayResponseModel)
            assert gateway.id is not None
            assert gateway.name is not None


@pytest.mark.api
class TestIPsecCryptoProfileAPI:
    """Live API tests for IPsecCryptoProfile objects."""

    def test_list_ipsec_crypto_profiles(self, live_client, folder):
        """Verify IPsecCryptoProfile list responses parse correctly."""
        profiles = live_client.ipsec_crypto_profile.list(folder=folder, limit=10)
        assert isinstance(profiles, list)
        for profile in profiles:
            assert isinstance(profile, IPsecCryptoProfileResponseModel)
            assert profile.id is not None
            assert profile.name is not None


@pytest.mark.api
class TestNatRuleAPI:
    """Live API tests for NatRule objects."""

    def test_list_nat_rules(self, live_client, folder):
        """Verify NatRule list responses parse correctly."""
        rules = live_client.nat_rule.list(folder=folder, limit=10)
        assert isinstance(rules, list)
        for rule in rules:
            assert isinstance(rule, NatRuleResponseModel)
            assert rule.id is not None
            assert rule.name is not None

    def test_nat_rule_has_valid_nat_type(self, live_client, folder):
        """Verify NatRule nat_type field is valid."""
        rules = live_client.nat_rule.list(folder=folder, limit=5)
        valid_types = {"ipv4", "nat64", "nptv6"}
        for rule in rules:
            if rule.nat_type is not None:
                assert rule.nat_type.value in valid_types, f"Invalid nat_type: {rule.nat_type}"


@pytest.mark.api
class TestSecurityZoneAPI:
    """Live API tests for SecurityZone objects."""

    def test_list_security_zones(self, live_client, folder):
        """Verify SecurityZone list responses parse correctly."""
        zones = live_client.security_zone.list(folder=folder, limit=10)
        assert isinstance(zones, list)
        for zone in zones:
            assert isinstance(zone, SecurityZoneResponseModel)
            assert zone.id is not None
            assert zone.name is not None

    def test_security_zone_network_config(self, live_client, folder):
        """Verify SecurityZone network configuration parses correctly."""
        zones = live_client.security_zone.list(folder=folder, limit=5)
        for zone in zones:
            if zone.network is not None:
                # Network config should have at most one interface type set
                interface_types = [
                    zone.network.tap,
                    zone.network.virtual_wire,
                    zone.network.layer2,
                    zone.network.layer3,
                    zone.network.tunnel,
                    zone.network.external,
                ]
                set_types = [t for t in interface_types if t is not None]
                assert len(set_types) <= 1, f"Zone {zone.name} has multiple interface types"


# ---------------------------------------------------------------------------
# v0.8.0 Routing Profile Services (no-POST: list/get/update/fetch only)
# ---------------------------------------------------------------------------


@pytest.mark.api
class TestRouteAccessListAPI:
    """Live API tests for RouteAccessList objects."""

    FOLDER = "ngfw-shared"

    def test_list_route_access_lists(self, live_client):
        """Verify RouteAccessList list responses parse correctly."""
        items = live_client.route_access_list.list(folder=self.FOLDER)
        assert isinstance(items, list)
        for item in items:
            assert isinstance(item, RouteAccessListResponseModel)
            assert item.id is not None
            assert item.name is not None
        print(f"\n  Found {len(items)} route access lists in '{self.FOLDER}'")


@pytest.mark.api
class TestRoutePrefixListAPI:
    """Live API tests for RoutePrefixList objects."""

    FOLDER = "ngfw-shared"

    def test_list_route_prefix_lists(self, live_client):
        """Verify RoutePrefixList list responses parse correctly."""
        items = live_client.route_prefix_list.list(folder=self.FOLDER)
        assert isinstance(items, list)
        for item in items:
            assert isinstance(item, RoutePrefixListResponseModel)
            assert item.id is not None
            assert item.name is not None
        print(f"\n  Found {len(items)} route prefix lists in '{self.FOLDER}'")


@pytest.mark.api
class TestBgpAuthProfileAPI:
    """Live API tests for BgpAuthProfile objects."""

    FOLDER = "ngfw-shared"

    def test_list_bgp_auth_profiles(self, live_client):
        """Verify BgpAuthProfile list responses parse correctly."""
        items = live_client.bgp_auth_profile.list(folder=self.FOLDER)
        assert isinstance(items, list)
        for item in items:
            assert isinstance(item, BgpAuthProfileResponseModel)
            assert item.id is not None
            assert item.name is not None
        print(f"\n  Found {len(items)} BGP auth profiles in '{self.FOLDER}'")


@pytest.mark.api
class TestOspfAuthProfileAPI:
    """Live API tests for OspfAuthProfile objects."""

    FOLDER = "ngfw-shared"

    def test_list_ospf_auth_profiles(self, live_client):
        """Verify OspfAuthProfile list responses parse correctly."""
        items = live_client.ospf_auth_profile.list(folder=self.FOLDER)
        assert isinstance(items, list)
        for item in items:
            assert isinstance(item, OspfAuthProfileResponseModel)
            assert item.id is not None
            assert item.name is not None
        print(f"\n  Found {len(items)} OSPF auth profiles in '{self.FOLDER}'")


@pytest.mark.api
class TestBgpAddressFamilyProfileAPI:
    """Live API tests for BgpAddressFamilyProfile objects."""

    FOLDER = "ngfw-shared"

    def test_list_bgp_address_family_profiles(self, live_client):
        """Verify BgpAddressFamilyProfile list responses parse correctly."""
        items = live_client.bgp_address_family_profile.list(folder=self.FOLDER)
        assert isinstance(items, list)
        for item in items:
            assert isinstance(item, BgpAddressFamilyProfileResponseModel)
            assert item.id is not None
            assert item.name is not None
        print(f"\n  Found {len(items)} BGP address family profiles in '{self.FOLDER}'")


# ---------------------------------------------------------------------------
# v0.9.0 Routing Profile Services
# ---------------------------------------------------------------------------


@pytest.mark.api
class TestBgpFilteringProfileAPI:
    """Live API tests for BgpFilteringProfile objects."""

    FOLDER = "ngfw-shared"

    def test_list_bgp_filtering_profiles(self, live_client):
        """Verify BgpFilteringProfile list responses parse correctly."""
        items = live_client.bgp_filtering_profile.list(folder=self.FOLDER)
        assert isinstance(items, list)
        for item in items:
            assert isinstance(item, BgpFilteringProfileResponseModel)
            assert item.id is not None
            assert item.name is not None
        print(f"\n  Found {len(items)} BGP filtering profiles in '{self.FOLDER}'")


@pytest.mark.api
class TestBgpRedistributionProfileAPI:
    """Live API tests for BgpRedistributionProfile objects."""

    FOLDER = "ngfw-shared"

    def test_list_bgp_redistribution_profiles(self, live_client):
        """Verify BgpRedistributionProfile list responses parse correctly."""
        items = live_client.bgp_redistribution_profile.list(folder=self.FOLDER)
        assert isinstance(items, list)
        for item in items:
            assert isinstance(item, BgpRedistributionProfileResponseModel)
            assert item.id is not None
            assert item.name is not None
        print(f"\n  Found {len(items)} BGP redistribution profiles in '{self.FOLDER}'")


@pytest.mark.api
class TestBgpRouteMapAPI:
    """Live API tests for BgpRouteMap objects."""

    FOLDER = "ngfw-shared"

    def test_list_bgp_route_maps(self, live_client):
        """Verify BgpRouteMap list responses parse correctly."""
        items = live_client.bgp_route_map.list(folder=self.FOLDER)
        assert isinstance(items, list)
        for item in items:
            assert isinstance(item, BgpRouteMapResponseModel)
            assert item.id is not None
            assert item.name is not None
        print(f"\n  Found {len(items)} BGP route maps in '{self.FOLDER}'")


@pytest.mark.api
class TestBgpRouteMapRedistributionAPI:
    """Live API tests for BgpRouteMapRedistribution objects."""

    FOLDER = "ngfw-shared"

    def test_list_bgp_route_map_redistributions(self, live_client):
        """Verify BgpRouteMapRedistribution list responses parse correctly."""
        items = live_client.bgp_route_map_redistribution.list(folder=self.FOLDER)
        assert isinstance(items, list)
        for item in items:
            assert isinstance(item, BgpRouteMapRedistributionResponseModel)
            assert item.id is not None
            assert item.name is not None
        print(f"\n  Found {len(items)} BGP route map redistributions in '{self.FOLDER}'")
