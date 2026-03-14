# tests/scm/models/network/test_interface_common_models.py

"""Tests for shared network interface common models."""

from pydantic import ValidationError
import pytest

from scm.models.network._interface_common import (
    AdjustTcpMss,
    ArpEntry,
    ArpEntryWithInterface,
    BonjourConfig,
    DdnsConfig,
    DhcpClient,
    Ipv6Address,
    Ipv6Config,
    Ipv6ConfigExtended,
    Ipv6NeighborDiscovery,
    LacpConfig,
    LacpMode,
    LacpTransmissionRate,
    LinkDuplex,
    LinkSpeed,
    LinkState,
    LldpConfig,
    NdpProxyConfig,
    PoeConfig,
    PppoeAuthentication,
    PppoeConfig,
    PppoePassive,
    PppoeStaticAddress,
    SendHostname,
    StaticIpEntry,
)


class TestEnums:
    """Tests for network interface enums."""

    def test_link_speed_values(self):
        """Verify LinkSpeed enum values match expected strings."""
        assert LinkSpeed.AUTO == "auto"
        assert LinkSpeed.TEN_THOUSAND == "10000"
        assert LinkSpeed.HUNDRED_THOUSAND == "100000"

    def test_link_duplex_values(self):
        """Verify LinkDuplex enum values."""
        assert LinkDuplex.AUTO == "auto"
        assert LinkDuplex.HALF == "half"
        assert LinkDuplex.FULL == "full"

    def test_link_state_values(self):
        """Verify LinkState enum values."""
        assert LinkState.AUTO == "auto"
        assert LinkState.UP == "up"
        assert LinkState.DOWN == "down"

    def test_pppoe_authentication_values(self):
        """Verify PppoeAuthentication enum values."""
        assert PppoeAuthentication.CHAP == "CHAP"
        assert PppoeAuthentication.PAP == "PAP"
        assert PppoeAuthentication.AUTO == "auto"

    def test_lacp_mode_values(self):
        """Verify LacpMode enum values."""
        assert LacpMode.PASSIVE == "passive"
        assert LacpMode.ACTIVE == "active"

    def test_lacp_transmission_rate_values(self):
        """Verify LacpTransmissionRate enum values."""
        assert LacpTransmissionRate.FAST == "fast"
        assert LacpTransmissionRate.SLOW == "slow"


class TestStaticIpEntry:
    """Tests for StaticIpEntry model."""

    def test_valid_entry(self):
        """Verify StaticIpEntry accepts a valid IP/CIDR string."""
        entry = StaticIpEntry(name="192.168.1.1/24")
        assert entry.name == "192.168.1.1/24"

    def test_name_required(self):
        """Verify name field is required."""
        with pytest.raises(ValidationError):
            StaticIpEntry()

    def test_extra_fields_forbidden(self):
        """Verify extra fields are rejected."""
        with pytest.raises(ValidationError):
            StaticIpEntry(name="10.0.0.1", extra_field="bad")


class TestSendHostname:
    """Tests for SendHostname model."""

    def test_defaults(self):
        """Verify default values for SendHostname."""
        sh = SendHostname()
        assert sh.enable is True
        assert sh.hostname == "system-hostname"

    def test_custom_hostname(self):
        """Verify custom hostname is accepted."""
        sh = SendHostname(hostname="my-host")
        assert sh.hostname == "my-host"

    def test_invalid_hostname_pattern(self):
        """Verify invalid hostname pattern is rejected."""
        with pytest.raises(ValidationError):
            SendHostname(hostname="invalid host!")


class TestDhcpClient:
    """Tests for DhcpClient model."""

    def test_defaults(self):
        """Verify default values for DhcpClient."""
        dhcp = DhcpClient()
        assert dhcp.enable is True
        assert dhcp.create_default_route is True
        assert dhcp.default_route_metric == 10
        assert dhcp.send_hostname is None

    def test_metric_bounds(self):
        """Verify default_route_metric enforces valid range."""
        DhcpClient(default_route_metric=1)
        DhcpClient(default_route_metric=65535)
        with pytest.raises(ValidationError):
            DhcpClient(default_route_metric=0)
        with pytest.raises(ValidationError):
            DhcpClient(default_route_metric=65536)

    def test_nested_send_hostname(self):
        """Verify nested SendHostname model works."""
        dhcp = DhcpClient(send_hostname=SendHostname(hostname="test"))
        assert dhcp.send_hostname.hostname == "test"


