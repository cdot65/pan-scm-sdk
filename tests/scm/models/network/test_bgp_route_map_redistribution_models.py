"""Test models for BGP Route Map Redistributions."""

from uuid import UUID

from pydantic import ValidationError
import pytest

from scm.models.network import (
    BgpRouteMapRedistBgpMatch,
    BgpRouteMapRedistBgpMatchIpv4,
    BgpRouteMapRedistBgpSource,
    BgpRouteMapRedistBgpToOspf,
    BgpRouteMapRedistBgpToOspfEntry,
    BgpRouteMapRedistBgpToRib,
    BgpRouteMapRedistBgpToRibEntry,
    BgpRouteMapRedistConnectedStaticSource,
    BgpRouteMapRedistConnStaticToBgp,
    BgpRouteMapRedistConnStaticToBgpEntry,
    BgpRouteMapRedistConnStaticToOspf,
    BgpRouteMapRedistConnStaticToOspfEntry,
    BgpRouteMapRedistConnStaticToRib,
    BgpRouteMapRedistConnStaticToRibEntry,
    BgpRouteMapRedistOspfSource,
    BgpRouteMapRedistOspfToBgp,
    BgpRouteMapRedistOspfToBgpEntry,
    BgpRouteMapRedistOspfToRib,
    BgpRouteMapRedistOspfToRibEntry,
    BgpRouteMapRedistSetAggregator,
    BgpRouteMapRedistSetIpv4,
    BgpRouteMapRedistSetMetric,
    BgpRouteMapRedistSetToBgp,
    BgpRouteMapRedistSetToOspf,
    BgpRouteMapRedistSetToRib,
    BgpRouteMapRedistSimpleMatch,
    BgpRouteMapRedistSimpleMatchIpv4,
    BgpRouteMapRedistributionBaseModel,
    BgpRouteMapRedistributionCreateModel,
    BgpRouteMapRedistributionResponseModel,
    BgpRouteMapRedistributionUpdateModel,
)


# --- Match Models ---


class TestBgpRouteMapRedistBgpMatchIpv4:
    """Test BGP redistribution BGP match IPv4 nested model."""

    def test_valid_all_fields(self):
        """Test valid IPv4 match with all fields."""
        ipv4 = BgpRouteMapRedistBgpMatchIpv4(
            address="pfx-list-1",
            next_hop="nh-list-1",
            route_source="rs-1",
        )
        assert ipv4.address == "pfx-list-1"
        assert ipv4.next_hop == "nh-list-1"
        assert ipv4.route_source == "rs-1"

    def test_optional_fields(self):
        """Test IPv4 match with no fields set."""
        ipv4 = BgpRouteMapRedistBgpMatchIpv4()
        assert ipv4.address is None
        assert ipv4.next_hop is None
        assert ipv4.route_source is None

    def test_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            BgpRouteMapRedistBgpMatchIpv4(address="test", unknown="fail")
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestBgpRouteMapRedistBgpMatch:
    """Test BGP redistribution BGP match nested model."""

    def test_valid_all_fields(self):
        """Test valid BGP match with all fields populated."""
        match = BgpRouteMapRedistBgpMatch(
            as_path_access_list="as-acl",
            regular_community="comm1",
            large_community="large-comm1",
            extended_community="ext-comm1",
            interface="eth0",
            tag=100,
            local_preference=200,
            metric=300,
            origin="igp",
            peer="local",
            ipv4=BgpRouteMapRedistBgpMatchIpv4(address="pfx-1"),
        )
        assert match.as_path_access_list == "as-acl"
        assert match.regular_community == "comm1"
        assert match.peer == "local"
        assert match.ipv4.address == "pfx-1"

    def test_peer_valid_values(self):
        """Test valid peer pattern values."""
        for value in ["local", "none"]:
            match = BgpRouteMapRedistBgpMatch(peer=value)
            assert match.peer == value

    def test_peer_invalid_value(self):
        """Test invalid peer value raises ValidationError."""
        with pytest.raises(ValidationError):
            BgpRouteMapRedistBgpMatch(peer="invalid")

    def test_optional_fields(self):
        """Test BGP match with no fields set."""
        match = BgpRouteMapRedistBgpMatch()
        assert match.as_path_access_list is None
        assert match.peer is None


