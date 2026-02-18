"""Test models for Logical Router."""

from uuid import UUID

from pydantic import ValidationError
import pytest

from scm.models.network import (
    AdminDists,
    BfdProfile,
    BgpConfig,
    BgpPeer,
    BgpPeerAddress,
    BgpPeerGroup,
    BgpPeerGroupType,
    BgpPolicyAction,
    BgpPolicyActionAllow,
    BgpPolicyUpdateAsPath,
    BgpPolicyUpdateCommunity,
    EcmpAlgorithm,
    EcmpConfig,
    EcmpIpHash,
    EcmpWeightedRoundRobin,
    IPv4Nexthop,
    IPv4RouteTable,
    IPv4StaticRoute,
    IPv6Nexthop,
    IPv6RouteTable,
    IPv6StaticRoute,
    LogicalRouterCreateModel,
    LogicalRouterResponseModel,
    LogicalRouterUpdateModel,
    MonitorDestination,
    OspfArea,
    OspfAreaType,
    OspfAuthProfile,
    OspfConfig,
    OspfInterface,
    OspfLinkType,
    OspfMd5Key,
    OspfNormalArea,
    OspfNssaArea,
    OspfStubArea,
    PathMonitor,
    RoutingStackEnum,
    RoutingTable,
    RoutingTableIp,
    VrAdminDists,
    VrfConfig,
)


class TestAdminDistsModels:
    """Test AdminDists and VrAdminDists models."""

    def test_admin_dists_valid(self):
        """Test valid AdminDists configuration."""
        ad = AdminDists(
            static=10,
            static_ipv6=15,
            ospf_inter=110,
            ospf_intra=30,
            ospf_ext=150,
            bgp_internal=200,
            bgp_external=20,
            bgp_local=200,
            rip=120,
        )
        assert ad.static == 10
        assert ad.static_ipv6 == 15
        assert ad.ospf_inter == 110
        assert ad.ospf_intra == 30
        assert ad.ospf_ext == 150
        assert ad.bgp_internal == 200
        assert ad.bgp_external == 20
        assert ad.bgp_local == 200
        assert ad.rip == 120

    def test_admin_dists_defaults_none(self):
        """Test AdminDists with all defaults (None)."""
        ad = AdminDists()
        assert ad.static is None
        assert ad.bgp_internal is None
        assert ad.rip is None

    def test_admin_dists_extra_fields_forbidden(self):
        """Test that extra fields are rejected on AdminDists."""
        with pytest.raises(ValidationError) as exc_info:
            AdminDists(unknown_field="bad")
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_vr_admin_dists_valid(self):
        """Test valid VrAdminDists configuration."""
        vrad = VrAdminDists(
            static=10,
            static_ipv6=15,
            ospf_int=110,
            ospf_ext=150,
            ospfv3_int=110,
            ospfv3_ext=150,
            ibgp=200,
            ebgp=20,
            rip=120,
        )
        assert vrad.static == 10
        assert vrad.ospf_int == 110
        assert vrad.ibgp == 200
        assert vrad.ebgp == 20

    def test_vr_admin_dists_extra_fields_forbidden(self):
        """Test that extra fields are rejected on VrAdminDists."""
        with pytest.raises(ValidationError) as exc_info:
            VrAdminDists(unknown_field="bad")
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestBfdProfileModel:
    """Test BfdProfile model."""

    def test_bfd_profile_valid(self):
        """Test valid BfdProfile configuration."""
        bfd = BfdProfile(profile="my-bfd-profile")
        assert bfd.profile == "my-bfd-profile"

    def test_bfd_profile_none(self):
        """Test BfdProfile with no profile."""
        bfd = BfdProfile()
        assert bfd.profile is None

    def test_bfd_profile_extra_fields_forbidden(self):
        """Test that extra fields are rejected on BfdProfile."""
        with pytest.raises(ValidationError) as exc_info:
            BfdProfile(profile="test", unknown="bad")
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestMonitorDestinationAndPathMonitor:
    """Test MonitorDestination and PathMonitor models."""

    def test_monitor_destination_valid(self):
        """Test valid MonitorDestination configuration."""
        md = MonitorDestination(
            name="monitor-1",
            enable=True,
            source="10.0.0.1",
            destination="10.0.0.2",
            interval=5,
            count=3,
        )
        assert md.name == "monitor-1"
        assert md.enable is True
        assert md.source == "10.0.0.1"
        assert md.destination == "10.0.0.2"
        assert md.interval == 5
        assert md.count == 3

    def test_monitor_destination_with_fqdn(self):
        """Test MonitorDestination with FQDN destination."""
        md = MonitorDestination(
            name="fqdn-monitor",
            destination_fqdn="www.example.com",
        )
        assert md.destination_fqdn == "www.example.com"

    def test_path_monitor_valid(self):
        """Test valid PathMonitor configuration."""
        pm = PathMonitor(
            enable=True,
            failure_condition="any",
            hold_time=10,
            monitor_destinations=[
                MonitorDestination(name="dest-1", enable=True, destination="10.0.0.1"),
            ],
        )
        assert pm.enable is True
        assert pm.failure_condition == "any"
        assert pm.hold_time == 10
        assert len(pm.monitor_destinations) == 1

    def test_path_monitor_failure_condition_all(self):
        """Test PathMonitor with 'all' failure condition."""
        pm = PathMonitor(failure_condition="all")
        assert pm.failure_condition == "all"

    def test_path_monitor_failure_condition_invalid(self):
        """Test PathMonitor with invalid failure_condition."""
        with pytest.raises(ValidationError):
            PathMonitor(failure_condition="invalid")