class TestArpEntry:
    """Tests for ArpEntry model."""

    def test_valid_entry(self):
        """Verify ArpEntry with IP and MAC address."""
        arp = ArpEntry(name="10.0.0.1", hw_address="00:11:22:33:44:55")
        assert arp.name == "10.0.0.1"
        assert arp.hw_address == "00:11:22:33:44:55"

    def test_hw_address_optional(self):
        """Verify hw_address defaults to None."""
        arp = ArpEntry(name="10.0.0.1")
        assert arp.hw_address is None


class TestArpEntryWithInterface:
    """Tests for ArpEntryWithInterface model."""

    def test_with_interface(self):
        """Verify interface field is accepted."""
        arp = ArpEntryWithInterface(name="10.0.0.1", interface="eth0")
        assert arp.interface == "eth0"

    def test_interface_optional(self):
        """Verify interface field defaults to None."""
        arp = ArpEntryWithInterface(name="10.0.0.1")
        assert arp.interface is None


class TestIpv6Models:
    """Tests for IPv6 configuration models."""

    def test_ipv6_address(self):
        """Verify Ipv6Address model fields and defaults."""
        addr = Ipv6Address(name="2001:DB8::1/128")
        assert addr.name == "2001:DB8::1/128"
        assert addr.enable_on_interface is True

    def test_ipv6_config_defaults(self):
        """Verify Ipv6Config default values."""
        cfg = Ipv6Config()
        assert cfg.enabled is False
        assert cfg.address is None

    def test_ipv6_config_with_addresses(self):
        """Verify Ipv6Config with a list of addresses."""
        cfg = Ipv6Config(
            enabled=True,
            address=[Ipv6Address(name="::1/128")],
        )
        assert len(cfg.address) == 1


class TestDdnsConfig:
    """Tests for DdnsConfig model."""

    def test_defaults(self):
        """Verify DdnsConfig default values."""
        ddns = DdnsConfig()
        assert ddns.ddns_enabled is False
        assert ddns.ddns_update_interval == 1

    def test_update_interval_bounds(self):
        """Verify ddns_update_interval enforces valid range 1-30."""
        DdnsConfig(ddns_update_interval=1)
        DdnsConfig(ddns_update_interval=30)
        with pytest.raises(ValidationError):
            DdnsConfig(ddns_update_interval=0)
        with pytest.raises(ValidationError):
            DdnsConfig(ddns_update_interval=31)

    def test_hostname_pattern(self):
        """Verify ddns_hostname validates against pattern."""
        DdnsConfig(ddns_hostname="my-host.example.com")
        with pytest.raises(ValidationError):
            DdnsConfig(ddns_hostname="invalid host!")


class TestLacpConfig:
    """Tests for LacpConfig model."""

    def test_defaults(self):
        """Verify LacpConfig default values."""
        lacp = LacpConfig()
        assert lacp.enable is False
        assert lacp.fast_failover is False
        assert lacp.mode == "passive"
        assert lacp.transmission_rate == "slow"
        assert lacp.system_priority == 32768
        assert lacp.max_ports == 8

    def test_system_priority_bounds(self):
        """Verify system_priority enforces valid range 1-65535."""
        LacpConfig(system_priority=1)
        LacpConfig(system_priority=65535)
        with pytest.raises(ValidationError):
            LacpConfig(system_priority=0)

    def test_max_ports_bounds(self):
        """Verify max_ports enforces valid range 1-8."""
        LacpConfig(max_ports=1)
        LacpConfig(max_ports=8)
        with pytest.raises(ValidationError):
            LacpConfig(max_ports=9)


class TestLldpConfig:
    """Tests for LldpConfig model."""

    def test_defaults(self):
        """Verify LldpConfig defaults to disabled."""
        lldp = LldpConfig()
        assert lldp.enable is False