class TestBgpRouteMapRedistSimpleMatchIpv4:
    """Test BGP redistribution simple match IPv4 nested model."""

    def test_valid_all_fields(self):
        """Test valid simple match IPv4 with all fields."""
        ipv4 = BgpRouteMapRedistSimpleMatchIpv4(
            address="pfx-list-1",
            next_hop="nh-list-1",
        )
        assert ipv4.address == "pfx-list-1"
        assert ipv4.next_hop == "nh-list-1"

    def test_optional_fields(self):
        """Test simple match IPv4 with no fields set."""
        ipv4 = BgpRouteMapRedistSimpleMatchIpv4()
        assert ipv4.address is None
        assert ipv4.next_hop is None


class TestBgpRouteMapRedistSimpleMatch:
    """Test BGP redistribution simple match nested model."""

    def test_valid_all_fields(self):
        """Test valid simple match with all fields."""
        match = BgpRouteMapRedistSimpleMatch(
            interface="eth0",
            metric=100,
            tag=200,
            ipv4=BgpRouteMapRedistSimpleMatchIpv4(address="pfx-1"),
        )
        assert match.interface == "eth0"
        assert match.metric == 100
        assert match.tag == 200
        assert match.ipv4.address == "pfx-1"

    def test_optional_fields(self):
        """Test simple match with no fields set."""
        match = BgpRouteMapRedistSimpleMatch()
        assert match.interface is None
        assert match.metric is None
        assert match.tag is None
        assert match.ipv4 is None


# --- Set Models ---


class TestBgpRouteMapRedistSetMetric:
    """Test BGP redistribution set metric nested model."""

    def test_valid_set_action(self):
        """Test valid metric set action."""
        metric = BgpRouteMapRedistSetMetric(action="set", value=100)
        assert metric.action == "set"
        assert metric.value == 100

    def test_valid_add_action(self):
        """Test valid metric add action."""
        metric = BgpRouteMapRedistSetMetric(action="add", value=50)
        assert metric.action == "add"

    def test_valid_substract_action(self):
        """Test valid metric substract action (API typo must be valid)."""
        metric = BgpRouteMapRedistSetMetric(action="substract", value=25)
        assert metric.action == "substract"

    def test_invalid_subtract_action(self):
        """Test that correctly spelled 'subtract' is invalid (API uses 'substract')."""
        with pytest.raises(ValidationError):
            BgpRouteMapRedistSetMetric(action="subtract")

    def test_invalid_action(self):
        """Test invalid metric action raises ValidationError."""
        with pytest.raises(ValidationError):
            BgpRouteMapRedistSetMetric(action="invalid")

    def test_optional_fields(self):
        """Test metric with no fields set."""
        metric = BgpRouteMapRedistSetMetric()
        assert metric.action is None
        assert metric.value is None


class TestBgpRouteMapRedistSetAggregator:
    """Test BGP redistribution set aggregator nested model."""

    def test_valid_aggregator(self):
        """Test valid aggregator with both fields."""
        agg = BgpRouteMapRedistSetAggregator(**{"as": 65000, "router_id": "1.1.1.1"})
        assert agg.as_ == 65000
        assert agg.router_id == "1.1.1.1"

    def test_aggregator_as_alias_serialization(self):
        """Test that as_ alias serializes to 'as' in output."""
        agg = BgpRouteMapRedistSetAggregator(**{"as": 65000})
        data = agg.model_dump(by_alias=True)
        assert "as" in data
        assert data["as"] == 65000

    def test_optional_fields(self):
        """Test aggregator with no fields set."""
        agg = BgpRouteMapRedistSetAggregator()
        assert agg.as_ is None
        assert agg.router_id is None


class TestBgpRouteMapRedistSetIpv4:
    """Test BGP redistribution set IPv4 nested model."""

    def test_valid_all_fields(self):
        """Test valid IPv4 set with all fields."""
        ipv4 = BgpRouteMapRedistSetIpv4(
            source_address="10.0.0.1",
            next_hop="10.0.0.254",
        )
        assert ipv4.source_address == "10.0.0.1"
        assert ipv4.next_hop == "10.0.0.254"

    def test_optional_fields(self):
        """Test IPv4 set with no fields set."""
        ipv4 = BgpRouteMapRedistSetIpv4()
        assert ipv4.source_address is None
        assert ipv4.next_hop is None


