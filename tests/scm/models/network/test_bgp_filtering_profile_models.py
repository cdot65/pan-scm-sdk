"""Test models for BGP Filtering Profiles."""

from uuid import UUID

from pydantic import ValidationError
import pytest

from scm.models.network import (
    BgpConditionalAdvertisement,
    BgpConditionalAdvertisementCondition,
    BgpFilter,
    BgpFilteringProfileBaseModel,
    BgpFilteringProfileCreateModel,
    BgpFilteringProfileIpv4,
    BgpFilteringProfileMulticast,
    BgpFilteringProfileResponseModel,
    BgpFilteringProfileUpdateModel,
    BgpFilterList,
    BgpNetworkFilters,
    BgpRouteMaps,
)


class TestBgpFilterList:
    """Test BGP filter list nested model."""

    def test_valid_filter_list(self):
        """Test valid filter list with both fields."""
        fl = BgpFilterList(inbound="in-filter", outbound="out-filter")
        assert fl.inbound == "in-filter"
        assert fl.outbound == "out-filter"

    def test_filter_list_optional_fields(self):
        """Test filter list with no fields set."""
        fl = BgpFilterList()
        assert fl.inbound is None
        assert fl.outbound is None

    def test_filter_list_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            BgpFilterList(inbound="test", unknown="fail")
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestBgpNetworkFilters:
    """Test BGP network filters nested model."""

    def test_valid_network_filters(self):
        """Test valid network filters with both fields."""
        nf = BgpNetworkFilters(distribute_list="dist-list", prefix_list="pfx-list")
        assert nf.distribute_list == "dist-list"
        assert nf.prefix_list == "pfx-list"

    def test_network_filters_optional_fields(self):
        """Test network filters with no fields set."""
        nf = BgpNetworkFilters()
        assert nf.distribute_list is None
        assert nf.prefix_list is None

    def test_network_filters_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            BgpNetworkFilters(distribute_list="test", unknown="fail")
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestBgpRouteMaps:
    """Test BGP route maps nested model."""

    def test_valid_route_maps(self):
        """Test valid route maps with both fields."""
        rm = BgpRouteMaps(inbound="in-map", outbound="out-map")
        assert rm.inbound == "in-map"
        assert rm.outbound == "out-map"

    def test_route_maps_optional_fields(self):
        """Test route maps with no fields set."""
        rm = BgpRouteMaps()
        assert rm.inbound is None
        assert rm.outbound is None

    def test_route_maps_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            BgpRouteMaps(inbound="test", unknown="fail")
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestBgpConditionalAdvertisementCondition:
    """Test BGP conditional advertisement condition nested model."""

    def test_valid_condition(self):
        """Test valid condition with advertise_map."""
        cond = BgpConditionalAdvertisementCondition(advertise_map="my-adv-map")
        assert cond.advertise_map == "my-adv-map"

    def test_condition_optional_fields(self):
        """Test condition with no fields set."""
        cond = BgpConditionalAdvertisementCondition()
        assert cond.advertise_map is None

    def test_condition_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            BgpConditionalAdvertisementCondition(advertise_map="test", unknown="fail")
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestBgpConditionalAdvertisement:
    """Test BGP conditional advertisement nested model."""

    def test_valid_with_exist(self):
        """Test valid conditional advertisement with exist condition."""
        ca = BgpConditionalAdvertisement(
            exist=BgpConditionalAdvertisementCondition(advertise_map="exist-map")
        )
        assert ca.exist.advertise_map == "exist-map"
        assert ca.non_exist is None

    def test_valid_with_non_exist(self):
        """Test valid conditional advertisement with non_exist condition."""
        ca = BgpConditionalAdvertisement(
            non_exist=BgpConditionalAdvertisementCondition(advertise_map="non-exist-map")
        )
        assert ca.non_exist.advertise_map == "non-exist-map"
        assert ca.exist is None

    def test_valid_with_both(self):
        """Test valid conditional advertisement with both conditions."""
        ca = BgpConditionalAdvertisement(
            exist=BgpConditionalAdvertisementCondition(advertise_map="exist-map"),
            non_exist=BgpConditionalAdvertisementCondition(advertise_map="non-exist-map"),
        )
        assert ca.exist.advertise_map == "exist-map"
        assert ca.non_exist.advertise_map == "non-exist-map"

    def test_optional_fields(self):
        """Test conditional advertisement with no fields set."""
        ca = BgpConditionalAdvertisement()
        assert ca.exist is None
        assert ca.non_exist is None


