# tests/scm/models/deployment/test_bgp_routing_models.py

"""Tests for BGP routing deployment models."""

from pydantic import ValidationError
import pytest

from scm.models.deployment.bgp_routing import (
    BackboneRoutingEnum,
    BGPRoutingBaseModel,
    BGPRoutingCreateModel,
    BGPRoutingResponseModel,
    BGPRoutingUpdateModel,
    DefaultRoutingModel,
    HotPotatoRoutingModel,
)
from tests.factories.deployment.bgp_routing import (
    BGPRoutingCreateModelFactory,
    BGPRoutingResponseModelFactory,
    BGPRoutingUpdateModelFactory,
    DefaultRoutingModelFactory,
    HotPotatoRoutingModelFactory,
)


class TestBackboneRoutingEnum:
    """Tests for the BackboneRoutingEnum class."""

    def test_enum_values(self):
        """Test that the enum has the expected values."""
        assert BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING == "no-asymmetric-routing"
        assert BackboneRoutingEnum.ASYMMETRIC_ROUTING_ONLY == "asymmetric-routing-only"
        assert (
            BackboneRoutingEnum.ASYMMETRIC_ROUTING_WITH_LOAD_SHARE
            == "asymmetric-routing-with-load-share"
        )


class TestDefaultRoutingModel:
    """Tests for the DefaultRoutingModel class."""

    def test_default_creation(self):
        """Test creating a DefaultRoutingModel with default values."""
        model_data = DefaultRoutingModelFactory()
        model = DefaultRoutingModel(**model_data.model_dump())
        assert model.default == {}

    def test_custom_default(self):
        """Test creating a DefaultRoutingModel with custom values."""
        model_data = DefaultRoutingModelFactory(default={"some_setting": "value"})
        model = DefaultRoutingModel(**model_data.model_dump())
        assert model.default == {"some_setting": "value"}

    def test_model_dict_output(self):
        """Test model dict output format."""
        model_data = DefaultRoutingModelFactory()
        model = DefaultRoutingModel(**model_data.model_dump())
        model_dict = model.model_dump()
        assert "default" in model_dict
        assert model_dict["default"] == {}

    def test_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            DefaultRoutingModel(default={}, extra_field="value")
        assert "extra_field" in str(exc_info.value)


class TestHotPotatoRoutingModel:
    """Tests for the HotPotatoRoutingModel class."""

    def test_default_creation(self):
        """Test creating a HotPotatoRoutingModel with default values."""
        model_data = HotPotatoRoutingModelFactory()
        model = HotPotatoRoutingModel(**model_data.model_dump())
        assert model.hot_potato_routing == {}

    def test_custom_values(self):
        """Test creating a HotPotatoRoutingModel with custom values."""
        model_data = HotPotatoRoutingModelFactory(hot_potato_routing={"some_setting": "value"})
        model = HotPotatoRoutingModel(**model_data.model_dump())
        assert model.hot_potato_routing == {"some_setting": "value"}

    def test_model_dict_output(self):
        """Test model dict output format."""
        model_data = HotPotatoRoutingModelFactory()
        model = HotPotatoRoutingModel(**model_data.model_dump())
        model_dict = model.model_dump()
        assert "hot_potato_routing" in model_dict
        assert model_dict["hot_potato_routing"] == {}

    def test_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            HotPotatoRoutingModel(hot_potato_routing={}, extra_field="value")
        assert "extra_field" in str(exc_info.value)