class TestBgpRouteMapRedistSetToBgp:
    """Test BGP redistribution set-to-BGP model."""

    def test_valid_all_fields(self):
        """Test valid set-to-BGP with all fields populated."""
        s = BgpRouteMapRedistSetToBgp(
            atomic_aggregate=True,
            local_preference=100,
            tag=200,
            metric=BgpRouteMapRedistSetMetric(action="set", value=50),
            weight=300,
            origin="igp",
            remove_regular_community="comm1",
            remove_large_community="large-comm1",
            originator_id="1.1.1.1",
            aggregator=BgpRouteMapRedistSetAggregator(**{"as": 65000}),
            ipv4=BgpRouteMapRedistSetIpv4(source_address="10.0.0.1"),
            aspath_exclude="65001",
            aspath_prepend="65002",
            regular_community=["100:200"],
            overwrite_regular_community=True,
            large_community=["65000:1:2"],
            overwrite_large_community=False,
        )
        assert s.atomic_aggregate is True
        assert s.local_preference == 100
        assert s.origin == "igp"
        assert s.aggregator.as_ == 65000

    def test_origin_valid_values(self):
        """Test all valid origin values."""
        for value in ["none", "egp", "igp", "incomplete"]:
            s = BgpRouteMapRedistSetToBgp(origin=value)
            assert s.origin == value

    def test_origin_invalid_value(self):
        """Test invalid origin value raises ValidationError."""
        with pytest.raises(ValidationError):
            BgpRouteMapRedistSetToBgp(origin="invalid")

    def test_optional_fields(self):
        """Test set-to-BGP with no fields set."""
        s = BgpRouteMapRedistSetToBgp()
        assert s.atomic_aggregate is None
        assert s.origin is None


class TestBgpRouteMapRedistSetToOspf:
    """Test BGP redistribution set-to-OSPF model."""

    def test_valid_all_fields(self):
        """Test valid set-to-OSPF with all fields."""
        s = BgpRouteMapRedistSetToOspf(
            metric=BgpRouteMapRedistSetMetric(action="set", value=100),
            metric_type="type-1",
            tag=200,
        )
        assert s.metric.action == "set"
        assert s.metric.value == 100
        assert s.metric_type == "type-1"
        assert s.tag == 200

    def test_optional_fields(self):
        """Test set-to-OSPF with no fields set."""
        s = BgpRouteMapRedistSetToOspf()
        assert s.metric is None
        assert s.metric_type is None
        assert s.tag is None


class TestBgpRouteMapRedistSetToRib:
    """Test BGP redistribution set-to-RIB model."""

    def test_valid_with_ipv4(self):
        """Test valid set-to-RIB with IPv4 config."""
        s = BgpRouteMapRedistSetToRib(ipv4=BgpRouteMapRedistSetIpv4(source_address="10.0.0.1"))
        assert s.ipv4.source_address == "10.0.0.1"

    def test_optional_fields(self):
        """Test set-to-RIB with no fields set."""
        s = BgpRouteMapRedistSetToRib()
        assert s.ipv4 is None


# --- Source Protocol Models (Level 1) ---