class TestBgpFilter:
    """Test BGP filter nested model."""

    def test_valid_minimal(self):
        """Test valid filter with minimal fields."""
        f = BgpFilter()
        assert f.filter_list is None
        assert f.inbound_network_filters is None
        assert f.outbound_network_filters is None
        assert f.route_maps is None
        assert f.conditional_advertisement is None
        assert f.unsuppress_map is None

    def test_valid_all_fields(self):
        """Test valid filter with all fields populated."""
        f = BgpFilter(
            filter_list=BgpFilterList(inbound="in-fl", outbound="out-fl"),
            inbound_network_filters=BgpNetworkFilters(distribute_list="dist"),
            outbound_network_filters=BgpNetworkFilters(prefix_list="pfx"),
            route_maps=BgpRouteMaps(inbound="in-rm", outbound="out-rm"),
            conditional_advertisement=BgpConditionalAdvertisement(
                exist=BgpConditionalAdvertisementCondition(advertise_map="adv")
            ),
            unsuppress_map="unsupp-map",
        )
        assert f.filter_list.inbound == "in-fl"
        assert f.inbound_network_filters.distribute_list == "dist"
        assert f.outbound_network_filters.prefix_list == "pfx"
        assert f.route_maps.inbound == "in-rm"
        assert f.conditional_advertisement.exist.advertise_map == "adv"
        assert f.unsuppress_map == "unsupp-map"

    def test_filter_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            BgpFilter(unknown="fail")
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestBgpFilteringProfileMulticast:
    """Test BGP filtering profile multicast model (oneOf: inherit or filter fields)."""

    def test_valid_with_inherit_only(self):
        """Test valid multicast with inherit=True alone."""
        mc = BgpFilteringProfileMulticast(inherit=True)
        assert mc.inherit is True
        assert mc.filter_list is None
        assert mc.route_maps is None

    def test_valid_with_filter_fields_only(self):
        """Test valid multicast with filter fields alone."""
        mc = BgpFilteringProfileMulticast(
            filter_list=BgpFilterList(inbound="in-fl"),
            route_maps=BgpRouteMaps(outbound="out-rm"),
        )
        assert mc.inherit is None
        assert mc.filter_list.inbound == "in-fl"
        assert mc.route_maps.outbound == "out-rm"

    def test_inherit_and_filter_fields_mutually_exclusive(self):
        """Test that inherit and filter fields are mutually exclusive."""
        with pytest.raises(ValueError) as exc_info:
            BgpFilteringProfileMulticast(
                inherit=True,
                filter_list=BgpFilterList(inbound="in-fl"),
            )
        assert "'inherit' and filter fields are mutually exclusive" in str(exc_info.value)

    def test_inherit_and_route_maps_mutually_exclusive(self):
        """Test that inherit and route_maps are mutually exclusive."""
        with pytest.raises(ValueError) as exc_info:
            BgpFilteringProfileMulticast(
                inherit=True,
                route_maps=BgpRouteMaps(inbound="in-rm"),
            )
        assert "'inherit' and filter fields are mutually exclusive" in str(exc_info.value)

    def test_inherit_and_unsuppress_map_mutually_exclusive(self):
        """Test that inherit and unsuppress_map are mutually exclusive."""
        with pytest.raises(ValueError) as exc_info:
            BgpFilteringProfileMulticast(
                inherit=True,
                unsuppress_map="unsupp-map",
            )
        assert "'inherit' and filter fields are mutually exclusive" in str(exc_info.value)

    def test_inherit_and_conditional_advertisement_mutually_exclusive(self):
        """Test that inherit and conditional_advertisement are mutually exclusive."""
        with pytest.raises(ValueError) as exc_info:
            BgpFilteringProfileMulticast(
                inherit=True,
                conditional_advertisement=BgpConditionalAdvertisement(
                    exist=BgpConditionalAdvertisementCondition(advertise_map="adv")
                ),
            )
        assert "'inherit' and filter fields are mutually exclusive" in str(exc_info.value)

    def test_neither_set_is_valid(self):
        """Test that neither inherit nor filter fields is valid."""
        mc = BgpFilteringProfileMulticast()
        assert mc.inherit is None
        assert mc.filter_list is None

    def test_multicast_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            BgpFilteringProfileMulticast(inherit=True, unknown="fail")
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestBgpFilteringProfileIpv4:
    """Test BGP filtering profile IPv4 container model."""

    def test_valid_with_unicast_and_multicast(self):
        """Test valid IPv4 with both unicast and multicast."""
        ipv4 = BgpFilteringProfileIpv4(
            unicast=BgpFilter(unsuppress_map="unsupp"),
            multicast=BgpFilteringProfileMulticast(inherit=True),
        )
        assert ipv4.unicast.unsuppress_map == "unsupp"
        assert ipv4.multicast.inherit is True

    def test_optional_fields(self):
        """Test IPv4 with no fields set."""
        ipv4 = BgpFilteringProfileIpv4()
        assert ipv4.unicast is None
        assert ipv4.multicast is None