class TestPppoeModels:
    """Tests for PPPoE configuration models."""

    def test_pppoe_passive_default(self):
        """Verify PppoePassive defaults to disabled."""
        p = PppoePassive()
        assert p.enable is False

    def test_pppoe_static_address(self):
        """Verify PppoeStaticAddress accepts an IP."""
        addr = PppoeStaticAddress(ip="10.0.0.1")
        assert addr.ip == "10.0.0.1"

    def test_pppoe_config_required_fields(self):
        """Verify PppoeConfig requires username and password."""
        with pytest.raises(ValidationError):
            PppoeConfig()

    def test_pppoe_config_valid(self):
        """Verify PppoeConfig with valid required fields and defaults."""
        cfg = PppoeConfig(username="user", password="pass")
        assert cfg.enable is True
        assert cfg.default_route_metric == 10


class TestPoeConfig:
    """Tests for PoeConfig model."""

    def test_defaults(self):
        """Verify PoeConfig defaults."""
        poe = PoeConfig()
        assert poe.poe_enabled is False
        assert poe.poe_rsvd_pwr == 0

    def test_power_bounds(self):
        """Verify poe_rsvd_pwr enforces valid range 0-90."""
        PoeConfig(poe_rsvd_pwr=0)
        PoeConfig(poe_rsvd_pwr=90)
        with pytest.raises(ValidationError):
            PoeConfig(poe_rsvd_pwr=91)


class TestAdjustTcpMss:
    """Tests for AdjustTcpMss model."""

    def test_defaults(self):
        """Verify AdjustTcpMss defaults."""
        mss = AdjustTcpMss()
        assert mss.enable is False
        assert mss.ipv4_mss_adjustment is None

    def test_ipv4_mss_bounds(self):
        """Verify ipv4_mss_adjustment enforces valid range 40-300."""
        AdjustTcpMss(ipv4_mss_adjustment=40)
        AdjustTcpMss(ipv4_mss_adjustment=300)
        with pytest.raises(ValidationError):
            AdjustTcpMss(ipv4_mss_adjustment=39)
        with pytest.raises(ValidationError):
            AdjustTcpMss(ipv4_mss_adjustment=301)

    def test_ipv6_mss_bounds(self):
        """Verify ipv6_mss_adjustment enforces valid range 60-300."""
        AdjustTcpMss(ipv6_mss_adjustment=60)
        AdjustTcpMss(ipv6_mss_adjustment=300)
        with pytest.raises(ValidationError):
            AdjustTcpMss(ipv6_mss_adjustment=59)


class TestBonjourConfig:
    """Tests for BonjourConfig model."""

    def test_defaults(self):
        """Verify BonjourConfig defaults to disabled."""
        b = BonjourConfig()
        assert b.enable is False


class TestNdpProxyConfig:
    """Tests for NdpProxyConfig model."""

    def test_defaults(self):
        """Verify NdpProxyConfig defaults to disabled."""
        ndp = NdpProxyConfig()
        assert ndp.enabled is False


class TestIpv6NeighborDiscovery:
    """Tests for Ipv6NeighborDiscovery model."""

    def test_defaults(self):
        """Verify Ipv6NeighborDiscovery default values."""
        nd = Ipv6NeighborDiscovery()
        assert nd.enable_ndp_monitor is False
        assert nd.enable_dad is True
        assert nd.dad_attempts == 1
        assert nd.ns_interval == 1
        assert nd.reachable_time == 30
        assert nd.enable is False

    def test_dad_attempts_bounds(self):
        """Verify dad_attempts enforces valid range 0-10."""
        Ipv6NeighborDiscovery(dad_attempts=0)
        Ipv6NeighborDiscovery(dad_attempts=10)
        with pytest.raises(ValidationError):
            Ipv6NeighborDiscovery(dad_attempts=11)


class TestIpv6ConfigExtended:
    """Tests for Ipv6ConfigExtended model."""

    def test_defaults(self):
        """Verify Ipv6ConfigExtended default values."""
        cfg = Ipv6ConfigExtended()
        assert cfg.enabled is False
        assert cfg.interface_id is None
        assert cfg.address is None
        assert cfg.neighbor_discovery is None

    def test_with_neighbor_discovery(self):
        """Verify Ipv6ConfigExtended with nested NeighborDiscovery."""
        nd = Ipv6NeighborDiscovery(enable=True)
        cfg = Ipv6ConfigExtended(enabled=True, neighbor_discovery=nd)
        assert cfg.neighbor_discovery.enable is True