class TestBgpRouteMapRedistBgpSource:
    """Test BGP source protocol model (oneOf: ospf or rib)."""

    def test_valid_to_ospf_only(self):
        """Test valid BGP source with ospf only."""
        src = BgpRouteMapRedistBgpSource(
            ospf=BgpRouteMapRedistBgpToOspf(
                route_map=[BgpRouteMapRedistBgpToOspfEntry(name=10, action="permit")]
            )
        )
        assert src.ospf is not None
        assert src.rib is None

    def test_valid_to_rib_only(self):
        """Test valid BGP source with rib only."""
        src = BgpRouteMapRedistBgpSource(
            rib=BgpRouteMapRedistBgpToRib(
                route_map=[BgpRouteMapRedistBgpToRibEntry(name=10, action="deny")]
            )
        )
        assert src.rib is not None
        assert src.ospf is None

    def test_both_targets_raises_error(self):
        """Test that setting both ospf and rib raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            BgpRouteMapRedistBgpSource(
                ospf=BgpRouteMapRedistBgpToOspf(),
                rib=BgpRouteMapRedistBgpToRib(),
            )
        assert "Only one of 'ospf' or 'rib' can be set" in str(exc_info.value)

    def test_neither_target_is_valid(self):
        """Test that no target set is valid."""
        src = BgpRouteMapRedistBgpSource()
        assert src.ospf is None
        assert src.rib is None


class TestBgpRouteMapRedistOspfSource:
    """Test OSPF source protocol model (oneOf: bgp or rib)."""

    def test_valid_to_bgp_only(self):
        """Test valid OSPF source with bgp only."""
        src = BgpRouteMapRedistOspfSource(
            bgp=BgpRouteMapRedistOspfToBgp(
                route_map=[BgpRouteMapRedistOspfToBgpEntry(name=10, action="permit")]
            )
        )
        assert src.bgp is not None
        assert src.rib is None

    def test_valid_to_rib_only(self):
        """Test valid OSPF source with rib only."""
        src = BgpRouteMapRedistOspfSource(
            rib=BgpRouteMapRedistOspfToRib(
                route_map=[BgpRouteMapRedistOspfToRibEntry(name=10, action="deny")]
            )
        )
        assert src.rib is not None
        assert src.bgp is None

    def test_both_targets_raises_error(self):
        """Test that setting both bgp and rib raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            BgpRouteMapRedistOspfSource(
                bgp=BgpRouteMapRedistOspfToBgp(),
                rib=BgpRouteMapRedistOspfToRib(),
            )
        assert "Only one of 'bgp' or 'rib' can be set" in str(exc_info.value)

    def test_neither_target_is_valid(self):
        """Test that no target set is valid."""
        src = BgpRouteMapRedistOspfSource()
        assert src.bgp is None
        assert src.rib is None


class TestBgpRouteMapRedistConnectedStaticSource:
    """Test Connected/Static source protocol model (oneOf: bgp, ospf, or rib)."""

    def test_valid_to_bgp_only(self):
        """Test valid connected_static source with bgp only."""
        src = BgpRouteMapRedistConnectedStaticSource(
            bgp=BgpRouteMapRedistConnStaticToBgp(
                route_map=[BgpRouteMapRedistConnStaticToBgpEntry(name=10)]
            )
        )
        assert src.bgp is not None
        assert src.ospf is None
        assert src.rib is None

    def test_valid_to_ospf_only(self):
        """Test valid connected_static source with ospf only."""
        src = BgpRouteMapRedistConnectedStaticSource(
            ospf=BgpRouteMapRedistConnStaticToOspf(
                route_map=[BgpRouteMapRedistConnStaticToOspfEntry(name=10)]
            )
        )
        assert src.ospf is not None
        assert src.bgp is None
        assert src.rib is None

    def test_valid_to_rib_only(self):
        """Test valid connected_static source with rib only."""
        src = BgpRouteMapRedistConnectedStaticSource(
            rib=BgpRouteMapRedistConnStaticToRib(
                route_map=[BgpRouteMapRedistConnStaticToRibEntry(name=10)]
            )
        )
        assert src.rib is not None
        assert src.bgp is None
        assert src.ospf is None

    def test_multiple_targets_raises_error(self):
        """Test that setting multiple targets raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            BgpRouteMapRedistConnectedStaticSource(
                bgp=BgpRouteMapRedistConnStaticToBgp(),
                ospf=BgpRouteMapRedistConnStaticToOspf(),
            )
        assert "Only one of 'bgp', 'ospf', or 'rib' can be set" in str(exc_info.value)

    def test_all_three_targets_raises_error(self):
        """Test that setting all three targets raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            BgpRouteMapRedistConnectedStaticSource(
                bgp=BgpRouteMapRedistConnStaticToBgp(),
                ospf=BgpRouteMapRedistConnStaticToOspf(),
                rib=BgpRouteMapRedistConnStaticToRib(),
            )
        assert "Only one of 'bgp', 'ospf', or 'rib' can be set" in str(exc_info.value)

    def test_neither_target_is_valid(self):
        """Test that no target set is valid."""
        src = BgpRouteMapRedistConnectedStaticSource()
        assert src.bgp is None
        assert src.ospf is None
        assert src.rib is None


# --- Level 1 Mutual Exclusivity (Base Model) ---