class TestBGPRoutingBaseModel:
    """Tests for the BGPRoutingBaseModel class."""

    def test_empty_model_creation(self):
        """Test creating a model with no fields."""
        model = BGPRoutingBaseModel()
        assert model.routing_preference is None
        assert model.backbone_routing is None
        assert model.accept_route_over_SC is None
        assert model.outbound_routes_for_services is None
        assert model.add_host_route_to_ike_peer is None
        assert model.withdraw_static_route is None

    def test_full_model_creation(self):
        """Test creating a model with all fields."""
        data = {
            "routing_preference": DefaultRoutingModelFactory(),
            "backbone_routing": BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING,
            "accept_route_over_SC": True,
            "outbound_routes_for_services": ["10.0.0.0/24", "192.168.1.0/24"],
            "add_host_route_to_ike_peer": True,
            "withdraw_static_route": False,
        }
        model = BGPRoutingBaseModel(**data)
        assert isinstance(model.routing_preference, DefaultRoutingModel)
        assert model.backbone_routing == BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING
        assert model.accept_route_over_SC is True
        assert model.outbound_routes_for_services == ["10.0.0.0/24", "192.168.1.0/24"]
        assert model.add_host_route_to_ike_peer is True
        assert model.withdraw_static_route is False

    def test_with_default_routing(self):
        """Test creating a model with default routing preference."""
        model = BGPRoutingBaseModel(routing_preference=DefaultRoutingModelFactory())
        assert isinstance(model.routing_preference, DefaultRoutingModel)
        assert model.routing_preference.default == {}

    def test_with_hot_potato_routing(self):
        """Test creating a model with hot potato routing preference."""
        model = BGPRoutingBaseModel(routing_preference=HotPotatoRoutingModelFactory())
        assert isinstance(model.routing_preference, HotPotatoRoutingModel)
        assert model.routing_preference.hot_potato_routing == {}

    def test_serialize_default_routing(self):
        """Test serializing default routing preference."""
        model = BGPRoutingBaseModel(routing_preference=DefaultRoutingModelFactory())
        serialized = model.serialize_routing_preference(model.routing_preference)
        assert serialized == {"default": {}}

    def test_serialize_hot_potato_routing(self):
        """Test serializing hot potato routing preference."""
        model = BGPRoutingBaseModel(routing_preference=HotPotatoRoutingModelFactory())
        serialized = model.serialize_routing_preference(model.routing_preference)
        assert serialized == {"hot_potato_routing": {}}

    def test_serialize_none_routing(self):
        """Test serializing None routing preference."""
        model = BGPRoutingBaseModel(routing_preference=None)
        serialized = model.serialize_routing_preference(model.routing_preference)
        assert serialized is None

    def test_serialize_unknown_routing_type(self):
        """Test serializing an unknown routing preference type."""
        model = BGPRoutingBaseModel()
        result = model.serialize_routing_preference("invalid_type")
        assert result is None

    def test_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            BGPRoutingBaseModel(unknown_field="value")
        assert "unknown_field" in str(exc_info.value)


class TestBGPRoutingCreateModel:
    """Tests for BGPRoutingCreateModel (alias for BGPRoutingUpdateModel)."""

    def test_create_model_is_alias(self):
        """Test that BGPRoutingCreateModel is an alias for BGPRoutingUpdateModel."""
        assert BGPRoutingCreateModel is BGPRoutingUpdateModel

    def test_minimal_model_creation(self):
        """Test creating a model with a single field."""
        model = BGPRoutingCreateModel(
            backbone_routing=BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING
        )
        assert model.backbone_routing == BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING

    def test_full_model_creation(self):
        """Test creating a model with all fields."""
        model_data = BGPRoutingCreateModelFactory.build_with_hot_potato_routing(
            backbone_routing=BackboneRoutingEnum.ASYMMETRIC_ROUTING_ONLY,
            accept_route_over_SC=True,
            outbound_routes_for_services=["10.0.0.0/24", "192.168.1.0/24"],
            add_host_route_to_ike_peer=True,
            withdraw_static_route=True,
        )
        model = BGPRoutingCreateModel(**model_data)
        assert model.backbone_routing == BackboneRoutingEnum.ASYMMETRIC_ROUTING_ONLY
        assert isinstance(model.routing_preference, HotPotatoRoutingModel)
        assert model.accept_route_over_SC is True
        assert model.outbound_routes_for_services == ["10.0.0.0/24", "192.168.1.0/24"]
        assert model.add_host_route_to_ike_peer is True
        assert model.withdraw_static_route is True

    def test_empty_model_fails(self):
        """Test that creating an empty model raises an error."""
        with pytest.raises(ValidationError) as exc_info:
            BGPRoutingCreateModel()
        assert "At least one field must be specified for update" in str(exc_info.value)