class TestIPv4NexthopModel:
    """Test IPv4Nexthop model and mutual exclusivity."""

    def test_nexthop_receive(self):
        """Test IPv4Nexthop with receive."""
        nh = IPv4Nexthop(receive={})
        assert nh.receive == {}
        assert nh.discard is None

    def test_nexthop_discard(self):
        """Test IPv4Nexthop with discard."""
        nh = IPv4Nexthop(discard={})
        assert nh.discard == {}

    def test_nexthop_ip_address(self):
        """Test IPv4Nexthop with ip_address."""
        nh = IPv4Nexthop(ip_address="10.0.0.1")
        assert nh.ip_address == "10.0.0.1"

    def test_nexthop_ipv6_address(self):
        """Test IPv4Nexthop with ipv6_address."""
        nh = IPv4Nexthop(ipv6_address="2001:db8::1")
        assert nh.ipv6_address == "2001:db8::1"

    def test_nexthop_fqdn(self):
        """Test IPv4Nexthop with fqdn."""
        nh = IPv4Nexthop(fqdn="gw.example.com")
        assert nh.fqdn == "gw.example.com"

    def test_nexthop_next_lr(self):
        """Test IPv4Nexthop with next_lr."""
        nh = IPv4Nexthop(next_lr="LR-2")
        assert nh.next_lr == "LR-2"

    def test_nexthop_next_vr(self):
        """Test IPv4Nexthop with next_vr."""
        nh = IPv4Nexthop(next_vr="VR-2")
        assert nh.next_vr == "VR-2"

    def test_nexthop_tunnel(self):
        """Test IPv4Nexthop with tunnel."""
        nh = IPv4Nexthop(tunnel="tunnel.1")
        assert nh.tunnel == "tunnel.1"

    def test_nexthop_mutual_exclusivity(self):
        """Test that multiple nexthop types fail."""
        with pytest.raises(ValueError) as exc_info:
            IPv4Nexthop(ip_address="10.0.0.1", fqdn="gw.example.com")
        assert "At most one nexthop type can be set" in str(exc_info.value)

    def test_nexthop_empty_is_valid(self):
        """Test that no nexthop set is valid (all None)."""
        nh = IPv4Nexthop()
        assert nh.receive is None
        assert nh.ip_address is None