class TestBgpRouteMapRedistributionBaseModelSourceExclusivity:
    """Test Level 1 mutual exclusivity: bgp, ospf, connected_static sources."""

    def test_valid_bgp_only(self):
        """Test valid model with bgp source only."""
        model = BgpRouteMapRedistributionBaseModel(
            name="test-redist",
            folder="Test Folder",
            bgp=BgpRouteMapRedistBgpSource(ospf=BgpRouteMapRedistBgpToOspf()),
        )
        assert model.bgp is not None
        assert model.ospf is None
        assert model.connected_static is None

    def test_valid_ospf_only(self):
        """Test valid model with ospf source only."""
        model = BgpRouteMapRedistributionBaseModel(
            name="test-redist",
            folder="Test Folder",
            ospf=BgpRouteMapRedistOspfSource(bgp=BgpRouteMapRedistOspfToBgp()),
        )
        assert model.ospf is not None
        assert model.bgp is None
        assert model.connected_static is None

    def test_valid_connected_static_only(self):
        """Test valid model with connected_static source only."""
        model = BgpRouteMapRedistributionBaseModel(
            name="test-redist",
            folder="Test Folder",
            connected_static=BgpRouteMapRedistConnectedStaticSource(
                bgp=BgpRouteMapRedistConnStaticToBgp()
            ),
        )
        assert model.connected_static is not None
        assert model.bgp is None
        assert model.ospf is None

    def test_multiple_sources_raises_error(self):
        """Test that setting multiple source protocols raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            BgpRouteMapRedistributionBaseModel(
                name="test-redist",
                folder="Test Folder",
                bgp=BgpRouteMapRedistBgpSource(),
                ospf=BgpRouteMapRedistOspfSource(),
            )
        assert "At most one source protocol can be set" in str(exc_info.value)

    def test_all_three_sources_raises_error(self):
        """Test that setting all three source protocols raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            BgpRouteMapRedistributionBaseModel(
                name="test-redist",
                folder="Test Folder",
                bgp=BgpRouteMapRedistBgpSource(),
                ospf=BgpRouteMapRedistOspfSource(),
                connected_static=BgpRouteMapRedistConnectedStaticSource(),
            )
        assert "At most one source protocol can be set" in str(exc_info.value)

    def test_no_source_is_valid(self):
        """Test that no source protocol set is valid."""
        model = BgpRouteMapRedistributionBaseModel(
            name="test-redist",
            folder="Test Folder",
        )
        assert model.bgp is None
        assert model.ospf is None
        assert model.connected_static is None


# --- Crossover Variant Integration Tests ---