class TestBGPRoutingUpdateModel:
    """Tests for the BGPRoutingUpdateModel class."""

    def test_empty_model_creation(self):
        """Test that creating an empty model raises an error."""
        with pytest.raises(ValueError) as exc_info:
            model_data = BGPRoutingUpdateModelFactory.build_empty()
            BGPRoutingUpdateModel(**model_data)
        assert "At least one field must be specified for update" in str(exc_info.value)

    def test_single_field_update(self):
        """Test updating a single field."""
        model_data = BGPRoutingUpdateModelFactory.build_partial(
            ["backbone_routing"], backbone_routing=BackboneRoutingEnum.ASYMMETRIC_ROUTING_ONLY
        )
        model = BGPRoutingUpdateModel(**model_data)
        assert model.backbone_routing == BackboneRoutingEnum.ASYMMETRIC_ROUTING_ONLY
        assert model.routing_preference is None
        assert model.accept_route_over_SC is None
        assert model.outbound_routes_for_services is None
        assert model.add_host_route_to_ike_peer is None
        assert model.withdraw_static_route is None

    def test_multiple_fields_update(self):
        """Test updating multiple fields."""
        model_data = BGPRoutingUpdateModelFactory.build_partial(
            ["backbone_routing", "accept_route_over_SC", "outbound_routes_for_services"],
            backbone_routing=BackboneRoutingEnum.ASYMMETRIC_ROUTING_WITH_LOAD_SHARE,
            accept_route_over_SC=True,
            outbound_routes_for_services=["10.0.0.0/24"],
        )
        model = BGPRoutingUpdateModel(**model_data)
        assert model.backbone_routing == BackboneRoutingEnum.ASYMMETRIC_ROUTING_WITH_LOAD_SHARE
        assert model.accept_route_over_SC is True
        assert model.outbound_routes_for_services == ["10.0.0.0/24"]
        assert model.routing_preference is None
        assert model.add_host_route_to_ike_peer is None
        assert model.withdraw_static_route is None

    def test_full_model_update(self):
        """Test updating all fields."""
        model_data = BGPRoutingUpdateModelFactory.build_with_default_routing(
            backbone_routing=BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING,
            accept_route_over_SC=False,
            outbound_routes_for_services=["192.168.1.0/24"],
            add_host_route_to_ike_peer=True,
            withdraw_static_route=True,
        )
        model = BGPRoutingUpdateModel(**model_data)
        assert model.backbone_routing == BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING
        assert isinstance(model.routing_preference, DefaultRoutingModel)
        assert model.accept_route_over_SC is False
        assert model.outbound_routes_for_services == ["192.168.1.0/24"]
        assert model.add_host_route_to_ike_peer is True
        assert model.withdraw_static_route is True

    def test_invalid_routing_preference(self):
        """Test validation fails for invalid routing_preference type."""
        with pytest.raises(ValidationError) as exc_info:
            BGPRoutingUpdateModel(routing_preference="invalid")
        assert "Input should be a valid dictionary or instance of" in str(exc_info.value)

    def test_outbound_routes_string_to_list(self):
        """Test that a string value for outbound_routes_for_services is converted to a list."""
        model = BGPRoutingUpdateModel(outbound_routes_for_services="10.0.0.0/24")
        assert model.outbound_routes_for_services == ["10.0.0.0/24"]

    def test_outbound_routes_none_preserved(self):
        """Test that None for outbound_routes_for_services is preserved for partial updates."""
        model = BGPRoutingUpdateModel(
            backbone_routing=BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING,
            outbound_routes_for_services=None,
        )
        assert model.outbound_routes_for_services is None

    def test_outbound_routes_invalid_type(self):
        """Test validation fails for invalid outbound_routes_for_services type."""
        with pytest.raises(ValidationError) as exc_info:
            BGPRoutingUpdateModel(
                backbone_routing=BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING,
                outbound_routes_for_services=123,
            )
        assert "outbound_routes_for_services must be a list of strings" in str(exc_info.value)

    def test_model_dump_exclude_none(self):
        """Test model dump with exclude_none option."""
        model_data = BGPRoutingUpdateModelFactory.build_partial(
            ["backbone_routing"], backbone_routing=BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING
        )
        model = BGPRoutingUpdateModel(**model_data)
        model_dict = model.model_dump(exclude_none=True)
        assert "backbone_routing" in model_dict
        assert "routing_preference" not in model_dict

    def test_update_with_default_routing(self):
        """Test update with default routing preference."""
        model_data = BGPRoutingUpdateModelFactory.build_with_default_routing(
            backbone_routing=BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING
        )
        model = BGPRoutingUpdateModel(**model_data)
        assert isinstance(model.routing_preference, DefaultRoutingModel)