class TestIPv6NexthopModel:
    """Test IPv6Nexthop model and mutual exclusivity."""

    def test_nexthop_receive(self):
        """Test IPv6Nexthop with receive."""
        nh = IPv6Nexthop(receive={})
        assert nh.receive == {}

    def test_nexthop_discard(self):
        """Test IPv6Nexthop with discard."""
        nh = IPv6Nexthop(discard={})
        assert nh.discard == {}

    def test_nexthop_ipv6_address(self):
        """Test IPv6Nexthop with ipv6_address."""
        nh = IPv6Nexthop(ipv6_address="2001:db8::1")
        assert nh.ipv6_address == "2001:db8::1"

    def test_nexthop_fqdn(self):
        """Test IPv6Nexthop with fqdn."""
        nh = IPv6Nexthop(fqdn="gw.example.com")
        assert nh.fqdn == "gw.example.com"

    def test_nexthop_next_lr(self):
        """Test IPv6Nexthop with next_lr."""
        nh = IPv6Nexthop(next_lr="LR-2")
        assert nh.next_lr == "LR-2"

    def test_nexthop_next_vr(self):
        """Test IPv6Nexthop with next_vr."""
        nh = IPv6Nexthop(next_vr="VR-2")
        assert nh.next_vr == "VR-2"

    def test_nexthop_tunnel(self):
        """Test IPv6Nexthop with tunnel."""
        nh = IPv6Nexthop(tunnel="tunnel.1")
        assert nh.tunnel == "tunnel.1"

    def test_nexthop_mutual_exclusivity(self):
        """Test that multiple IPv6 nexthop types fail."""
        with pytest.raises(ValueError) as exc_info:
            IPv6Nexthop(ipv6_address="2001:db8::1", fqdn="gw.example.com")
        assert "At most one nexthop type can be set" in str(exc_info.value)


class TestRouteTableModels:
    """Test IPv4RouteTable and IPv6RouteTable oneOf validation."""

    def test_ipv4_route_table_unicast(self):
        """Test IPv4RouteTable with unicast."""
        rt = IPv4RouteTable(unicast={})
        assert rt.unicast == {}
        assert rt.multicast is None

    def test_ipv4_route_table_multicast(self):
        """Test IPv4RouteTable with multicast."""
        rt = IPv4RouteTable(multicast={})
        assert rt.multicast == {}

    def test_ipv4_route_table_both(self):
        """Test IPv4RouteTable with both."""
        rt = IPv4RouteTable(both={})
        assert rt.both == {}

    def test_ipv4_route_table_no_install(self):
        """Test IPv4RouteTable with no_install."""
        rt = IPv4RouteTable(no_install={})
        assert rt.no_install == {}

    def test_ipv4_route_table_mutual_exclusivity(self):
        """Test that multiple route table types fail."""
        with pytest.raises(ValueError) as exc_info:
            IPv4RouteTable(unicast={}, multicast={})
        assert "At most one route table type can be set" in str(exc_info.value)

    def test_ipv6_route_table_unicast(self):
        """Test IPv6RouteTable with unicast."""
        rt = IPv6RouteTable(unicast={})
        assert rt.unicast == {}

    def test_ipv6_route_table_mutual_exclusivity(self):
        """Test that multiple IPv6 route table types fail."""
        with pytest.raises(ValueError) as exc_info:
            IPv6RouteTable(unicast={}, both={})
        assert "At most one route table type can be set" in str(exc_info.value)


class TestStaticRouteModels:
    """Test IPv4StaticRoute and IPv6StaticRoute models."""

    def test_ipv4_static_route_required_name(self):
        """Test that IPv4StaticRoute requires name."""
        with pytest.raises(ValidationError):
            IPv4StaticRoute()

    def test_ipv4_static_route_valid(self):
        """Test valid IPv4StaticRoute."""
        route = IPv4StaticRoute(
            name="default-route",
            destination="0.0.0.0/0",
            interface="ethernet1/1",
            nexthop=IPv4Nexthop(ip_address="10.0.0.1"),
            admin_dist=10,
            metric=100,
        )
        assert route.name == "default-route"
        assert route.destination == "0.0.0.0/0"
        assert route.nexthop.ip_address == "10.0.0.1"
        assert route.admin_dist == 10

    def test_ipv6_static_route_required_name(self):
        """Test that IPv6StaticRoute requires name."""
        with pytest.raises(ValidationError):
            IPv6StaticRoute()

    def test_ipv6_static_route_valid(self):
        """Test valid IPv6StaticRoute."""
        route = IPv6StaticRoute(
            name="ipv6-default",
            destination="::/0",
            nexthop=IPv6Nexthop(ipv6_address="2001:db8::1"),
        )
        assert route.name == "ipv6-default"
        assert route.destination == "::/0"
        assert route.nexthop.ipv6_address == "2001:db8::1"


