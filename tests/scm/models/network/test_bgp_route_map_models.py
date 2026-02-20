"""Test models for BGP Route Maps."""

from uuid import UUID

from pydantic import ValidationError
import pytest

from scm.models.network import (
    BgpRouteMapBaseModel,
    BgpRouteMapCreateModel,
    BgpRouteMapEntry,
    BgpRouteMapMatch,
    BgpRouteMapMatchIpv4,
    BgpRouteMapResponseModel,
    BgpRouteMapSet,
    BgpRouteMapSetAggregator,
    BgpRouteMapSetIpv4,
    BgpRouteMapSetMetric,
    BgpRouteMapUpdateModel,
)


class TestBgpRouteMapMatchIpv4:
    """Test BGP route map match IPv4 nested model."""

    def test_valid_match_ipv4(self):
        """Test valid IPv4 match with all fields."""
        ipv4 = BgpRouteMapMatchIpv4(
            address="pfx-list-1",
            next_hop="nh-list-1",
            route_source="rs-1",
        )
        assert ipv4.address == "pfx-list-1"
        assert ipv4.next_hop == "nh-list-1"
        assert ipv4.route_source == "rs-1"

    def test_match_ipv4_optional_fields(self):
        """Test IPv4 match with no fields set."""
        ipv4 = BgpRouteMapMatchIpv4()
        assert ipv4.address is None
        assert ipv4.next_hop is None
        assert ipv4.route_source is None

    def test_match_ipv4_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            BgpRouteMapMatchIpv4(address="test", unknown="fail")
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestBgpRouteMapMatch:
    """Test BGP route map match nested model."""

    def test_valid_match_all_fields(self):
        """Test valid match with all fields populated."""
        match = BgpRouteMapMatch(
            as_path_access_list="as-acl",
            interface="eth0",
            regular_community="comm1",
            origin="igp",
            large_community="large-comm1",
            tag=100,
            extended_community="ext-comm1",
            local_preference=200,
            metric=300,
            peer="local",
            ipv4=BgpRouteMapMatchIpv4(address="pfx-1"),
        )
        assert match.as_path_access_list == "as-acl"
        assert match.interface == "eth0"
        assert match.regular_community == "comm1"
        assert match.origin == "igp"
        assert match.large_community == "large-comm1"
        assert match.tag == 100
        assert match.extended_community == "ext-comm1"
        assert match.local_preference == 200
        assert match.metric == 300
        assert match.peer == "local"
        assert match.ipv4.address == "pfx-1"

    def test_match_optional_fields(self):
        """Test match with no fields set."""
        match = BgpRouteMapMatch()
        assert match.as_path_access_list is None
        assert match.peer is None

    def test_peer_valid_local(self):
        """Test valid peer value 'local'."""
        match = BgpRouteMapMatch(peer="local")
        assert match.peer == "local"

    def test_peer_valid_none(self):
        """Test valid peer value 'none'."""
        match = BgpRouteMapMatch(peer="none")
        assert match.peer == "none"

    def test_peer_invalid_value(self):
        """Test invalid peer value raises ValidationError."""
        with pytest.raises(ValidationError):
            BgpRouteMapMatch(peer="invalid")

    def test_match_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            BgpRouteMapMatch(unknown="fail")
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestBgpRouteMapSetMetric:
    """Test BGP route map set metric nested model."""

    def test_valid_set_action(self):
        """Test valid metric set action."""
        metric = BgpRouteMapSetMetric(action="set", value=100)
        assert metric.action == "set"
        assert metric.value == 100

    def test_valid_add_action(self):
        """Test valid metric add action."""
        metric = BgpRouteMapSetMetric(action="add", value=50)
        assert metric.action == "add"
        assert metric.value == 50

    def test_valid_substract_action(self):
        """Test valid metric substract action (API typo must be valid)."""
        metric = BgpRouteMapSetMetric(action="substract", value=25)
        assert metric.action == "substract"
        assert metric.value == 25

    def test_invalid_subtract_action(self):
        """Test that correctly spelled 'subtract' is invalid (API uses 'substract')."""
        with pytest.raises(ValidationError):
            BgpRouteMapSetMetric(action="subtract")

    def test_invalid_action(self):
        """Test invalid metric action raises ValidationError."""
        with pytest.raises(ValidationError):
            BgpRouteMapSetMetric(action="invalid")

    def test_metric_optional_fields(self):
        """Test metric with no fields set."""
        metric = BgpRouteMapSetMetric()
        assert metric.action is None
        assert metric.value is None

    def test_metric_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            BgpRouteMapSetMetric(action="set", unknown="fail")
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestBgpRouteMapSetAggregator:
    """Test BGP route map set aggregator nested model."""

    def test_valid_aggregator(self):
        """Test valid aggregator with both fields."""
        agg = BgpRouteMapSetAggregator(**{"as": 65000, "router_id": "1.1.1.1"})
        assert agg.as_ == 65000
        assert agg.router_id == "1.1.1.1"

    def test_aggregator_as_alias_serialization(self):
        """Test that as_ alias serializes to 'as' in output."""
        agg = BgpRouteMapSetAggregator(**{"as": 65000})
        data = agg.model_dump(by_alias=True)
        assert "as" in data
        assert data["as"] == 65000

    def test_aggregator_optional_fields(self):
        """Test aggregator with no fields set."""
        agg = BgpRouteMapSetAggregator()
        assert agg.as_ is None
        assert agg.router_id is None

    def test_aggregator_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            BgpRouteMapSetAggregator(**{"as": 65000, "unknown": "fail"})
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestBgpRouteMapSetIpv4:
    """Test BGP route map set IPv4 nested model."""

    def test_valid_set_ipv4(self):
        """Test valid IPv4 set with both fields."""
        ipv4 = BgpRouteMapSetIpv4(source_address="10.0.0.1", next_hop="10.0.0.254")
        assert ipv4.source_address == "10.0.0.1"
        assert ipv4.next_hop == "10.0.0.254"

    def test_set_ipv4_optional_fields(self):
        """Test IPv4 set with no fields set."""
        ipv4 = BgpRouteMapSetIpv4()
        assert ipv4.source_address is None
        assert ipv4.next_hop is None