class TestBgpFilteringProfileBaseModel:
    """Test BGP Filtering Profile base model validation."""

    def test_valid_minimal_fields(self):
        """Test valid model with only required fields."""
        model = BgpFilteringProfileBaseModel(name="test-fp", folder="Test Folder")
        assert model.name == "test-fp"
        assert model.folder == "Test Folder"
        assert model.ipv4 is None

    def test_valid_all_fields(self):
        """Test valid model with all fields populated."""
        model = BgpFilteringProfileBaseModel(
            name="test-fp",
            folder="Test Folder",
            ipv4=BgpFilteringProfileIpv4(
                unicast=BgpFilter(
                    filter_list=BgpFilterList(inbound="in-fl"),
                    route_maps=BgpRouteMaps(outbound="out-rm"),
                ),
                multicast=BgpFilteringProfileMulticast(inherit=True),
            ),
        )
        assert model.name == "test-fp"
        assert model.ipv4.unicast.filter_list.inbound == "in-fl"
        assert model.ipv4.unicast.route_maps.outbound == "out-rm"
        assert model.ipv4.multicast.inherit is True

    def test_missing_name_raises_error(self):
        """Test that missing name field raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            BgpFilteringProfileBaseModel(folder="Test Folder")
        assert "name" in str(exc_info.value)

    def test_container_folder(self):
        """Test model with folder container."""
        model = BgpFilteringProfileBaseModel(name="test", folder="MyFolder")
        assert model.folder == "MyFolder"
        assert model.snippet is None
        assert model.device is None

    def test_container_snippet(self):
        """Test model with snippet container."""
        model = BgpFilteringProfileBaseModel(name="test", snippet="MySnippet")
        assert model.snippet == "MySnippet"
        assert model.folder is None

    def test_container_device(self):
        """Test model with device container."""
        model = BgpFilteringProfileBaseModel(name="test", device="MyDevice")
        assert model.device == "MyDevice"
        assert model.folder is None

    def test_container_max_length(self):
        """Test container field max_length validation."""
        model = BgpFilteringProfileBaseModel(name="test", folder="A" * 64)
        assert len(model.folder) == 64

        with pytest.raises(ValidationError):
            BgpFilteringProfileBaseModel(name="test", folder="A" * 65)

    def test_container_pattern_validation(self):
        """Test container field pattern validation."""
        model = BgpFilteringProfileBaseModel(name="test", folder="My-Folder_1.0")
        assert model.folder == "My-Folder_1.0"

        with pytest.raises(ValidationError):
            BgpFilteringProfileBaseModel(name="test", folder="Folder@#$")


class TestBgpFilteringProfileCreateModel:
    """Test BGP Filtering Profile create model."""

    def test_valid_create_with_folder(self):
        """Test valid create model with folder container."""
        model = BgpFilteringProfileCreateModel(
            name="test-fp",
            folder="Test Folder",
        )
        assert model.name == "test-fp"
        assert model.folder == "Test Folder"

    def test_valid_create_with_snippet(self):
        """Test valid create model with snippet container."""
        model = BgpFilteringProfileCreateModel(
            name="test-fp",
            snippet="MySnippet",
        )
        assert model.snippet == "MySnippet"

    def test_valid_create_with_device(self):
        """Test valid create model with device container."""
        model = BgpFilteringProfileCreateModel(
            name="test-fp",
            device="MyDevice",
        )
        assert model.device == "MyDevice"

    def test_create_no_container_raises_error(self):
        """Test that create without any container raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            BgpFilteringProfileCreateModel(name="test-fp")
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

    def test_create_multiple_containers_raises_error(self):
        """Test that create with multiple containers raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            BgpFilteringProfileCreateModel(
                name="test-fp",
                folder="Test Folder",
                snippet="MySnippet",
            )
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

    def test_create_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on BgpFilteringProfileCreateModel."""
        with pytest.raises(ValidationError) as exc_info:
            BgpFilteringProfileCreateModel(
                name="test",
                folder="Test Folder",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestBgpFilteringProfileUpdateModel:
    """Test BGP Filtering Profile update model."""

    def test_valid_update_model(self):
        """Test valid update model."""
        model = BgpFilteringProfileUpdateModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="updated-fp",
            folder="Test Folder",
        )
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "updated-fp"

    def test_invalid_uuid(self):
        """Test update model with invalid UUID."""
        with pytest.raises(ValidationError):
            BgpFilteringProfileUpdateModel(
                id="not-a-uuid",
                name="test",
                folder="Test Folder",
            )


class TestBgpFilteringProfileResponseModel:
    """Test BGP Filtering Profile response model."""

    def test_valid_response_model(self):
        """Test valid response model."""
        model = BgpFilteringProfileResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="response-fp",
            folder="Test Folder",
        )
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "response-fp"

    def test_missing_id_raises_error(self):
        """Test that missing id field raises ValidationError."""
        with pytest.raises(ValidationError):
            BgpFilteringProfileResponseModel(
                name="test",
                folder="Test Folder",
            )


class TestExtraFieldsBgpFilteringProfile:
    """Tests for extra field handling on BGP Filtering Profile models."""

    def test_base_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on BgpFilteringProfileBaseModel."""
        with pytest.raises(ValidationError) as exc_info:
            BgpFilteringProfileBaseModel(
                name="test",
                folder="Test Folder",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_update_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on BgpFilteringProfileUpdateModel."""
        with pytest.raises(ValidationError) as exc_info:
            BgpFilteringProfileUpdateModel(
                id="123e4567-e89b-12d3-a456-426655440000",
                name="test",
                folder="Test Folder",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_response_model_extra_fields_ignored(self):
        """Test that extra fields are silently ignored on BgpFilteringProfileResponseModel."""
        model = BgpFilteringProfileResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test",
            folder="Test Folder",
            unknown_field="should_be_ignored",
        )
        assert not hasattr(model, "unknown_field")