class TestOspfAuthProfileModel:
    """Test OspfAuthProfile model with password/md5 oneOf."""

    def test_ospf_auth_profile_with_password(self):
        """Test OspfAuthProfile with password."""
        auth = OspfAuthProfile(name="auth-1", password="secret123")
        assert auth.name == "auth-1"
        assert auth.password == "secret123"
        assert auth.md5 is None

    def test_ospf_auth_profile_with_md5(self):
        """Test OspfAuthProfile with MD5 keys."""
        auth = OspfAuthProfile(
            name="auth-2",
            md5=[OspfMd5Key(name="1", key="md5key", preferred=True)],
        )
        assert auth.name == "auth-2"
        assert auth.password is None
        assert len(auth.md5) == 1
        assert auth.md5[0].preferred is True

    def test_ospf_auth_profile_mutual_exclusivity(self):
        """Test that password and md5 are mutually exclusive."""
        with pytest.raises(ValueError) as exc_info:
            OspfAuthProfile(
                name="auth-bad",
                password="secret",
                md5=[OspfMd5Key(name="1", key="md5key")],
            )
        assert "mutually exclusive" in str(exc_info.value)

    def test_ospf_auth_profile_neither(self):
        """Test OspfAuthProfile with neither password nor md5 (valid)."""
        auth = OspfAuthProfile(name="auth-none")
        assert auth.password is None
        assert auth.md5 is None


class TestOspfAreaTypeModel:
    """Test OspfAreaType model with normal/stub/nssa oneOf."""

    def test_area_type_normal(self):
        """Test OspfAreaType with normal."""
        at = OspfAreaType(normal=OspfNormalArea())
        assert at.normal is not None
        assert at.stub is None
        assert at.nssa is None

    def test_area_type_stub(self):
        """Test OspfAreaType with stub."""
        at = OspfAreaType(stub=OspfStubArea(accept_summary=True))
        assert at.stub is not None
        assert at.stub.accept_summary is True

    def test_area_type_nssa(self):
        """Test OspfAreaType with nssa."""
        at = OspfAreaType(nssa=OspfNssaArea(accept_summary=False))
        assert at.nssa is not None

    def test_area_type_mutual_exclusivity(self):
        """Test that multiple area types fail."""
        with pytest.raises(ValueError) as exc_info:
            OspfAreaType(normal=OspfNormalArea(), stub=OspfStubArea())
        assert "At most one area type can be set" in str(exc_info.value)


class TestOspfLinkTypeModel:
    """Test OspfLinkType model with broadcast/p2p/p2mp oneOf."""

    def test_link_type_broadcast(self):
        """Test OspfLinkType with broadcast."""
        lt = OspfLinkType(broadcast={})
        assert lt.broadcast == {}
        assert lt.p2p is None
        assert lt.p2mp is None

    def test_link_type_p2p(self):
        """Test OspfLinkType with p2p."""
        lt = OspfLinkType(p2p={})
        assert lt.p2p == {}

    def test_link_type_p2mp(self):
        """Test OspfLinkType with p2mp."""
        lt = OspfLinkType(p2mp={})
        assert lt.p2mp == {}

    def test_link_type_mutual_exclusivity(self):
        """Test that multiple link types fail."""
        with pytest.raises(ValueError) as exc_info:
            OspfLinkType(broadcast={}, p2p={})
        assert "At most one link type can be set" in str(exc_info.value)


class TestEcmpAlgorithmModel:
    """Test EcmpAlgorithm model with 4-way oneOf."""

    def test_algorithm_ip_modulo(self):
        """Test EcmpAlgorithm with ip_modulo."""
        alg = EcmpAlgorithm(ip_modulo={})
        assert alg.ip_modulo == {}
        assert alg.ip_hash is None

    def test_algorithm_ip_hash(self):
        """Test EcmpAlgorithm with ip_hash."""
        alg = EcmpAlgorithm(ip_hash=EcmpIpHash(src_only=True, use_port=True, hash_seed=42))
        assert alg.ip_hash.src_only is True
        assert alg.ip_hash.hash_seed == 42

    def test_algorithm_weighted_round_robin(self):
        """Test EcmpAlgorithm with weighted_round_robin."""
        alg = EcmpAlgorithm(weighted_round_robin=EcmpWeightedRoundRobin())
        assert alg.weighted_round_robin is not None

    def test_algorithm_balanced_round_robin(self):
        """Test EcmpAlgorithm with balanced_round_robin."""
        alg = EcmpAlgorithm(balanced_round_robin={})
        assert alg.balanced_round_robin == {}

    def test_algorithm_mutual_exclusivity(self):
        """Test that multiple ECMP algorithms fail."""
        with pytest.raises(ValueError) as exc_info:
            EcmpAlgorithm(ip_modulo={}, balanced_round_robin={})
        assert "At most one ECMP algorithm can be set" in str(exc_info.value)


