# tests/scm/models/deployment/test_bgp_routing_models.py

import pytest
from pydantic import ValidationError

from scm.models.deployment.bgp_routing import (
    BackboneRoutingEnum,
    BGPRoutingBaseModel,
    BGPRoutingCreateModel,
    BGPRoutingResponseModel,
    BGPRoutingUpdateModel,
    DefaultRoutingModel,
    HotPotatoRoutingModel,
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
        model = DefaultRoutingModel()
        assert model.default == {}

    def test_custom_default(self):
        """Test creating a DefaultRoutingModel with custom values."""
        model = DefaultRoutingModel(default={"some_setting": "value"})
        assert model.default == {"some_setting": "value"}

    def test_model_dict_output(self):
        """Test model dict output format."""
        model = DefaultRoutingModel()
        model_dict = model.model_dump()
        assert "default" in model_dict
        assert model_dict["default"] == {}


class TestHotPotatoRoutingModel:
    """Tests for the HotPotatoRoutingModel class."""

    def test_default_creation(self):
        """Test creating a HotPotatoRoutingModel with default values."""
        model = HotPotatoRoutingModel()
        assert model.hot_potato_routing == {}

    def test_custom_values(self):
        """Test creating a HotPotatoRoutingModel with custom values."""
        model = HotPotatoRoutingModel(hot_potato_routing={"some_setting": "value"})
        assert model.hot_potato_routing == {"some_setting": "value"}

    def test_model_dict_output(self):
        """Test model dict output format."""
        model = HotPotatoRoutingModel()
        model_dict = model.model_dump()
        assert "hot_potato_routing" in model_dict
        assert model_dict["hot_potato_routing"] == {}


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
            "routing_preference": DefaultRoutingModel(),
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
        model = BGPRoutingBaseModel(routing_preference=DefaultRoutingModel())
        assert isinstance(model.routing_preference, DefaultRoutingModel)
        assert model.routing_preference.default == {}

    def test_with_hot_potato_routing(self):
        """Test creating a model with hot potato routing preference."""
        model = BGPRoutingBaseModel(routing_preference=HotPotatoRoutingModel())
        assert isinstance(model.routing_preference, HotPotatoRoutingModel)
        assert model.routing_preference.hot_potato_routing == {}

    def test_serialize_default_routing(self):
        """Test serializing default routing preference."""
        model = BGPRoutingBaseModel(routing_preference=DefaultRoutingModel())
        serialized = model.serialize_routing_preference(model.routing_preference)
        assert serialized == {"default": {}}

    def test_serialize_hot_potato_routing(self):
        """Test serializing hot potato routing preference."""
        model = BGPRoutingBaseModel(routing_preference=HotPotatoRoutingModel())
        serialized = model.serialize_routing_preference(model.routing_preference)
        assert serialized == {"hot_potato_routing": {}}

    def test_serialize_none_routing(self):
        """Test serializing None routing preference."""
        model = BGPRoutingBaseModel(routing_preference=None)
        serialized = model.serialize_routing_preference(model.routing_preference)
        assert serialized is None

    def test_serialize_unknown_routing_type(self):
        """Test serializing an unknown routing preference type."""
        # Create a test object - note this shouldn't be possible in real usage
        # because of validation, but we're testing the edge case
        model = BGPRoutingBaseModel()
        # This is to test the else branch in the serialize_routing_preference method
        # that would handle unexpected types by returning None
        result = model.serialize_routing_preference("invalid_type")
        assert result is None

    def test_outbound_routes_string_to_list(self):
        """Test that a string value for outbound_routes_for_services is converted to a list."""
        model = BGPRoutingBaseModel(outbound_routes_for_services="10.0.0.0/24")
        assert model.outbound_routes_for_services == ["10.0.0.0/24"]

    def test_outbound_routes_none_to_empty_list(self):
        """Test that None for outbound_routes_for_services is converted to an empty list."""
        model = BGPRoutingBaseModel(outbound_routes_for_services=None)
        assert model.outbound_routes_for_services == []

    def test_outbound_routes_invalid_type(self):
        """Test validation fails for invalid outbound_routes_for_services type."""
        with pytest.raises(ValidationError) as exc_info:
            BGPRoutingBaseModel(outbound_routes_for_services=123)
        assert "outbound_routes_for_services must be a list of strings" in str(exc_info.value)

    def test_field_validator_different_classes(self):
        """Test that validate_outbound_routes behaves differently for different classes."""
        # For base/create model, None should become []
        base_model = BGPRoutingBaseModel(outbound_routes_for_services=None)
        assert base_model.outbound_routes_for_services == []

        create_model = BGPRoutingCreateModel(
            backbone_routing=BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING,
            outbound_routes_for_services=None,
        )
        assert create_model.outbound_routes_for_services == []

        # For update model, None should remain None
        update_model = BGPRoutingUpdateModel(
            backbone_routing=BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING,
            outbound_routes_for_services=None,
        )
        assert update_model.outbound_routes_for_services is None


class TestBGPRoutingCreateModel:
    """Tests for the BGPRoutingCreateModel class."""

    def test_minimal_model_creation(self):
        """Test creating a model with only the required field (backbone_routing)."""
        model = BGPRoutingCreateModel(backbone_routing=BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING)
        assert model.backbone_routing == BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING
        assert model.routing_preference is None
        assert model.accept_route_over_SC is False
        assert model.outbound_routes_for_services == []
        assert model.add_host_route_to_ike_peer is False
        assert model.withdraw_static_route is False

    def test_full_model_creation(self):
        """Test creating a model with all fields."""
        data = {
            "backbone_routing": BackboneRoutingEnum.ASYMMETRIC_ROUTING_ONLY,
            "routing_preference": HotPotatoRoutingModel(),
            "accept_route_over_SC": True,
            "outbound_routes_for_services": ["10.0.0.0/24", "192.168.1.0/24"],
            "add_host_route_to_ike_peer": True,
            "withdraw_static_route": True,
        }
        model = BGPRoutingCreateModel(**data)
        assert model.backbone_routing == BackboneRoutingEnum.ASYMMETRIC_ROUTING_ONLY
        assert isinstance(model.routing_preference, HotPotatoRoutingModel)
        assert model.accept_route_over_SC is True
        assert model.outbound_routes_for_services == ["10.0.0.0/24", "192.168.1.0/24"]
        assert model.add_host_route_to_ike_peer is True
        assert model.withdraw_static_route is True

    def test_missing_required_field(self):
        """Test validation fails when required field is missing."""
        with pytest.raises(ValidationError) as exc_info:
            BGPRoutingCreateModel()
        assert "backbone_routing" in str(exc_info.value)
        assert "Field required" in str(exc_info.value)

    def test_dict_to_routing_preference(self):
        """Test that a dict can be provided for routing_preference."""
        BGPRoutingCreateModel(
            backbone_routing=BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING,
            routing_preference={"default": {}},
        )
        # This should work through Pydantic's validation,
        # but we don't directly test the conversion here as it's handled in the service layer

    def test_model_dump_exclude_none(self):
        """Test model dump with exclude_none option."""
        model = BGPRoutingCreateModel(backbone_routing=BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING)
        model_dict = model.model_dump(exclude_none=True)
        assert "backbone_routing" in model_dict
        assert "routing_preference" not in model_dict

    def test_invalid_routing_preference_type(self):
        """Test validation fails for invalid routing_preference type."""
        with pytest.raises(ValidationError) as exc_info:
            BGPRoutingCreateModel(
                backbone_routing=BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING,
                routing_preference="invalid",
            )
        assert "Input should be a valid dictionary or instance of" in str(exc_info.value)

    def test_validate_routing_preference_type(self):
        """Test the model_validator for routing_preference type validation."""
        # Valid cases - these should pass
        model1 = BGPRoutingCreateModel(
            backbone_routing=BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING,
            routing_preference=DefaultRoutingModel(),
        )
        assert isinstance(model1.routing_preference, DefaultRoutingModel)

        model2 = BGPRoutingCreateModel(
            backbone_routing=BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING,
            routing_preference=HotPotatoRoutingModel(),
        )
        assert isinstance(model2.routing_preference, HotPotatoRoutingModel)

    def test_validate_routing_preference_with_invalid_type(self):
        """Test validator with invalid routing_preference type directly calling the validator."""
        # Create a model with a valid required field
        model = BGPRoutingCreateModel(backbone_routing=BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING)

        # Set an invalid routing_preference attribute directly
        # This bypasses normal Pydantic validation to test the explicit validator
        object.__setattr__(model, "routing_preference", "invalid_string_value")

        # Now calling the validator method directly should trigger the ValueError
        with pytest.raises(ValueError) as exc_info:
            model.validate_routing_preference_type()

        # Verify error message matches exactly what's in the code
        assert (
            str(exc_info.value)
            == "routing_preference must be either DefaultRoutingModel or HotPotatoRoutingModel"
        )


class TestBGPRoutingUpdateModel:
    """Tests for the BGPRoutingUpdateModel class."""

    def test_empty_model_creation(self):
        """Test that creating an empty model raises an error."""
        with pytest.raises(ValidationError) as exc_info:
            BGPRoutingUpdateModel().validate_update_model()
        assert "At least one field must be specified for update" in str(exc_info.value)

    def test_single_field_update(self):
        """Test updating a single field."""
        model = BGPRoutingUpdateModel(backbone_routing=BackboneRoutingEnum.ASYMMETRIC_ROUTING_ONLY)
        assert model.backbone_routing == BackboneRoutingEnum.ASYMMETRIC_ROUTING_ONLY
        assert model.routing_preference is None
        assert model.accept_route_over_SC is None
        assert model.outbound_routes_for_services is None
        assert model.add_host_route_to_ike_peer is None
        assert model.withdraw_static_route is None

    def test_multiple_fields_update(self):
        """Test updating multiple fields."""
        data = {
            "backbone_routing": BackboneRoutingEnum.ASYMMETRIC_ROUTING_WITH_LOAD_SHARE,
            "accept_route_over_SC": True,
            "outbound_routes_for_services": ["10.0.0.0/24"],
        }
        model = BGPRoutingUpdateModel(**data)
        assert model.backbone_routing == BackboneRoutingEnum.ASYMMETRIC_ROUTING_WITH_LOAD_SHARE
        assert model.accept_route_over_SC is True
        assert model.outbound_routes_for_services == ["10.0.0.0/24"]
        assert model.routing_preference is None
        assert model.add_host_route_to_ike_peer is None
        assert model.withdraw_static_route is None

    def test_full_model_update(self):
        """Test updating all fields."""
        data = {
            "backbone_routing": BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING,
            "routing_preference": DefaultRoutingModel(),
            "accept_route_over_SC": False,
            "outbound_routes_for_services": ["192.168.1.0/24"],
            "add_host_route_to_ike_peer": True,
            "withdraw_static_route": True,
        }
        model = BGPRoutingUpdateModel(**data)
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
        # The error message is different but the validation still fails for invalid type
        assert "Input should be a valid dictionary or instance of" in str(exc_info.value)

    def test_validate_update_model_with_invalid_routing_preference(self):
        """Test the validator with an invalid routing_preference type that bypasses initial validation."""
        # Create a model with a valid field to pass the "at least one field" check
        model = BGPRoutingUpdateModel(backbone_routing=BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING)
        # Mock the routing_preference with an invalid type (simulating a scenario where it bypassed initial validation)
        # In real usage, Pydantic would prevent this, but we want to test the validator
        object.__setattr__(model, "routing_preference", "invalid_type")

        # This should now fail in validate_update_model when checking the type
        with pytest.raises(ValueError) as exc_info:
            BGPRoutingUpdateModel.validate_update_model(model)

        assert (
            "routing_preference must be either DefaultRoutingModel or HotPotatoRoutingModel"
            in str(exc_info.value)
        )

    def test_outbound_routes_handling(self):
        """Test handling of outbound_routes_for_services in update model."""
        # None should remain None for updates (not converted to empty list)
        model = BGPRoutingUpdateModel(
            backbone_routing=BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING,
            outbound_routes_for_services=None,
        )
        assert model.outbound_routes_for_services is None

        # String should be converted to list
        model = BGPRoutingUpdateModel(
            backbone_routing=BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING,
            outbound_routes_for_services="10.0.0.0/24",
        )
        assert model.outbound_routes_for_services == ["10.0.0.0/24"]

        # Invalid type should fail validation
        with pytest.raises(ValidationError) as exc_info:
            BGPRoutingUpdateModel(
                backbone_routing=BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING,
                outbound_routes_for_services=123,
            )
        assert "outbound_routes_for_services must be a list of strings" in str(exc_info.value)

    def test_model_dump_exclude_none(self):
        """Test model dump with exclude_none option."""
        model = BGPRoutingUpdateModel(backbone_routing=BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING)
        model_dict = model.model_dump(exclude_none=True)
        assert "backbone_routing" in model_dict
        assert "routing_preference" not in model_dict
        assert "accept_route_over_SC" not in model_dict

    def test_update_with_default_routing(self):
        """Test update with default routing preference."""
        model = BGPRoutingUpdateModel(
            backbone_routing=BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING,
            routing_preference=DefaultRoutingModel(),
        )
        assert isinstance(model.routing_preference, DefaultRoutingModel)


class TestBGPRoutingResponseModel:
    """Tests for the BGPRoutingResponseModel class."""

    def test_valid_response(self):
        """Test creating a valid response model."""
        data = {
            "routing_preference": DefaultRoutingModel(),
            "backbone_routing": BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING,
            "accept_route_over_SC": True,
            "outbound_routes_for_services": ["10.0.0.0/24", "192.168.1.0/24"],
            "add_host_route_to_ike_peer": False,
            "withdraw_static_route": True,
        }
        model = BGPRoutingResponseModel(**data)
        assert isinstance(model.routing_preference, DefaultRoutingModel)
        assert model.backbone_routing == BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING
        assert model.accept_route_over_SC is True
        assert model.outbound_routes_for_services == ["10.0.0.0/24", "192.168.1.0/24"]
        assert model.add_host_route_to_ike_peer is False
        assert model.withdraw_static_route is True

    def test_missing_required_fields(self):
        """Test validation fails when required fields are missing."""
        with pytest.raises(ValidationError) as exc_info:
            BGPRoutingResponseModel()
        assert "Field required" in str(exc_info.value)
        assert "routing_preference" in str(exc_info.value)
        assert "backbone_routing" in str(exc_info.value)
        assert "accept_route_over_SC" in str(exc_info.value)
        assert "outbound_routes_for_services" in str(exc_info.value)
        assert "add_host_route_to_ike_peer" in str(exc_info.value)
        assert "withdraw_static_route" in str(exc_info.value)

    def test_serialize_default_routing(self):
        """Test serializing default routing preference in response model."""
        data = {
            "routing_preference": DefaultRoutingModel(),
            "backbone_routing": BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING,
            "accept_route_over_SC": True,
            "outbound_routes_for_services": [],
            "add_host_route_to_ike_peer": False,
            "withdraw_static_route": True,
        }
        model = BGPRoutingResponseModel(**data)
        # Response model inherits serializer from base model
        serialized = model.serialize_routing_preference(model.routing_preference)
        assert serialized == {"default": {}}

    def test_serialize_hot_potato_routing(self):
        """Test serializing hot potato routing preference in response model."""
        data = {
            "routing_preference": HotPotatoRoutingModel(),
            "backbone_routing": BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING,
            "accept_route_over_SC": True,
            "outbound_routes_for_services": [],
            "add_host_route_to_ike_peer": False,
            "withdraw_static_route": True,
        }
        model = BGPRoutingResponseModel(**data)
        # Response model inherits serializer from base model
        serialized = model.serialize_routing_preference(model.routing_preference)
        assert serialized == {"hot_potato_routing": {}}

    def test_model_dump(self):
        """Test model dumping to dictionary."""
        data = {
            "routing_preference": DefaultRoutingModel(),
            "backbone_routing": BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING,
            "accept_route_over_SC": True,
            "outbound_routes_for_services": ["10.0.0.0/24"],
            "add_host_route_to_ike_peer": False,
            "withdraw_static_route": True,
        }
        model = BGPRoutingResponseModel(**data)
        model_dict = model.model_dump()
        assert model_dict["backbone_routing"] == BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING
        assert model_dict["accept_route_over_SC"] is True
        assert model_dict["outbound_routes_for_services"] == ["10.0.0.0/24"]

    def test_with_hot_potato_routing(self):
        """Test response model with hot potato routing."""
        data = {
            "routing_preference": HotPotatoRoutingModel(),
            "backbone_routing": BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING,
            "accept_route_over_SC": True,
            "outbound_routes_for_services": [],
            "add_host_route_to_ike_peer": False,
            "withdraw_static_route": True,
        }
        model = BGPRoutingResponseModel(**data)
        assert isinstance(model.routing_preference, HotPotatoRoutingModel)
        assert model.routing_preference.hot_potato_routing == {}