class TestBgpRouteMapRedistCrossoverVariants:
    """Integration tests for all 7 source->target redistribution variants."""

    def test_bgp_to_ospf_full_model(self):
        """Test full valid model for bgp->ospf redistribution."""
        model = BgpRouteMapRedistributionBaseModel(
            name="bgp-to-ospf",
            folder="Test Folder",
            bgp=BgpRouteMapRedistBgpSource(
                ospf=BgpRouteMapRedistBgpToOspf(
                    route_map=[
                        BgpRouteMapRedistBgpToOspfEntry(
                            name=10,
                            action="permit",
                            match=BgpRouteMapRedistBgpMatch(
                                as_path_access_list="as-acl",
                                peer="local",
                            ),
                            set=BgpRouteMapRedistSetToOspf(
                                metric=BgpRouteMapRedistSetMetric(action="set", value=100),
                                tag=200,
                            ),
                        )
                    ]
                )
            ),
        )
        assert model.bgp.ospf.route_map[0].name == 10
        assert model.bgp.ospf.route_map[0].action == "permit"
        assert model.bgp.ospf.route_map[0].match.as_path_access_list == "as-acl"
        assert model.bgp.ospf.route_map[0].set.metric.action == "set"
        assert model.bgp.ospf.route_map[0].set.tag == 200
        # Verify set model type is ToOspf
        assert isinstance(model.bgp.ospf.route_map[0].set, BgpRouteMapRedistSetToOspf)

    def test_bgp_to_rib_full_model(self):
        """Test full valid model for bgp->rib redistribution."""
        model = BgpRouteMapRedistributionBaseModel(
            name="bgp-to-rib",
            folder="Test Folder",
            bgp=BgpRouteMapRedistBgpSource(
                rib=BgpRouteMapRedistBgpToRib(
                    route_map=[
                        BgpRouteMapRedistBgpToRibEntry(
                            name=10,
                            action="deny",
                            match=BgpRouteMapRedistBgpMatch(
                                ipv4=BgpRouteMapRedistBgpMatchIpv4(address="pfx-1"),
                            ),
                            set=BgpRouteMapRedistSetToRib(
                                ipv4=BgpRouteMapRedistSetIpv4(source_address="10.0.0.1"),
                            ),
                        )
                    ]
                )
            ),
        )
        assert model.bgp.rib.route_map[0].name == 10
        assert model.bgp.rib.route_map[0].action == "deny"
        assert model.bgp.rib.route_map[0].match.ipv4.address == "pfx-1"
        assert model.bgp.rib.route_map[0].set.ipv4.source_address == "10.0.0.1"
        # Verify set model type is ToRib
        assert isinstance(model.bgp.rib.route_map[0].set, BgpRouteMapRedistSetToRib)

    def test_ospf_to_bgp_full_model(self):
        """Test full valid model for ospf->bgp redistribution."""
        model = BgpRouteMapRedistributionBaseModel(
            name="ospf-to-bgp",
            folder="Test Folder",
            ospf=BgpRouteMapRedistOspfSource(
                bgp=BgpRouteMapRedistOspfToBgp(
                    route_map=[
                        BgpRouteMapRedistOspfToBgpEntry(
                            name=10,
                            action="permit",
                            match=BgpRouteMapRedistSimpleMatch(
                                interface="eth0",
                                metric=100,
                            ),
                            set=BgpRouteMapRedistSetToBgp(
                                local_preference=200,
                                origin="igp",
                                weight=300,
                            ),
                        )
                    ]
                )
            ),
        )
        assert model.ospf.bgp.route_map[0].name == 10
        assert model.ospf.bgp.route_map[0].match.interface == "eth0"
        assert model.ospf.bgp.route_map[0].set.local_preference == 200
        assert model.ospf.bgp.route_map[0].set.origin == "igp"
        # Verify set model type is ToBgp
        assert isinstance(model.ospf.bgp.route_map[0].set, BgpRouteMapRedistSetToBgp)

    def test_ospf_to_rib_full_model(self):
        """Test full valid model for ospf->rib redistribution."""
        model = BgpRouteMapRedistributionBaseModel(
            name="ospf-to-rib",
            folder="Test Folder",
            ospf=BgpRouteMapRedistOspfSource(
                rib=BgpRouteMapRedistOspfToRib(
                    route_map=[
                        BgpRouteMapRedistOspfToRibEntry(
                            name=10,
                            action="permit",
                            match=BgpRouteMapRedistSimpleMatch(
                                tag=500,
                                ipv4=BgpRouteMapRedistSimpleMatchIpv4(address="pfx-2"),
                            ),
                            set=BgpRouteMapRedistSetToRib(
                                ipv4=BgpRouteMapRedistSetIpv4(next_hop="10.0.0.254"),
                            ),
                        )
                    ]
                )
            ),
        )
        assert model.ospf.rib.route_map[0].name == 10
        assert model.ospf.rib.route_map[0].match.tag == 500
        assert model.ospf.rib.route_map[0].set.ipv4.next_hop == "10.0.0.254"
        # Verify set model type is ToRib
        assert isinstance(model.ospf.rib.route_map[0].set, BgpRouteMapRedistSetToRib)

    def test_connected_static_to_bgp_full_model(self):
        """Test full valid model for connected_static->bgp redistribution."""
        model = BgpRouteMapRedistributionBaseModel(
            name="cs-to-bgp",
            folder="Test Folder",
            connected_static=BgpRouteMapRedistConnectedStaticSource(
                bgp=BgpRouteMapRedistConnStaticToBgp(
                    route_map=[
                        BgpRouteMapRedistConnStaticToBgpEntry(
                            name=10,
                            action="permit",
                            match=BgpRouteMapRedistSimpleMatch(
                                interface="loopback0",
                            ),
                            set=BgpRouteMapRedistSetToBgp(
                                atomic_aggregate=True,
                                local_preference=150,
                                aspath_prepend="65001 65002",
                                regular_community=["100:200"],
                                overwrite_regular_community=True,
                            ),
                        )
                    ]
                )
            ),
        )
        assert model.connected_static.bgp.route_map[0].name == 10
        assert model.connected_static.bgp.route_map[0].set.atomic_aggregate is True
        assert model.connected_static.bgp.route_map[0].set.aspath_prepend == "65001 65002"
        # Verify set model type is ToBgp
        assert isinstance(model.connected_static.bgp.route_map[0].set, BgpRouteMapRedistSetToBgp)

    def test_connected_static_to_ospf_full_model(self):
        """Test full valid model for connected_static->ospf redistribution."""
        model = BgpRouteMapRedistributionBaseModel(
            name="cs-to-ospf",
            folder="Test Folder",
            connected_static=BgpRouteMapRedistConnectedStaticSource(
                ospf=BgpRouteMapRedistConnStaticToOspf(
                    route_map=[
                        BgpRouteMapRedistConnStaticToOspfEntry(
                            name=10,
                            action="deny",
                            match=BgpRouteMapRedistSimpleMatch(
                                metric=50,
                            ),
                            set=BgpRouteMapRedistSetToOspf(
                                metric=BgpRouteMapRedistSetMetric(action="add", value=10),
                                metric_type="type-2",
                                tag=999,
                            ),
                        )
                    ]
                )
            ),
        )
        assert model.connected_static.ospf.route_map[0].name == 10
        assert model.connected_static.ospf.route_map[0].action == "deny"
        assert model.connected_static.ospf.route_map[0].set.metric.action == "add"
        assert model.connected_static.ospf.route_map[0].set.metric_type == "type-2"
        # Verify set model type is ToOspf
        assert isinstance(model.connected_static.ospf.route_map[0].set, BgpRouteMapRedistSetToOspf)

    def test_connected_static_to_rib_full_model(self):
        """Test full valid model for connected_static->rib redistribution."""
        model = BgpRouteMapRedistributionBaseModel(
            name="cs-to-rib",
            folder="Test Folder",
            connected_static=BgpRouteMapRedistConnectedStaticSource(
                rib=BgpRouteMapRedistConnStaticToRib(
                    route_map=[
                        BgpRouteMapRedistConnStaticToRibEntry(
                            name=10,
                            action="permit",
                            match=BgpRouteMapRedistSimpleMatch(
                                ipv4=BgpRouteMapRedistSimpleMatchIpv4(
                                    address="pfx-3",
                                    next_hop="nh-3",
                                ),
                            ),
                            set=BgpRouteMapRedistSetToRib(
                                ipv4=BgpRouteMapRedistSetIpv4(
                                    source_address="192.168.1.1",
                                ),
                            ),
                        )
                    ]
                )
            ),
        )
        assert model.connected_static.rib.route_map[0].name == 10
        assert model.connected_static.rib.route_map[0].match.ipv4.address == "pfx-3"
        assert model.connected_static.rib.route_map[0].set.ipv4.source_address == "192.168.1.1"
        # Verify set model type is ToRib
        assert isinstance(model.connected_static.rib.route_map[0].set, BgpRouteMapRedistSetToRib)