class TestBgpRouteMapSet:
    """Test BGP route map set actions nested model."""

    def test_valid_set_all_fields(self):
        """Test valid set with all fields populated."""
        s = BgpRouteMapSet(
            atomic_aggregate=True,
            local_preference=100,
            tag=200,
            metric=BgpRouteMapSetMetric(action="set", value=50),
            weight=300,
            origin="igp",
            remove_regular_community="comm1",
            remove_large_community="large-comm1",
            originator_id="1.1.1.1",
            aggregator=BgpRouteMapSetAggregator(**{"as": 65000, "router_id": "2.2.2.2"}),
            ipv4=BgpRouteMapSetIpv4(source_address="10.0.0.1"),
            aspath_exclude="65001",
            aspath_prepend="65002 65003",
            regular_community=["100:200"],
            overwrite_regular_community=True,
            large_community=["65000:1:2"],
            overwrite_large_community=False,
        )
        assert s.atomic_aggregate is True
        assert s.local_preference == 100
        assert s.tag == 200
        assert s.metric.action == "set"
        assert s.weight == 300
        assert s.origin == "igp"
        assert s.remove_regular_community == "comm1"
        assert s.remove_large_community == "large-comm1"
        assert s.originator_id == "1.1.1.1"
        assert s.aggregator.as_ == 65000
        assert s.ipv4.source_address == "10.0.0.1"
        assert s.aspath_exclude == "65001"
        assert s.aspath_prepend == "65002 65003"
        assert s.regular_community == ["100:200"]
        assert s.overwrite_regular_community is True
        assert s.large_community == ["65000:1:2"]
        assert s.overwrite_large_community is False

    def test_origin_valid_values(self):
        """Test all valid origin values."""
        for value in ["none", "egp", "igp", "incomplete"]:
            s = BgpRouteMapSet(origin=value)
            assert s.origin == value

    def test_origin_invalid_value(self):
        """Test invalid origin value raises ValidationError."""
        with pytest.raises(ValidationError):
            BgpRouteMapSet(origin="invalid")

    def test_set_optional_fields(self):
        """Test set with no fields set."""
        s = BgpRouteMapSet()
        assert s.atomic_aggregate is None
        assert s.local_preference is None
        assert s.origin is None

    def test_set_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            BgpRouteMapSet(unknown="fail")
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestBgpRouteMapEntry:
    """Test BGP route map entry model."""

    def test_valid_entry(self):
        """Test valid route map entry with all fields."""
        entry = BgpRouteMapEntry(
            name=10,
            description="Test entry",
            action="permit",
            match=BgpRouteMapMatch(peer="local"),
            set=BgpRouteMapSet(local_preference=100),
        )
        assert entry.name == 10
        assert entry.description == "Test entry"
        assert entry.action == "permit"
        assert entry.match.peer == "local"
        assert entry.set.local_preference == 100

    def test_name_min_valid(self):
        """Test name (sequence number) at minimum valid boundary (1)."""
        entry = BgpRouteMapEntry(name=1)
        assert entry.name == 1

    def test_name_max_valid(self):
        """Test name (sequence number) at maximum valid boundary (65535)."""
        entry = BgpRouteMapEntry(name=65535)
        assert entry.name == 65535

    def test_name_below_min_invalid(self):
        """Test name below minimum boundary (0) raises ValidationError."""
        with pytest.raises(ValidationError):
            BgpRouteMapEntry(name=0)

    def test_name_above_max_invalid(self):
        """Test name above maximum boundary (65536) raises ValidationError."""
        with pytest.raises(ValidationError):
            BgpRouteMapEntry(name=65536)

    def test_action_valid_permit(self):
        """Test valid action 'permit'."""
        entry = BgpRouteMapEntry(name=10, action="permit")
        assert entry.action == "permit"

    def test_action_valid_deny(self):
        """Test valid action 'deny'."""
        entry = BgpRouteMapEntry(name=10, action="deny")
        assert entry.action == "deny"

    def test_action_invalid(self):
        """Test invalid action raises ValidationError."""
        with pytest.raises(ValidationError):
            BgpRouteMapEntry(name=10, action="allow")

    def test_entry_optional_fields(self):
        """Test entry with only required fields."""
        entry = BgpRouteMapEntry(name=10)
        assert entry.description is None
        assert entry.action is None
        assert entry.match is None
        assert entry.set is None

    def test_entry_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            BgpRouteMapEntry(name=10, unknown="fail")
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestBgpRouteMapBaseModel:
    """Test BGP Route Map base model validation."""

    def test_valid_minimal_fields(self):
        """Test valid model with only required fields."""
        model = BgpRouteMapBaseModel(name="test-rm", folder="Test Folder")
        assert model.name == "test-rm"
        assert model.folder == "Test Folder"
        assert model.route_map is None

    def test_valid_all_fields(self):
        """Test valid model with all fields populated."""
        model = BgpRouteMapBaseModel(
            name="test-rm",
            folder="Test Folder",
            route_map=[
                BgpRouteMapEntry(
                    name=10,
                    action="permit",
                    match=BgpRouteMapMatch(peer="local"),
                    set=BgpRouteMapSet(local_preference=100),
                ),
                BgpRouteMapEntry(
                    name=20,
                    action="deny",
                ),
            ],
        )
        assert model.name == "test-rm"
        assert len(model.route_map) == 2
        assert model.route_map[0].name == 10
        assert model.route_map[0].action == "permit"
        assert model.route_map[1].name == 20
        assert model.route_map[1].action == "deny"

    def test_missing_name_raises_error(self):
        """Test that missing name field raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            BgpRouteMapBaseModel(folder="Test Folder")
        assert "name" in str(exc_info.value)

    def test_container_folder(self):
        """Test model with folder container."""
        model = BgpRouteMapBaseModel(name="test", folder="MyFolder")
        assert model.folder == "MyFolder"
        assert model.snippet is None
        assert model.device is None

    def test_container_snippet(self):
        """Test model with snippet container."""
        model = BgpRouteMapBaseModel(name="test", snippet="MySnippet")
        assert model.snippet == "MySnippet"
        assert model.folder is None

    def test_container_device(self):
        """Test model with device container."""
        model = BgpRouteMapBaseModel(name="test", device="MyDevice")
        assert model.device == "MyDevice"
        assert model.folder is None

    def test_container_max_length(self):
        """Test container field max_length validation."""
        model = BgpRouteMapBaseModel(name="test", folder="A" * 64)
        assert len(model.folder) == 64

        with pytest.raises(ValidationError):
            BgpRouteMapBaseModel(name="test", folder="A" * 65)

    def test_container_pattern_validation(self):
        """Test container field pattern validation."""
        model = BgpRouteMapBaseModel(name="test", folder="My-Folder_1.0")
        assert model.folder == "My-Folder_1.0"

        with pytest.raises(ValidationError):
            BgpRouteMapBaseModel(name="test", folder="Folder@#$")


class TestBgpRouteMapCreateModel:
    """Test BGP Route Map create model."""

    def test_valid_create_with_folder(self):
        """Test valid create model with folder container."""
        model = BgpRouteMapCreateModel(
            name="test-rm",
            folder="Test Folder",
        )
        assert model.name == "test-rm"
        assert model.folder == "Test Folder"

    def test_valid_create_with_snippet(self):
        """Test valid create model with snippet container."""
        model = BgpRouteMapCreateModel(
            name="test-rm",
            snippet="MySnippet",
        )
        assert model.snippet == "MySnippet"

    def test_valid_create_with_device(self):
        """Test valid create model with device container."""
        model = BgpRouteMapCreateModel(
            name="test-rm",
            device="MyDevice",
        )
        assert model.device == "MyDevice"

    def test_create_no_container_raises_error(self):
        """Test that create without any container raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            BgpRouteMapCreateModel(name="test-rm")
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

    def test_create_multiple_containers_raises_error(self):
        """Test that create with multiple containers raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            BgpRouteMapCreateModel(
                name="test-rm",
                folder="Test Folder",
                snippet="MySnippet",
            )
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

    def test_create_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on BgpRouteMapCreateModel."""
        with pytest.raises(ValidationError) as exc_info:
            BgpRouteMapCreateModel(
                name="test",
                folder="Test Folder",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestBgpRouteMapUpdateModel:
    """Test BGP Route Map update model."""

    def test_valid_update_model(self):
        """Test valid update model."""
        model = BgpRouteMapUpdateModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="updated-rm",
            folder="Test Folder",
        )
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "updated-rm"

    def test_invalid_uuid(self):
        """Test update model with invalid UUID."""
        with pytest.raises(ValidationError):
            BgpRouteMapUpdateModel(
                id="not-a-uuid",
                name="test",
                folder="Test Folder",
            )