class TestBgpPeerGroupTypeModel:
    """Test BgpPeerGroupType model with 4-way oneOf."""

    def test_type_ibgp(self):
        """Test BgpPeerGroupType with ibgp."""
        t = BgpPeerGroupType(ibgp={})
        assert t.ibgp == {}
        assert t.ebgp is None

    def test_type_ebgp_confed(self):
        """Test BgpPeerGroupType with ebgp_confed."""
        t = BgpPeerGroupType(ebgp_confed={})
        assert t.ebgp_confed == {}

    def test_type_ibgp_confed(self):
        """Test BgpPeerGroupType with ibgp_confed."""
        t = BgpPeerGroupType(ibgp_confed={})
        assert t.ibgp_confed == {}

    def test_type_ebgp(self):
        """Test BgpPeerGroupType with ebgp."""
        t = BgpPeerGroupType(ebgp={})
        assert t.ebgp == {}

    def test_type_mutual_exclusivity(self):
        """Test that multiple peer group types fail."""
        with pytest.raises(ValueError) as exc_info:
            BgpPeerGroupType(ibgp={}, ebgp={})
        assert "At most one peer group type can be set" in str(exc_info.value)


class TestBgpPeerAddressModel:
    """Test BgpPeerAddress model with ip/fqdn oneOf."""

    def test_peer_address_ip(self):
        """Test BgpPeerAddress with ip."""
        pa = BgpPeerAddress(ip="10.0.0.1")
        assert pa.ip == "10.0.0.1"
        assert pa.fqdn is None

    def test_peer_address_fqdn(self):
        """Test BgpPeerAddress with fqdn."""
        pa = BgpPeerAddress(fqdn="peer.example.com")
        assert pa.fqdn == "peer.example.com"

    def test_peer_address_mutual_exclusivity(self):
        """Test that ip and fqdn are mutually exclusive."""
        with pytest.raises(ValueError) as exc_info:
            BgpPeerAddress(ip="10.0.0.1", fqdn="peer.example.com")
        assert "mutually exclusive" in str(exc_info.value)


class TestBgpPolicyActionModel:
    """Test BgpPolicyAction model with deny/allow oneOf."""

    def test_action_deny(self):
        """Test BgpPolicyAction with deny."""
        action = BgpPolicyAction(deny={})
        assert action.deny == {}
        assert action.allow is None

    def test_action_allow(self):
        """Test BgpPolicyAction with allow."""
        action = BgpPolicyAction(allow=BgpPolicyActionAllow())
        assert action.allow is not None

    def test_action_mutual_exclusivity(self):
        """Test that deny and allow are mutually exclusive."""
        with pytest.raises(ValueError) as exc_info:
            BgpPolicyAction(deny={}, allow=BgpPolicyActionAllow())
        assert "mutually exclusive" in str(exc_info.value)


class TestBgpPolicyUpdateAsPathModel:
    """Test BgpPolicyUpdateAsPath model with 4-way oneOf."""

    def test_as_path_none_action(self):
        """Test BgpPolicyUpdateAsPath with none."""
        asp = BgpPolicyUpdateAsPath(none={})
        assert asp.none == {}

    def test_as_path_remove(self):
        """Test BgpPolicyUpdateAsPath with remove."""
        asp = BgpPolicyUpdateAsPath(remove={})
        assert asp.remove == {}

    def test_as_path_prepend(self):
        """Test BgpPolicyUpdateAsPath with prepend."""
        asp = BgpPolicyUpdateAsPath(prepend=3)
        assert asp.prepend == 3

    def test_as_path_remove_and_prepend(self):
        """Test BgpPolicyUpdateAsPath with remove_and_prepend."""
        asp = BgpPolicyUpdateAsPath(remove_and_prepend=2)
        assert asp.remove_and_prepend == 2

    def test_as_path_mutual_exclusivity(self):
        """Test that multiple AS path actions fail."""
        with pytest.raises(ValueError) as exc_info:
            BgpPolicyUpdateAsPath(none={}, prepend=3)
        assert "At most one AS path action can be set" in str(exc_info.value)


