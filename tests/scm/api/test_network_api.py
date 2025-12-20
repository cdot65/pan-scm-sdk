"""Live API tests for Network models.

These tests validate that Pydantic models correctly parse real API responses.
They are excluded from CI and only run locally with valid credentials.

Run with: pytest -m api tests/scm/api/test_network_api.py -v
"""

import pytest

from scm.models.network import (
    IKECryptoProfileResponseModel,
    IKEGatewayResponseModel,
    IPsecCryptoProfileResponseModel,
    NatRuleResponseModel,
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