class TestBgpRouteMapResponseModel:
    """Test BGP Route Map response model."""

    def test_valid_response_model(self):
        """Test valid response model."""
        model = BgpRouteMapResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="response-rm",
            folder="Test Folder",
        )
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "response-rm"

    def test_missing_id_raises_error(self):
        """Test that missing id field raises ValidationError."""
        with pytest.raises(ValidationError):
            BgpRouteMapResponseModel(
                name="test",
                folder="Test Folder",
            )


class TestExtraFieldsBgpRouteMap:
    """Tests for extra field handling on BGP Route Map models."""

    def test_base_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on BgpRouteMapBaseModel."""
        with pytest.raises(ValidationError) as exc_info:
            BgpRouteMapBaseModel(
                name="test",
                folder="Test Folder",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_update_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on BgpRouteMapUpdateModel."""
        with pytest.raises(ValidationError) as exc_info:
            BgpRouteMapUpdateModel(
                id="123e4567-e89b-12d3-a456-426655440000",
                name="test",
                folder="Test Folder",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_response_model_extra_fields_ignored(self):
        """Test that extra fields are silently ignored on BgpRouteMapResponseModel."""
        model = BgpRouteMapResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test",
            folder="Test Folder",
            unknown_field="should_be_ignored",
        )
        assert not hasattr(model, "unknown_field")