class TestBgpPolicyUpdateCommunityModel:
    """Test BgpPolicyUpdateCommunity model with 5-way oneOf."""

    def test_community_none(self):
        """Test BgpPolicyUpdateCommunity with none."""
        c = BgpPolicyUpdateCommunity(none={})
        assert c.none == {}

    def test_community_remove_all(self):
        """Test BgpPolicyUpdateCommunity with remove_all."""
        c = BgpPolicyUpdateCommunity(remove_all={})
        assert c.remove_all == {}

    def test_community_remove_regex(self):
        """Test BgpPolicyUpdateCommunity with remove_regex."""
        c = BgpPolicyUpdateCommunity(remove_regex="65000:.*")
        assert c.remove_regex == "65000:.*"

    def test_community_append(self):
        """Test BgpPolicyUpdateCommunity with append."""
        c = BgpPolicyUpdateCommunity(append=["65000:100", "65000:200"])
        assert len(c.append) == 2

    def test_community_overwrite(self):
        """Test BgpPolicyUpdateCommunity with overwrite."""
        c = BgpPolicyUpdateCommunity(overwrite=["65000:999"])
        assert c.overwrite == ["65000:999"]

    def test_community_mutual_exclusivity(self):
        """Test that multiple community actions fail."""
        with pytest.raises(ValueError) as exc_info:
            BgpPolicyUpdateCommunity(none={}, append=["65000:100"])
        assert "At most one community action can be set" in str(exc_info.value)


class TestLogicalRouterBaseModelValidation:
    """Test base model validation through LogicalRouterCreateModel."""

    def test_valid_minimal_config(self):
        """Test valid minimal configuration with just name and folder."""
        model = LogicalRouterCreateModel(name="LR-Test", folder="PANDA")
        assert model.name == "LR-Test"
        assert model.folder == "PANDA"
        assert model.routing_stack is None
        assert model.vrf is None

    def test_valid_with_routing_stack(self):
        """Test valid configuration with routing_stack enum."""
        model = LogicalRouterCreateModel(
            name="LR-Advanced",
            folder="PANDA",
            routing_stack="advanced",
        )
        assert model.routing_stack == RoutingStackEnum.ADVANCED

        model = LogicalRouterCreateModel(
            name="LR-Legacy",
            folder="PANDA",
            routing_stack="legacy",
        )
        assert model.routing_stack == RoutingStackEnum.LEGACY

    def test_valid_with_vrf(self):
        """Test valid configuration with VRF containing nested models."""
        model = LogicalRouterCreateModel(
            name="LR-With-VRF",
            folder="PANDA",
            vrf=[
                VrfConfig(
                    name="default",
                    interface=["ethernet1/1", "ethernet1/2"],
                ),
            ],
        )
        assert len(model.vrf) == 1
        assert model.vrf[0].name == "default"
        assert "ethernet1/1" in model.vrf[0].interface

    def test_name_required(self):
        """Test that name is required."""
        with pytest.raises(ValidationError):
            LogicalRouterCreateModel(folder="PANDA")

    def test_invalid_routing_stack(self):
        """Test invalid routing_stack value."""
        with pytest.raises(ValidationError):
            LogicalRouterCreateModel(
                name="LR-Bad",
                folder="PANDA",
                routing_stack="invalid_stack",
            )


class TestLogicalRouterContainerValidation:
    """Test container validation on LogicalRouterCreateModel."""

    def test_folder_container(self):
        """Test with folder container."""
        model = LogicalRouterCreateModel(name="LR-1", folder="PANDA")
        assert model.folder == "PANDA"
        assert model.snippet is None
        assert model.device is None

    def test_snippet_container(self):
        """Test with snippet container."""
        model = LogicalRouterCreateModel(name="LR-1", snippet="MySnippet")
        assert model.snippet == "MySnippet"

    def test_device_container(self):
        """Test with device container."""
        model = LogicalRouterCreateModel(name="LR-1", device="MyDevice")
        assert model.device == "MyDevice"

    def test_no_container_fails(self):
        """Test that no container fails validation."""
        with pytest.raises(ValueError) as exc_info:
            LogicalRouterCreateModel(name="LR-1")
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

    def test_multiple_containers_fails(self):
        """Test that multiple containers fail validation."""
        with pytest.raises(ValueError) as exc_info:
            LogicalRouterCreateModel(name="LR-1", folder="PANDA", snippet="MySnippet")
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )


