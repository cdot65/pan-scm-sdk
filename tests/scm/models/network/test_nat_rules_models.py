# tests/scm/models/security/test_nat_rules.py

from uuid import UUID

# External libraries
import pytest
from pydantic import ValidationError

# Local SDK imports
from scm.models.network.nat_rules import (
    NatRuleCreateModel,
    NatRuleUpdateModel,
    NatRuleResponseModel,
    NatRuleMoveModel,
    NatType,
    NatMoveDestination,
    NatRulebase,
    InterfaceAddress,
    SourceTranslation,
    StaticIp,
    DynamicIpAndPort,
    BiDirectional,
)
from tests.factories import (
    NatRuleCreateModelFactory,
    NatRuleUpdateModelFactory,
    NatRuleMoveModelFactory,
    NatRuleCreateApiFactory,
    NatRuleResponseFactory,
    NatRuleMoveApiFactory,
    InterfaceAddressFactory,
    SourceTranslationFactory,
    NatRuleUpdateApiFactory,
)


# -------------------- Test Classes for Pydantic Models --------------------


class TestNatRuleCreateModel:
    """Tests for NatRuleCreateModel validation."""

    def test_nat_rule_create_model_valid(self):
        """Test validation with valid data."""
        data = NatRuleCreateModelFactory.build_valid()
        model = NatRuleCreateModel(**data)
        assert model.name == data["name"]
        assert model.folder == data["folder"]
        assert model.from_ == data["from_"]
        assert model.to_ == data["to_"]
        assert model.source == data["source"]
        assert model.destination == data["destination"]

    def test_nat_rule_create_model_invalid_name(self):
        """Test validation when an invalid name is provided."""
        data = NatRuleCreateModelFactory.build_with_invalid_name()
        with pytest.raises(ValidationError) as exc_info:
            NatRuleCreateModel(**data)
        assert "name\n  String should match pattern" in str(exc_info.value)

    def test_nat_rule_create_model_duplicate_items(self):
        """Test validation when lists contain duplicate items."""
        data = NatRuleCreateModelFactory.build_with_duplicate_items()
        with pytest.raises(ValidationError) as exc_info:
            NatRuleCreateModel(**data)
        assert "List items must be unique" in str(exc_info.value)

    def test_nat_rule_create_model_with_snippet(self):
        """Test creation with snippet container."""
        model = NatRuleCreateApiFactory.with_snippet()
        assert model.snippet == "TestSnippet"
        assert model.folder is None
        assert model.device is None

    def test_nat_rule_create_model_with_device(self):
        """Test creation with device container."""
        model = NatRuleCreateApiFactory.with_device()
        assert model.device == "TestDevice"
        assert model.folder is None
        assert model.snippet is None

    def test_nat_rule_create_model_with_source_translation(self):
        """Test creation with source translation configuration."""
        model = NatRuleCreateApiFactory.with_source_translation()
        assert model.source_translation is not None
        assert isinstance(model.source_translation, SourceTranslation)
        # In the new model structure, translated_address is inside dynamic_ip_and_port
        assert model.source_translation.dynamic_ip_and_port is not None
        assert model.source_translation.dynamic_ip_and_port.translated_address == ["192.168.1.100"]

    def test_nat_rule_create_model_string_to_list_conversion(self):
        """Test that string values are converted to lists for list fields."""
        data = NatRuleCreateModelFactory.build_valid()
        data["source"] = "any"  # Provide string instead of list
        model = NatRuleCreateModel(**data)
        assert isinstance(model.source, list)
        assert model.source == ["any"]

    def test_nat_rule_create_model_invalid_list_type(self):
        """Test validation when invalid type is provided for list fields."""
        data = NatRuleCreateModelFactory.build_valid()
        data["source"] = {"invalid": "type"}
        with pytest.raises(ValidationError) as exc_info:
            NatRuleCreateModel(**data)
        assert "Value must be a list of strings" in str(exc_info.value)

    def test_nat_rule_create_model_no_container(self):
        """Test validation when no container is provided."""
        data = NatRuleCreateModelFactory.build_with_no_container()
        with pytest.raises(ValueError) as exc_info:
            NatRuleCreateModel(**data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_nat_rule_create_model_multiple_containers(self):
        """Test validation when multiple containers are provided."""
        data = NatRuleCreateModelFactory.build_with_multiple_containers()
        with pytest.raises(ValueError) as exc_info:
            NatRuleCreateModel(**data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_nat_rule_create_model_non_string_list_items(self):
        """Test that a list field with non-string items raises a ValueError."""
        data = NatRuleCreateModelFactory.build_valid()
        data["source"] = ["any", 123]  # 123 is not a string
        with pytest.raises(ValueError) as exc_info:
            NatRuleCreateModel(**data)
        assert "All items must be strings" in str(exc_info.value)


class TestNatRuleUpdateModel:
    """Tests for NatRuleUpdateModel validation."""

    def test_nat_rule_update_model_valid(self):
        """Test validation with valid update data."""
        data = NatRuleUpdateModelFactory.build_valid()
        model = NatRuleUpdateModel(**data)
        assert model.id == UUID(data["id"])
        assert model.name == "UpdatedNatRule"
        assert model.source == ["updated-source"]
        assert model.destination == ["updated-dest"]

    def test_nat_rule_update_model_invalid_fields(self):
        """Test validation with multiple invalid fields."""
        data = NatRuleUpdateModelFactory.build_with_invalid_fields()
        with pytest.raises(ValidationError) as exc_info:
            NatRuleUpdateModel(**data)
        error_msg = str(exc_info.value)
        assert "name\n  String should match pattern" in error_msg
        assert "List items must be unique" in error_msg

    def test_nat_rule_update_model_minimal_update(self):
        """Test validation with minimal valid update fields."""
        data = NatRuleUpdateModelFactory.build_minimal_update()
        model = NatRuleUpdateModel(**data)
        assert model.description == "Updated description"

    def test_nat_rule_update_model_with_source_translation(self):
        """Test update with source translation configuration."""
        model = NatRuleUpdateApiFactory.with_source_translation()
        assert model.source_translation is not None
        assert isinstance(model.source_translation, SourceTranslation)
        # In the new model structure, translated_address is inside dynamic_ip_and_port
        assert model.source_translation.dynamic_ip_and_port is not None
        assert model.source_translation.dynamic_ip_and_port.translated_address == ["192.168.1.100"]

    def test_nat_rule_update_model_with_zones_update(self):
        """Test update with modified zones."""
        model = NatRuleUpdateApiFactory.with_zones_update(
            from_zones=["new-trust"], to_zones=["new-untrust"]
        )
        assert model.from_ == ["new-trust"]
        assert model.to_ == ["new-untrust"]


class TestNatRuleMoveModel:
    """Tests for NatRuleMoveModel validation."""

    def test_nat_rule_move_model_valid_before(self):
        """Test validation with valid before move configuration."""
        data = NatRuleMoveModelFactory.build_valid_before()
        model = NatRuleMoveModel(**data)
        assert model.destination == NatMoveDestination.BEFORE
        assert model.destination_rule is not None

    def test_nat_rule_move_model_invalid_destination(self):
        """Test validation with invalid destination."""
        data = NatRuleMoveModelFactory.build_with_invalid_destination()
        with pytest.raises(ValidationError) as exc_info:
            NatRuleMoveModel(**data)
        assert "destination\n  Input should be" in str(exc_info.value)

    def test_nat_rule_move_model_missing_destination_rule(self):
        """Test validation when destination_rule is missing for before/after moves."""
        data = NatRuleMoveModelFactory.build_missing_destination_rule()
        with pytest.raises(ValueError) as exc_info:
            NatRuleMoveModel(**data)
        assert "destination_rule is required when destination is 'before'" in str(
            exc_info.value
        )

    def test_nat_rule_move_model_top_with_destination_rule(self):
        """Test validation when destination_rule is provided for top/bottom moves."""
        model_data = {
            "destination": NatMoveDestination.TOP,
            "rulebase": NatRulebase.PRE,
            "destination_rule": "123e4567-e89b-12d3-a456-426655440000",  # Valid UUID
        }
        with pytest.raises(ValueError) as exc_info:
            NatRuleMoveModel(**model_data)
        assert (
            "destination_rule should not be provided when destination is 'top'"
            in str(exc_info.value)
        )


class TestSourceTranslation:
    """Tests for SourceTranslation validation."""

    def test_source_translation_valid(self):
        """Test validation with valid source translation data."""
        model = SourceTranslationFactory()
        # Check dynamic_ip_and_port attributes in the new structure
        assert model.dynamic_ip_and_port is not None
        assert model.dynamic_ip_and_port.translated_address == ["10.0.0.1"]
        # These are no longer direct attributes of SourceTranslation
        assert model.dynamic_ip is None
        assert model.static_ip is None
        
    def test_source_translation_validation_error(self):
        """Test that providing no translation type raises a validation error."""
        with pytest.raises(ValueError) as exc_info:
            SourceTranslation(
                dynamic_ip_and_port=None,
                dynamic_ip=None,
                static_ip=None
            )
        assert "Exactly one of dynamic_ip_and_port, dynamic_ip, or static_ip must be provided" in str(exc_info.value)

    def test_source_translation_with_bi_directional(self):
        """Test validation with bi-directional translation enabled."""
        model = SourceTranslationFactory.with_bi_directional()
        # In the updated structure, bi_directional is an attribute of static_ip
        assert model.static_ip is not None
        assert model.static_ip.bi_directional == BiDirectional.YES  # Enum value now
        assert model.dynamic_ip_and_port is None
        assert model.dynamic_ip is None
        
    def test_static_ip_bi_directional_validation(self):
        """Test that bi_directional validation works correctly."""
        # Test with YES enum
        static_ip = StaticIp(translated_address="192.168.1.100", bi_directional=BiDirectional.YES)
        assert static_ip.bi_directional == BiDirectional.YES
        
        # Test with NO enum
        static_ip = StaticIp(translated_address="192.168.1.100", bi_directional=BiDirectional.NO)
        assert static_ip.bi_directional == BiDirectional.NO
        
        # Test with string values (should convert to enum)
        static_ip = StaticIp(translated_address="192.168.1.100", bi_directional="yes")
        assert static_ip.bi_directional == BiDirectional.YES
        
        # Test with invalid value
        with pytest.raises(Exception) as exc_info:
            StaticIp(translated_address="192.168.1.100", bi_directional="invalid")
        # Any validation error is fine
        
        # Test with None value
        static_ip = StaticIp(translated_address="192.168.1.100", bi_directional=None)
        assert static_ip.bi_directional is None
        
    def test_static_ip_bi_directional_boolean_conversion(self):
        """Create tests specifically for checking the lines that handle boolean conversion.
        
        This test is a bit unusual because we need to directly test the validator function
        rather than through the model, since Pydantic will validate the types before our
        field validator runs.
        """
        # Directly test the validator function
        from scm.models.network.nat_rules import StaticIp, BiDirectional
        
        # Test with None
        result = StaticIp.convert_boolean_to_enum(None)
        assert result is None
        
        # Test with boolean True
        result = StaticIp.convert_boolean_to_enum(True)
        assert result == BiDirectional.YES
        
        # Test with boolean False
        result = StaticIp.convert_boolean_to_enum(False)
        assert result == BiDirectional.NO
        
        # Test with enum values
        result = StaticIp.convert_boolean_to_enum(BiDirectional.YES)
        assert result == BiDirectional.YES

    def test_source_translation_with_interface(self):
        """Test validation with interface configuration."""
        # Need to update how interface is incorporated into source translation
        interface_data = InterfaceAddressFactory.with_floating_ip()
        
        # Create a dynamic_ip_and_port with interface_address
        dynamic_ip_and_port = {
            "type": "dynamic_ip_and_port",
            "interface_address": interface_data.model_dump()
        }
        
        model = SourceTranslationFactory(
            dynamic_ip_and_port=dynamic_ip_and_port,
            dynamic_ip=None,
            static_ip=None
        )
        
        assert model.dynamic_ip_and_port is not None
        assert model.dynamic_ip_and_port.interface_address is not None
        assert model.dynamic_ip_and_port.interface_address.interface == "ethernet1/1"
        assert model.dynamic_ip_and_port.interface_address.floating_ip == "192.168.1.100"
        
    def test_dynamic_ip_and_port_validation_error(self):
        """Test that providing neither translated_address nor interface_address raises an error."""
        # Create a dynamic_ip_and_port with neither translated_address nor interface_address
        dynamic_ip_and_port = {
            "type": "dynamic_ip_and_port",
            "translated_address": None,
            "interface_address": None
        }
        
        # This should trigger the validation error in line 142
        with pytest.raises(ValueError) as exc_info:
            SourceTranslationFactory(
                dynamic_ip_and_port=dynamic_ip_and_port,
                dynamic_ip=None,
                static_ip=None
            )
        
        assert "Either translated_address or interface_address must be provided, but not both" in str(exc_info.value)


class TestNatRuleResponseModel:
    """Tests for NatRuleResponseModel validation."""

    def test_nat_rule_response_model_valid(self):
        """Test validation with valid response data."""
        data = NatRuleResponseFactory().model_dump()
        model = NatRuleResponseModel(**data)
        assert isinstance(model.id, UUID)
        assert model.name.startswith("nat_rule_")
        assert model.nat_type == NatType.ipv4

    def test_nat_rule_response_model_from_request(self):
        """Test creation of response model from request data."""
        request_data = NatRuleCreateModelFactory.build_valid()
        request_model = NatRuleCreateModel(**request_data)
        response_data = NatRuleResponseFactory.from_request(request_model)
        model = NatRuleResponseModel(**response_data.model_dump())
        assert isinstance(model.id, UUID)
        assert model.name == request_model.name
        assert model.from_ == request_model.from_
        assert model.to_ == request_model.to_

    def test_nat_rule_response_model_with_source_translation(self):
        """Test response model with source translation."""
        data = NatRuleResponseFactory.with_source_translation()
        model = NatRuleResponseModel(**data.model_dump())
        assert model.source_translation is not None
        assert isinstance(model.source_translation, SourceTranslation)
        # In the new model structure, translated_address is inside dynamic_ip_and_port
        assert model.source_translation.dynamic_ip_and_port is not None
        assert model.source_translation.dynamic_ip_and_port.translated_address == ["192.168.1.100"]
        
    def test_nat_rule_custom_tag_accepted(self):
        """Test that using custom tags is now allowed."""
        data = NatRuleResponseFactory().model_dump()
        
        # Test with custom tags
        data["tag"] = ["custom-tag", "another_tag"]
        model = NatRuleResponseModel(**data)
        
        # Verify the custom tags are accepted
        assert "custom-tag" in model.tag
        assert "another_tag" in model.tag

        # Test invalid tags
        invalid_tags = ["", " ", "tag with spaces", "tag@with!symbols"]
        for invalid_tag in invalid_tags:
            data["tag"] = [invalid_tag]
            with pytest.raises(ValueError):
                NatRuleResponseModel(**data)

    def test_nat64_dns_rewrite_compatibility(self):
        """Test that using DNS rewrite with NAT64 raises a validation error."""
        # Create a NAT64 rule with DNS rewrite to trigger the validation error
        data = NatRuleResponseFactory().model_dump()
        data["nat_type"] = NatType.nat64
        data["destination_translation"] = {
            "translated_address": "2001:db8::1",
            "dns_rewrite": {
                "direction": "forward"
            }
        }
        
        with pytest.raises(ValueError) as exc_info:
            NatRuleResponseModel(**data)
        
        assert "DNS rewrite is not available with NAT64 rules" in str(exc_info.value)
        
    def test_bidirectional_nat_destination_translation_incompatibility(self):
        """Test that bi-directional static NAT with destination translation raises an error."""
        # Create a rule with both bi-directional static NAT and destination translation
        data = NatRuleResponseFactory().model_dump()
        
        # Add static IP with bi-directional enabled
        data["source_translation"] = {
            "static_ip": {
                "translated_address": "192.168.1.100",
                "bi_directional": BiDirectional.YES
            },
            "dynamic_ip": None,
            "dynamic_ip_and_port": None
        }
        
        # Add destination translation
        data["destination_translation"] = {
            "translated_address": "10.10.10.10"
        }
        
        with pytest.raises(ValueError) as exc_info:
            NatRuleResponseModel(**data)
        
        assert "Bi-directional static NAT cannot be used with destination translation in the same rule" in str(exc_info.value)


#
# class TestNatRuleBaseModel:
#     """Tests for NatRuleBaseModel validation."""
#
#     def test_ensure_list_of_strings_with_non_string_items(self):
#         """Test validation when list contains non-string items."""
#         data = NatRuleCreateModelFactory.build_valid()
#         data["tag"] = ["valid", 123, "also-valid"]  # Include a non-string item
#         with pytest.raises(ValueError) as exc_info:
#             NatRuleCreateModelFactory(**data)
#         assert "All items must be strings" in str(exc_info.value)
#

# -------------------- End of Test Classes --------------------