# --- Base / Create / Update / Response Models ---


class TestBgpRouteMapRedistributionBaseModel:
    """Test BGP Route Map Redistribution base model validation."""

    def test_valid_minimal_fields(self):
        """Test valid model with only required fields."""
        model = BgpRouteMapRedistributionBaseModel(
            name="test-redist",
            folder="Test Folder",
        )
        assert model.name == "test-redist"
        assert model.folder == "Test Folder"
        assert model.bgp is None
        assert model.ospf is None
        assert model.connected_static is None

    def test_missing_name_raises_error(self):
        """Test that missing name field raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            BgpRouteMapRedistributionBaseModel(folder="Test Folder")
        assert "name" in str(exc_info.value)

    def test_container_folder(self):
        """Test model with folder container."""
        model = BgpRouteMapRedistributionBaseModel(name="test", folder="MyFolder")
        assert model.folder == "MyFolder"
        assert model.snippet is None
        assert model.device is None

    def test_container_snippet(self):
        """Test model with snippet container."""
        model = BgpRouteMapRedistributionBaseModel(name="test", snippet="MySnippet")
        assert model.snippet == "MySnippet"
        assert model.folder is None

    def test_container_device(self):
        """Test model with device container."""
        model = BgpRouteMapRedistributionBaseModel(name="test", device="MyDevice")
        assert model.device == "MyDevice"
        assert model.folder is None

    def test_container_max_length(self):
        """Test container field max_length validation."""
        model = BgpRouteMapRedistributionBaseModel(name="test", folder="A" * 64)
        assert len(model.folder) == 64

        with pytest.raises(ValidationError):
            BgpRouteMapRedistributionBaseModel(name="test", folder="A" * 65)

    def test_container_pattern_validation(self):
        """Test container field pattern validation."""
        model = BgpRouteMapRedistributionBaseModel(name="test", folder="My-Folder_1.0")
        assert model.folder == "My-Folder_1.0"

        with pytest.raises(ValidationError):
            BgpRouteMapRedistributionBaseModel(name="test", folder="Folder@#$")


class TestBgpRouteMapRedistributionCreateModel:
    """Test BGP Route Map Redistribution create model."""

    def test_valid_create_with_folder(self):
        """Test valid create model with folder container."""
        model = BgpRouteMapRedistributionCreateModel(
            name="test-redist",
            folder="Test Folder",
        )
        assert model.name == "test-redist"
        assert model.folder == "Test Folder"

    def test_valid_create_with_snippet(self):
        """Test valid create model with snippet container."""
        model = BgpRouteMapRedistributionCreateModel(
            name="test-redist",
            snippet="MySnippet",
        )
        assert model.snippet == "MySnippet"

    def test_valid_create_with_device(self):
        """Test valid create model with device container."""
        model = BgpRouteMapRedistributionCreateModel(
            name="test-redist",
            device="MyDevice",
        )
        assert model.device == "MyDevice"

    def test_create_no_container_raises_error(self):
        """Test that create without any container raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            BgpRouteMapRedistributionCreateModel(name="test-redist")
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

    def test_create_multiple_containers_raises_error(self):
        """Test that create with multiple containers raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            BgpRouteMapRedistributionCreateModel(
                name="test-redist",
                folder="Test Folder",
                snippet="MySnippet",
            )
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

    def test_create_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on BgpRouteMapRedistributionCreateModel."""
        with pytest.raises(ValidationError) as exc_info:
            BgpRouteMapRedistributionCreateModel(
                name="test",
                folder="Test Folder",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestBgpRouteMapRedistributionUpdateModel:
    """Test BGP Route Map Redistribution update model."""

    def test_valid_update_model(self):
        """Test valid update model."""
        model = BgpRouteMapRedistributionUpdateModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="updated-redist",
            folder="Test Folder",
        )
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "updated-redist"

    def test_invalid_uuid(self):
        """Test update model with invalid UUID."""
        with pytest.raises(ValidationError):
            BgpRouteMapRedistributionUpdateModel(
                id="not-a-uuid",
                name="test",
                folder="Test Folder",
            )