class TestLogicalRouterUpdateModel:
    """Test LogicalRouterUpdateModel validation."""

    def test_update_model_valid(self):
        """Test valid update model with UUID id field."""
        model = LogicalRouterUpdateModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="LR-Updated",
            folder="PANDA",
        )
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "LR-Updated"

    def test_update_model_id_required(self):
        """Test that id is required for update model."""
        with pytest.raises(ValidationError):
            LogicalRouterUpdateModel(name="LR-Updated", folder="PANDA")

    def test_update_model_invalid_uuid(self):
        """Test invalid UUID for update model."""
        with pytest.raises(ValidationError):
            LogicalRouterUpdateModel(
                id="not-a-uuid",
                name="LR-Updated",
                folder="PANDA",
            )

    def test_update_model_with_routing_stack(self):
        """Test update model with routing_stack."""
        model = LogicalRouterUpdateModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="LR-Updated",
            folder="PANDA",
            routing_stack="advanced",
        )
        assert model.routing_stack == RoutingStackEnum.ADVANCED


class TestLogicalRouterResponseModel:
    """Test LogicalRouterResponseModel validation."""

    def test_response_model_valid(self):
        """Test valid response model."""
        model = LogicalRouterResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="LR-Response",
            folder="PANDA",
        )
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "LR-Response"

    def test_response_model_extra_fields_ignored(self):
        """Test that extra fields are silently ignored on ResponseModel."""
        model = LogicalRouterResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="LR-Response",
            folder="PANDA",
            unknown_field="should_be_ignored",
        )
        assert not hasattr(model, "unknown_field")

    def test_response_model_id_required(self):
        """Test that id is required for response model."""
        with pytest.raises(ValidationError):
            LogicalRouterResponseModel(name="LR-Response", folder="PANDA")

    def test_response_model_with_all_nested_data(self):
        """Test response model with VRF and nested routing data."""
        model = LogicalRouterResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="LR-Full",
            folder="PANDA",
            routing_stack="advanced",
            vrf=[
                VrfConfig(
                    name="default",
                    interface=["ethernet1/1"],
                    admin_dists=AdminDists(static=10, bgp_external=20),
                ),
            ],
        )
        assert model.routing_stack == RoutingStackEnum.ADVANCED
        assert len(model.vrf) == 1
        assert model.vrf[0].admin_dists.static == 10