class TestBGPRoutingResponseModel:
    """Tests for the BGPRoutingResponseModel class."""

    def test_valid_response(self):
        """Test creating a valid response model with all fields."""
        model_data = BGPRoutingResponseModelFactory.build_valid(
            routing_preference=DefaultRoutingModel(),
            backbone_routing=BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING,
            accept_route_over_SC=True,
            outbound_routes_for_services=["10.0.0.0/24", "192.168.1.0/24"],
            add_host_route_to_ike_peer=True,
            withdraw_static_route=True,
        )
        model = BGPRoutingResponseModel(**model_data)
        assert isinstance(model.routing_preference, DefaultRoutingModel)
        assert model.backbone_routing == BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING
        assert model.accept_route_over_SC is True
        assert model.outbound_routes_for_services == ["10.0.0.0/24", "192.168.1.0/24"]
        assert model.add_host_route_to_ike_peer is True
        assert model.withdraw_static_route is True

    def test_empty_response_allowed(self):
        """Test that empty response is allowed (all fields optional per OpenAPI spec)."""
        model = BGPRoutingResponseModel()
        assert model.routing_preference is None
        assert model.backbone_routing is None
        assert model.accept_route_over_SC is None
        # outbound_routes_for_services defaults to [] when None
        assert model.outbound_routes_for_services == []
        assert model.add_host_route_to_ike_peer is None
        assert model.withdraw_static_route is None

    def test_partial_response(self):
        """Test creating a response model with only some fields."""
        model = BGPRoutingResponseModel(
            backbone_routing=BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING
        )
        assert model.backbone_routing == BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING
        assert model.routing_preference is None

    def test_outbound_routes_none_to_empty_list(self):
        """Test that None for outbound_routes_for_services is converted to empty list."""
        model = BGPRoutingResponseModel(outbound_routes_for_services=None)
        assert model.outbound_routes_for_services == []

    def test_outbound_routes_string_to_list(self):
        """Test that a string value for outbound_routes_for_services is converted to a list."""
        model = BGPRoutingResponseModel(outbound_routes_for_services="10.0.0.0/24")
        assert model.outbound_routes_for_services == ["10.0.0.0/24"]

    def test_serialize_default_routing(self):
        """Test serializing default routing preference in response model."""
        model_data = BGPRoutingResponseModelFactory.build_valid(
            routing_preference=DefaultRoutingModel(),
            backbone_routing=BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING,
        )
        model = BGPRoutingResponseModel(**model_data)
        serialized = model.serialize_routing_preference(model.routing_preference)
        assert serialized == {"default": {}}

    def test_serialize_hot_potato_routing(self):
        """Test serializing hot potato routing preference in response model."""
        model_data = BGPRoutingResponseModelFactory.build_with_hot_potato_routing(
            backbone_routing=BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING,
        )
        model = BGPRoutingResponseModel(**model_data)
        serialized = model.serialize_routing_preference(model.routing_preference)
        assert serialized == {"hot_potato_routing": {}}

    def test_model_dump(self):
        """Test model dumping to dictionary."""
        model_data = BGPRoutingResponseModelFactory.build_valid(
            routing_preference=DefaultRoutingModel(),
            backbone_routing=BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING,
            accept_route_over_SC=True,
            outbound_routes_for_services=["10.0.0.0/24"],
            add_host_route_to_ike_peer=True,
            withdraw_static_route=True,
        )
        model = BGPRoutingResponseModel(**model_data)
        model_dict = model.model_dump()
        assert model_dict["backbone_routing"] == BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING
        assert model_dict["accept_route_over_SC"] is True
        assert model_dict["outbound_routes_for_services"] == ["10.0.0.0/24"]

    def test_with_hot_potato_routing(self):
        """Test response model with hot potato routing."""
        model_data = BGPRoutingResponseModelFactory.build_with_hot_potato_routing(
            backbone_routing=BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING,
        )
        model = BGPRoutingResponseModel(**model_data)
        assert isinstance(model.routing_preference, HotPotatoRoutingModel)
        assert model.routing_preference.hot_potato_routing == {}