class TestBgpRouteMapRedistributionResponseModel:
    """Test BGP Route Map Redistribution response model."""

    def test_valid_response_model(self):
        """Test valid response model."""
        model = BgpRouteMapRedistributionResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="response-redist",
            folder="Test Folder",
        )
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "response-redist"

    def test_missing_id_raises_error(self):
        """Test that missing id field raises ValidationError."""
        with pytest.raises(ValidationError):
            BgpRouteMapRedistributionResponseModel(
                name="test",
                folder="Test Folder",
            )


class TestExtraFieldsBgpRouteMapRedistribution:
    """Tests for extra field handling on BGP Route Map Redistribution models."""

    def test_base_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on BgpRouteMapRedistributionBaseModel."""
        with pytest.raises(ValidationError) as exc_info:
            BgpRouteMapRedistributionBaseModel(
                name="test",
                folder="Test Folder",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_update_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on BgpRouteMapRedistributionUpdateModel."""
        with pytest.raises(ValidationError) as exc_info:
            BgpRouteMapRedistributionUpdateModel(
                id="123e4567-e89b-12d3-a456-426655440000",
                name="test",
                folder="Test Folder",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_response_model_extra_fields_ignored(self):
        """Test that extra fields are silently ignored on BgpRouteMapRedistributionResponseModel."""
        model = BgpRouteMapRedistributionResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test",
            folder="Test Folder",
            unknown_field="should_be_ignored",
        )
        assert not hasattr(model, "unknown_field")