class TestExtraFieldsForbidden:
    """Tests for extra='forbid' validation on Logical Router models."""

    def test_create_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on LogicalRouterCreateModel."""
        with pytest.raises(ValidationError) as exc_info:
            LogicalRouterCreateModel(
                name="LR-1",
                folder="PANDA",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_update_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on LogicalRouterUpdateModel."""
        with pytest.raises(ValidationError) as exc_info:
            LogicalRouterUpdateModel(
                id="123e4567-e89b-12d3-a456-426655440000",
                name="LR-1",
                folder="PANDA",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_vrf_config_extra_fields_forbidden(self):
        """Test that extra fields are rejected on VrfConfig."""
        with pytest.raises(ValidationError) as exc_info:
            VrfConfig(name="default", unknown_field="bad")
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_ipv4_nexthop_extra_fields_forbidden(self):
        """Test that extra fields are rejected on IPv4Nexthop."""
        with pytest.raises(ValidationError) as exc_info:
            IPv4Nexthop(ip_address="10.0.0.1", unknown_field="bad")
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestCompleteNestedModelConstruction:
    """Test building a complete LogicalRouterCreateModel with deeply nested models."""

    def test_full_model_with_static_routes_bgp_ospf_ecmp(self):
        """Build a LogicalRouterCreateModel with static routes, BGP, OSPF, and ECMP config."""
        model = LogicalRouterCreateModel(
            name="LR-Production",
            folder="PANDA",
            routing_stack="advanced",
            vrf=[
                VrfConfig(
                    name="default",
                    interface=["ethernet1/1", "ethernet1/2"],
                    routing_table=RoutingTable(
                        ip=RoutingTableIp(
                            static_route=[
                                IPv4StaticRoute(
                                    name="default-route",
                                    destination="0.0.0.0/0",
                                    nexthop=IPv4Nexthop(ip_address="10.0.0.1"),
                                    admin_dist=10,
                                    metric=100,
                                ),
                            ]
                        )
                    ),
                    bgp=BgpConfig(
                        enable=True,
                        router_id="10.0.0.1",
                        local_as="65000",
                        peer_group=[
                            BgpPeerGroup(
                                name="EBGP-Peers",
                                enable=True,
                                type=BgpPeerGroupType(ebgp={}),
                                peer=[
                                    BgpPeer(
                                        name="ISP-1",
                                        enable=True,
                                        peer_as="65001",
                                        peer_address=BgpPeerAddress(ip="10.0.1.1"),
                                    ),
                                ],
                            ),
                        ],
                    ),
                    ospf=OspfConfig(
                        enable=True,
                        router_id="10.0.0.1",
                        area=[
                            OspfArea(
                                name="0.0.0.0",
                                type=OspfAreaType(normal=OspfNormalArea()),
                                interface=[
                                    OspfInterface(
                                        name="ethernet1/1",
                                        enable=True,
                                        link_type=OspfLinkType(broadcast={}),
                                    ),
                                ],
                            ),
                        ],
                    ),
                    ecmp=EcmpConfig(
                        enable=True,
                        algorithm=EcmpAlgorithm(
                            ip_hash=EcmpIpHash(src_only=False, use_port=True, hash_seed=12345),
                        ),
                        max_path=4,
                    ),
                ),
            ],
        )

        # Verify the top-level fields
        assert model.name == "LR-Production"
        assert model.routing_stack == RoutingStackEnum.ADVANCED
        assert len(model.vrf) == 1

        vrf = model.vrf[0]
        assert vrf.name == "default"
        assert len(vrf.interface) == 2

        # Verify static routes
        assert len(vrf.routing_table.ip.static_route) == 1
        assert vrf.routing_table.ip.static_route[0].name == "default-route"
        assert vrf.routing_table.ip.static_route[0].nexthop.ip_address == "10.0.0.1"

        # Verify BGP
        assert vrf.bgp.enable is True
        assert vrf.bgp.local_as == "65000"
        assert len(vrf.bgp.peer_group) == 1
        assert vrf.bgp.peer_group[0].name == "EBGP-Peers"
        assert vrf.bgp.peer_group[0].type.ebgp == {}
        assert len(vrf.bgp.peer_group[0].peer) == 1
        assert vrf.bgp.peer_group[0].peer[0].name == "ISP-1"
        assert vrf.bgp.peer_group[0].peer[0].peer_address.ip == "10.0.1.1"

        # Verify OSPF
        assert vrf.ospf.enable is True
        assert len(vrf.ospf.area) == 1
        assert vrf.ospf.area[0].name == "0.0.0.0"
        assert vrf.ospf.area[0].type.normal is not None
        assert len(vrf.ospf.area[0].interface) == 1

        # Verify ECMP
        assert vrf.ecmp.enable is True
        assert vrf.ecmp.algorithm.ip_hash.use_port is True
        assert vrf.ecmp.max_path == 4

    def test_serialization_with_model_dump_by_alias(self):
        """Verify model_dump(by_alias=True) serializes correctly."""
        model = LogicalRouterCreateModel(
            name="LR-Serialize",
            folder="PANDA",
            routing_stack="advanced",
            vrf=[
                VrfConfig(
                    name="default",
                    interface=["ethernet1/1"],
                    bgp=BgpConfig(
                        enable=True,
                        local_as="65000",
                    ),
                ),
            ],
        )

        dumped = model.model_dump(exclude_unset=True, by_alias=True)

        assert dumped["name"] == "LR-Serialize"
        assert dumped["folder"] == "PANDA"
        assert dumped["routing_stack"] == "advanced"
        assert len(dumped["vrf"]) == 1
        assert dumped["vrf"][0]["name"] == "default"
        assert dumped["vrf"][0]["bgp"]["enable"] is True
        assert dumped["vrf"][0]["bgp"]["local_as"] == "65000"

    def test_serialization_excludes_unset_fields(self):
        """Verify exclude_unset=True does not include None fields."""
        model = LogicalRouterCreateModel(
            name="LR-Minimal",
            folder="PANDA",
        )

        dumped = model.model_dump(exclude_unset=True, by_alias=True)

        assert "name" in dumped
        assert "folder" in dumped
        # These should not be present because they were not set
        assert "routing_stack" not in dumped
        assert "vrf" not in dumped
        assert "snippet" not in dumped
        assert "device" not in dumped
