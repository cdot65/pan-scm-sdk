# tests/scm/models/security/test_decryption_rules_models.py

"""Tests for decryption rule models."""

import uuid
from uuid import UUID

from pydantic import ValidationError

# External libraries
import pytest

# Local SDK imports
from scm.models.security.decryption_rules import (
    DecryptionRuleAction,
    DecryptionRuleCreateModel,
    DecryptionRuleMoveDestination,
    DecryptionRuleMoveModel,
    DecryptionRuleResponseModel,
    DecryptionRuleRulebase,
    DecryptionRuleType,
    DecryptionRuleUpdateModel,
)
from tests.factories.security import (
    DecryptionRuleCreateApiFactory,
    DecryptionRuleCreateModelFactory,
    DecryptionRuleMoveApiFactory,
    DecryptionRuleMoveModelFactory,
    DecryptionRuleResponseFactory,
    DecryptionRuleUpdateModelFactory,
)

# -------------------- Test Classes for Pydantic Models --------------------


class TestDecryptionRuleCreateModel:
    """Tests for DecryptionRuleCreateModel validation."""

    def test_decryption_rule_create_model_valid(self):
        """Test validation with valid data."""
        data = DecryptionRuleCreateModelFactory.build_valid()
        model = DecryptionRuleCreateModel(**data)
        assert model.name == data["name"]
        assert model.folder == data["folder"]
        assert model.action == DecryptionRuleAction.no_decrypt
        assert model.from_ == data["from_"]
        assert model.to_ == data["to_"]
        assert model.source == data["source"]
        assert model.destination == data["destination"]

    def test_decryption_rule_create_model_valid_with_decrypt(self):
        """Test validation with decrypt action."""
        data = DecryptionRuleCreateModelFactory.build_valid()
        data["action"] = "decrypt"
        model = DecryptionRuleCreateModel(**data)
        assert model.action == DecryptionRuleAction.decrypt

    def test_decryption_rule_create_model_invalid_name(self):
        """Test validation when an invalid name is provided."""
        data = DecryptionRuleCreateModelFactory.build_with_invalid_name()
        with pytest.raises(ValidationError) as exc_info:
            DecryptionRuleCreateModel(**data)
        assert "name\n  String should match pattern" in str(exc_info.value)

    def test_decryption_rule_create_model_invalid_action(self):
        """Test validation when an invalid action is provided."""
        data = DecryptionRuleCreateModelFactory.build_with_invalid_action()
        with pytest.raises(ValidationError) as exc_info:
            DecryptionRuleCreateModel(**data)
        assert "action\n  Input should be" in str(exc_info.value)

    def test_decryption_rule_create_model_duplicate_items(self):
        """Test validation when lists contain duplicate items."""
        data = DecryptionRuleCreateModelFactory.build_with_duplicate_items()
        with pytest.raises(ValidationError) as exc_info:
            DecryptionRuleCreateModel(**data)
        assert "List items must be unique" in str(exc_info.value)

    def test_decryption_rule_create_model_with_snippet(self):
        """Test creation with snippet container."""
        model = DecryptionRuleCreateApiFactory.with_snippet()
        assert model.snippet == "TestSnippet"
        assert model.folder is None
        assert model.device is None

    def test_decryption_rule_create_model_with_device(self):
        """Test creation with device container."""
        model = DecryptionRuleCreateApiFactory.with_device()
        assert model.device == "TestDevice"
        assert model.folder is None
        assert model.snippet is None

    def test_decryption_rule_create_model_with_custom_zones(self):
        """Test creation with custom security zones."""
        model = DecryptionRuleCreateApiFactory.with_custom_zones(
            from_zones=["trust"], to_zones=["untrust"]
        )
        assert model.from_ == ["trust"]
        assert model.to_ == ["untrust"]

    def test_decryption_rule_create_model_string_to_list_conversion(self):
        """Test that string values are converted to lists for list fields."""
        data = DecryptionRuleCreateModelFactory.build_valid()
        data["source"] = "any"  # Provide string instead of list
        model = DecryptionRuleCreateModel(**data)
        assert isinstance(model.source, list)
        assert model.source == ["any"]

    def test_decryption_rule_create_model_invalid_list_type(self):
        """Test validation when invalid type is provided for list fields."""
        data = DecryptionRuleCreateModelFactory.build_valid()
        data["source"] = {"invalid": "type"}
        with pytest.raises(ValidationError) as exc_info:
            DecryptionRuleCreateModel(**data)
        assert "Value must be a list of strings" in str(exc_info.value)

    def test_decryption_rule_create_model_no_container(self):
        """Test validation when no container is provided."""
        data = DecryptionRuleCreateModelFactory.build_valid()
        data.pop("folder")  # Remove the container field
        with pytest.raises(ValueError) as exc_info:
            DecryptionRuleCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_decryption_rule_create_model_multiple_containers(self):
        """Test validation when multiple containers are provided."""
        data = DecryptionRuleCreateModelFactory.build_valid()
        data["snippet"] = "TestSnippet"  # Add a second container
        with pytest.raises(ValueError) as exc_info:
            DecryptionRuleCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_decryption_rule_create_model_all_containers(self):
        """Test validation when all containers are provided."""
        data = DecryptionRuleCreateModelFactory.build_valid()
        data["snippet"] = "TestSnippet"
        data["device"] = "TestDevice"
        with pytest.raises(ValueError) as exc_info:
            DecryptionRuleCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_decryption_rule_create_model_with_type_ssl_forward_proxy(self):
        """Test creation with ssl_forward_proxy type."""
        data = DecryptionRuleCreateModelFactory.build_valid()
        data["type"] = {"ssl_forward_proxy": {}}
        model = DecryptionRuleCreateModel(**data)
        assert model.type is not None
        assert model.type.ssl_forward_proxy == {}
        assert model.type.ssl_inbound_inspection is None

    def test_decryption_rule_create_model_with_type_ssl_inbound_inspection(self):
        """Test creation with ssl_inbound_inspection type."""
        data = DecryptionRuleCreateModelFactory.build_valid()
        data["type"] = {"ssl_inbound_inspection": "my-certificate"}
        model = DecryptionRuleCreateModel(**data)
        assert model.type is not None
        assert model.type.ssl_inbound_inspection == "my-certificate"
        assert model.type.ssl_forward_proxy is None

    def test_decryption_rule_create_model_with_profile(self):
        """Test creation with decryption profile."""
        data = DecryptionRuleCreateModelFactory.build_valid()
        data["profile"] = "my-decryption-profile"
        model = DecryptionRuleCreateModel(**data)
        assert model.profile == "my-decryption-profile"

    def test_decryption_rule_create_model_with_log_fields(self):
        """Test creation with log-related fields."""
        data = DecryptionRuleCreateModelFactory.build_valid()
        data["log_fail"] = True
        data["log_success"] = False
        data["log_setting"] = "custom-logging"
        model = DecryptionRuleCreateModel(**data)
        assert model.log_fail is True
        assert model.log_success is False
        assert model.log_setting == "custom-logging"

    def test_decryption_rule_create_model_with_rulebase(self):
        """Test creation with rulebase field."""
        data = DecryptionRuleCreateModelFactory.build_valid()
        data["rulebase"] = "post"
        model = DecryptionRuleCreateModel(**data)
        assert model.rulebase == DecryptionRuleRulebase.POST

    def test_decryption_rule_create_model_with_negate_fields(self):
        """Test creation with negate source and destination."""
        data = DecryptionRuleCreateModelFactory.build_valid()
        data["negate_source"] = True
        data["negate_destination"] = True
        model = DecryptionRuleCreateModel(**data)
        assert model.negate_source is True
        assert model.negate_destination is True


class TestDecryptionRuleUpdateModel:
    """Tests for DecryptionRuleUpdateModel validation."""

    def test_decryption_rule_update_model_valid(self):
        """Test validation with valid update data."""
        data = DecryptionRuleUpdateModelFactory.build_valid()
        model = DecryptionRuleUpdateModel(**data)
        assert model.name == "UpdatedRule"
        assert model.action == DecryptionRuleAction.decrypt
        assert model.source == ["updated-source"]
        assert model.destination == ["updated-dest"]

    def test_decryption_rule_update_model_invalid_fields(self):
        """Test validation with multiple invalid fields."""
        data = DecryptionRuleUpdateModelFactory.build_with_invalid_fields()
        with pytest.raises(ValidationError) as exc_info:
            DecryptionRuleUpdateModel(**data)
        error_msg = str(exc_info.value)
        assert "name\n  String should match pattern" in error_msg
        assert "action\n  Input should be" in error_msg
        assert "List items must be unique" in error_msg

    def test_decryption_rule_update_model_minimal_update(self):
        """Test validation with minimal valid update fields."""
        data = DecryptionRuleUpdateModelFactory.build_minimal_update()
        data["action"] = "no-decrypt"  # action is required by the base model
        model = DecryptionRuleUpdateModel(**data)
        assert model.description == "Updated description"

    def test_decryption_rule_update_model_with_action_update(self):
        """Test update with modified action."""
        model = DecryptionRuleCreateApiFactory.with_post_rulebase(
            action=DecryptionRuleAction.decrypt
        )
        assert model.action == DecryptionRuleAction.decrypt

    def test_decryption_rule_update_model_with_zones_update(self):
        """Test update with modified security zones."""
        model = DecryptionRuleCreateApiFactory.with_post_rulebase(
            from_=["new-trust"],
            to_=["new-untrust"],
        )
        assert model.from_ == ["new-trust"]
        assert model.to_ == ["new-untrust"]

    def test_decryption_rule_update_model_has_uuid(self):
        """Test that update model requires a UUID."""
        data = DecryptionRuleUpdateModelFactory.build_valid()
        model = DecryptionRuleUpdateModel(**data)
        assert isinstance(model.id, UUID)
        assert str(model.id) == "123e4567-e89b-12d3-a456-426655440000"

    def test_decryption_rule_update_model_with_rulebase(self):
        """Test update with rulebase field."""
        data = DecryptionRuleUpdateModelFactory.build_valid()
        data["rulebase"] = "post"
        model = DecryptionRuleUpdateModel(**data)
        assert model.rulebase == DecryptionRuleRulebase.POST


class TestDecryptionRuleMoveModel:
    """Tests for DecryptionRuleMoveModel validation."""

    def test_decryption_rule_move_model_valid_before(self):
        """Test validation with valid before move configuration."""
        data = DecryptionRuleMoveModelFactory.build_valid_before()
        model = DecryptionRuleMoveModel(**data)
        assert model.destination == DecryptionRuleMoveDestination.BEFORE
        assert model.destination_rule is not None

    def test_decryption_rule_move_model_valid_after(self):
        """Test validation with valid after move configuration."""
        dest_rule = str(uuid.uuid4())
        data = {
            "destination": "after",
            "destination_rule": dest_rule,
            "rulebase": "pre",
        }
        model = DecryptionRuleMoveModel(**data)
        assert model.destination == DecryptionRuleMoveDestination.AFTER
        assert model.destination_rule is not None

    def test_decryption_rule_move_model_valid_top(self):
        """Test validation with valid top move configuration."""
        data = {"destination": "top", "rulebase": "pre"}
        model = DecryptionRuleMoveModel(**data)
        assert model.destination == DecryptionRuleMoveDestination.TOP
        assert model.destination_rule is None

    def test_decryption_rule_move_model_valid_bottom(self):
        """Test validation with valid bottom move configuration."""
        data = {"destination": "bottom", "rulebase": "post"}
        model = DecryptionRuleMoveModel(**data)
        assert model.destination == DecryptionRuleMoveDestination.BOTTOM
        assert model.destination_rule is None

    def test_decryption_rule_move_model_invalid_destination(self):
        """Test validation with invalid destination."""
        data = DecryptionRuleMoveModelFactory.build_with_invalid_destination()
        with pytest.raises(ValidationError) as exc_info:
            DecryptionRuleMoveModel(**data)
        assert "destination\n  Input should be" in str(exc_info.value)

    def test_decryption_rule_move_model_missing_destination_rule(self):
        """Test validation when destination_rule is missing for before/after moves."""
        data = DecryptionRuleMoveModelFactory.build_missing_destination_rule()
        with pytest.raises(ValueError) as exc_info:
            DecryptionRuleMoveModel(**data)
        assert "destination_rule is required when destination is 'before'" in str(exc_info.value)

    def test_decryption_rule_move_model_missing_destination_rule_after(self):
        """Test validation when destination_rule is missing for after moves."""
        data = {"destination": "after", "rulebase": "pre"}
        with pytest.raises(ValueError) as exc_info:
            DecryptionRuleMoveModel(**data)
        assert "destination_rule is required when destination is 'after'" in str(exc_info.value)

    def test_decryption_rule_move_model_top_with_destination_rule(self):
        """Test validation when destination_rule is provided for top moves."""
        with pytest.raises(ValidationError) as exc_info:
            DecryptionRuleMoveApiFactory(
                destination=DecryptionRuleMoveDestination.TOP,
                destination_rule="some-rule-id",
            )
        assert "1 validation error for DecryptionRuleMoveModel" in str(exc_info.value)

    def test_decryption_rule_move_model_bottom_with_destination_rule(self):
        """Test validation when destination_rule is provided for bottom moves."""
        with pytest.raises(
            ValueError,
            match="destination_rule should not be provided when destination is 'bottom'",
        ):
            DecryptionRuleMoveModel(
                destination=DecryptionRuleMoveDestination.BOTTOM,
                rulebase=DecryptionRuleRulebase.PRE,
                destination_rule=uuid.uuid4(),
            )


class TestDecryptionRuleResponseModel:
    """Tests for DecryptionRuleResponseModel validation."""

    def test_decryption_rule_response_model_valid(self):
        """Test validation with valid response data."""
        data = DecryptionRuleResponseFactory().model_dump()
        model = DecryptionRuleResponseModel(**data)
        assert isinstance(model.id, UUID)
        assert model.name.startswith("decryption_rule_")
        assert model.folder == "Texas"
        assert model.action == DecryptionRuleAction.no_decrypt

    def test_decryption_rule_response_model_from_request(self):
        """Test creation of response model from request data."""
        request_data = DecryptionRuleCreateModelFactory.build_valid()
        request_model = DecryptionRuleCreateModel(**request_data)
        response_data = DecryptionRuleResponseFactory.from_request(request_model)
        model = DecryptionRuleResponseModel(**response_data.model_dump())
        assert isinstance(model.id, UUID)
        assert model.name == request_model.name
        assert model.folder == request_model.folder
        assert model.action == request_model.action

    def test_decryption_rule_response_model_with_snippet(self):
        """Test response model with snippet container."""
        data = DecryptionRuleResponseFactory.with_snippet()
        model = DecryptionRuleResponseModel(**data.model_dump())
        assert model.snippet == "TestSnippet"
        assert model.folder is None
        assert model.device is None

    def test_decryption_rule_response_model_with_device_string(self):
        """Test response model with device container as string."""
        data = DecryptionRuleResponseFactory.with_device("TestDevice")
        model = DecryptionRuleResponseModel(**data.model_dump())
        assert model.device == "TestDevice"
        assert model.folder is None
        assert model.snippet is None

    def test_decryption_rule_response_model_with_device_empty_dict(self):
        """Test response model with device container as empty dictionary."""
        data = DecryptionRuleResponseFactory.with_empty_dict_device()
        model = DecryptionRuleResponseModel(**data.model_dump())
        assert model.device == {}
        assert model.folder is None
        assert model.snippet is None

    def test_decryption_rule_response_model_device_validation(self):
        """Test that device validation rejects non-empty dictionaries."""
        with pytest.raises(
            ValueError,
            match="If device is a dictionary, it must be empty",
        ):
            DecryptionRuleResponseModel(
                id=uuid.uuid4(),
                name="test_rule",
                action="no-decrypt",
                device={"some_key": "some_value"},
            )

    def test_decryption_rule_response_model_without_action(self):
        """Test response model accepts missing action field (API may omit it)."""
        model = DecryptionRuleResponseModel(
            id=uuid.uuid4(),
            name="test_rule",
            folder="Texas",
        )
        assert model.action is None
        assert model.name == "test_rule"

    def test_decryption_rule_response_model_with_rulebase(self):
        """Test response model with rulebase field."""
        data = DecryptionRuleResponseFactory(rulebase=DecryptionRuleRulebase.POST).model_dump()
        model = DecryptionRuleResponseModel(**data)
        assert model.rulebase == DecryptionRuleRulebase.POST


class TestDecryptionRuleType:
    """Tests for DecryptionRuleType validation."""

    def test_ssl_forward_proxy_valid(self):
        """Test valid ssl_forward_proxy configuration."""
        model = DecryptionRuleType(ssl_forward_proxy={})
        assert model.ssl_forward_proxy == {}
        assert model.ssl_inbound_inspection is None

    def test_ssl_inbound_inspection_valid(self):
        """Test valid ssl_inbound_inspection configuration."""
        model = DecryptionRuleType(ssl_inbound_inspection="my-cert")
        assert model.ssl_inbound_inspection == "my-cert"
        assert model.ssl_forward_proxy is None

    def test_both_set_raises_error(self):
        """Test that setting both types raises ValueError."""
        with pytest.raises(
            ValueError,
            match="Only one of 'ssl_forward_proxy' or 'ssl_inbound_inspection' can be provided.",
        ):
            DecryptionRuleType(ssl_forward_proxy={}, ssl_inbound_inspection="my-cert")

    def test_neither_set_raises_error(self):
        """Test that setting neither type raises ValueError."""
        with pytest.raises(
            ValueError,
            match="Exactly one of 'ssl_forward_proxy' or 'ssl_inbound_inspection' must be provided.",
        ):
            DecryptionRuleType()

    def test_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            DecryptionRuleType(ssl_forward_proxy={}, unknown_field="value")
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestDecryptionRuleBaseModel:
    """Tests for DecryptionRuleBaseModel validators."""

    def test_ensure_list_of_strings_with_non_string_items(self):
        """Test validation when list contains non-string items."""
        data = DecryptionRuleCreateModelFactory.build_valid()
        data["source"] = ["valid", 123, "also-valid"]  # Include a non-string item
        with pytest.raises(ValueError) as exc_info:
            DecryptionRuleCreateModel(**data)
        assert "All items must be strings" in str(exc_info.value)

    def test_ensure_list_of_strings_with_nested_structures(self):
        """Test validation when list contains nested structures."""
        data = DecryptionRuleCreateModelFactory.build_valid()
        data["source"] = ["valid", ["nested"], "invalid"]
        with pytest.raises(ValueError) as exc_info:
            DecryptionRuleCreateModel(**data)
        assert "All items must be strings" in str(exc_info.value)

    def test_ensure_list_of_strings_with_mixed_types(self):
        """Test validation when list contains mixed types."""
        data = DecryptionRuleCreateModelFactory.build_valid()
        data["source"] = ["valid", {"key": "value"}, 123]
        with pytest.raises(ValueError) as exc_info:
            DecryptionRuleCreateModel(**data)
        assert "All items must be strings" in str(exc_info.value)

    def test_ensure_list_of_strings_single_string_conversion(self):
        """Test that a single string is converted to a list."""
        model = DecryptionRuleCreateModel(
            name="test-rule",
            action="no-decrypt",
            source="192.168.1.1",
            folder="Texas",
        )
        assert model.source == ["192.168.1.1"]

    def test_ensure_list_of_strings_invalid_type(self):
        """Test that a non-string, non-list value raises a ValueError."""
        with pytest.raises(ValueError, match="Value must be a list of strings"):
            DecryptionRuleCreateModel(
                name="test-rule",
                action="no-decrypt",
                source=123,
                folder="Texas",
            )

    def test_ensure_list_of_strings_for_tag_field(self):
        """Test string-to-list conversion for tag field."""
        model = DecryptionRuleCreateModel(
            name="test-rule",
            action="no-decrypt",
            tag="single-tag",
            folder="Texas",
        )
        assert model.tag == ["single-tag"]

    def test_ensure_list_of_strings_for_from_field(self):
        """Test string-to-list conversion for from_ field."""
        model = DecryptionRuleCreateModel(
            name="test-rule",
            action="no-decrypt",
            from_="trust",
            folder="Texas",
        )
        assert model.from_ == ["trust"]

    def test_ensure_list_of_strings_for_to_field(self):
        """Test string-to-list conversion for to_ field."""
        model = DecryptionRuleCreateModel(
            name="test-rule",
            action="no-decrypt",
            to_="untrust",
            folder="Texas",
        )
        assert model.to_ == ["untrust"]

    def test_ensure_list_of_strings_for_category(self):
        """Test string-to-list conversion for category field."""
        model = DecryptionRuleCreateModel(
            name="test-rule",
            action="no-decrypt",
            category="social-networking",
            folder="Texas",
        )
        assert model.category == ["social-networking"]

    def test_ensure_list_of_strings_for_service(self):
        """Test string-to-list conversion for service field."""
        model = DecryptionRuleCreateModel(
            name="test-rule",
            action="no-decrypt",
            service="tcp-443",
            folder="Texas",
        )
        assert model.service == ["tcp-443"]

    def test_ensure_list_of_strings_for_source_user(self):
        """Test string-to-list conversion for source_user field."""
        model = DecryptionRuleCreateModel(
            name="test-rule",
            action="no-decrypt",
            source_user="admin",
            folder="Texas",
        )
        assert model.source_user == ["admin"]

    def test_ensure_list_of_strings_for_source_hip(self):
        """Test string-to-list conversion for source_hip field."""
        model = DecryptionRuleCreateModel(
            name="test-rule",
            action="no-decrypt",
            source_hip="my-hip",
            folder="Texas",
        )
        assert model.source_hip == ["my-hip"]

    def test_ensure_list_of_strings_for_destination_hip(self):
        """Test string-to-list conversion for destination_hip field."""
        model = DecryptionRuleCreateModel(
            name="test-rule",
            action="no-decrypt",
            destination_hip="my-hip",
            folder="Texas",
        )
        assert model.destination_hip == ["my-hip"]

    def test_from_alias_field(self):
        """Test that from_ can be set using 'from' alias."""
        data = {
            "name": "test-rule",
            "action": "no-decrypt",
            "from": ["trust"],
            "folder": "Texas",
        }
        model = DecryptionRuleCreateModel(**data)
        assert model.from_ == ["trust"]

    def test_to_alias_field(self):
        """Test that to_ can be set using 'to' alias."""
        data = {
            "name": "test-rule",
            "action": "no-decrypt",
            "to": ["untrust"],
            "folder": "Texas",
        }
        model = DecryptionRuleCreateModel(**data)
        assert model.to_ == ["untrust"]

    def test_default_values(self):
        """Test that default values are set correctly."""
        model = DecryptionRuleCreateModel(
            name="test-rule",
            action="no-decrypt",
            folder="Texas",
        )
        assert model.from_ == ["any"]
        assert model.to_ == ["any"]
        assert model.source == ["any"]
        assert model.destination == ["any"]
        assert model.source_user == ["any"]
        assert model.category == ["any"]
        assert model.service == ["any"]
        assert model.source_hip == ["any"]
        assert model.destination_hip == ["any"]
        assert model.negate_source is False
        assert model.negate_destination is False
        assert model.disabled is False
        assert model.description is None
        assert model.profile is None
        assert model.type is None
        assert model.log_setting is None
        assert model.log_fail is None
        assert model.log_success is None
        assert model.tag == []


class TestDecryptionRuleNonUniqueValues:
    """Tests to verify that non-unique values are allowed in from_ and to_ fields."""

    def test_from_field_allows_non_unique_values(self):
        """Test that the from_ field allows duplicate values."""
        data = {
            "name": "test_rule",
            "action": "no-decrypt",
            "from_": ["trust", "trust", "dmz", "trust"],
            "to_": ["untrust"],
            "source": ["any"],
            "destination": ["any"],
            "folder": "TestFolder",
        }
        model = DecryptionRuleCreateModel(**data)
        assert model.from_ == ["trust", "trust", "dmz", "trust"]

    def test_to_field_allows_non_unique_values(self):
        """Test that the to_ field allows duplicate values."""
        data = {
            "name": "test_rule",
            "action": "no-decrypt",
            "from_": ["trust"],
            "to_": ["untrust", "dmz", "untrust", "untrust"],
            "source": ["any"],
            "destination": ["any"],
            "folder": "TestFolder",
        }
        model = DecryptionRuleCreateModel(**data)
        assert model.to_ == ["untrust", "dmz", "untrust", "untrust"]

    def test_other_fields_still_require_unique_values(self):
        """Test that other list fields still enforce uniqueness."""
        # Test source field
        with pytest.raises(ValidationError) as exc_info:
            DecryptionRuleCreateModel(
                name="test_rule",
                action="no-decrypt",
                from_=["trust"],
                to_=["untrust"],
                source=["addr1", "addr1", "addr2"],
                destination=["any"],
                folder="TestFolder",
            )
        assert "List items must be unique" in str(exc_info.value)

        # Test destination field
        with pytest.raises(ValidationError) as exc_info:
            DecryptionRuleCreateModel(
                name="test_rule",
                action="no-decrypt",
                from_=["trust"],
                to_=["untrust"],
                source=["any"],
                destination=["dest1", "dest2", "dest1"],
                folder="TestFolder",
            )
        assert "List items must be unique" in str(exc_info.value)

        # Test service field
        with pytest.raises(ValidationError) as exc_info:
            DecryptionRuleCreateModel(
                name="test_rule",
                action="no-decrypt",
                from_=["trust"],
                to_=["untrust"],
                source=["any"],
                destination=["any"],
                service=["tcp/80", "tcp/443", "tcp/80"],
                folder="TestFolder",
            )
        assert "List items must be unique" in str(exc_info.value)

        # Test category field
        with pytest.raises(ValidationError) as exc_info:
            DecryptionRuleCreateModel(
                name="test_rule",
                action="no-decrypt",
                from_=["trust"],
                to_=["untrust"],
                source=["any"],
                destination=["any"],
                category=["social", "news", "social"],
                folder="TestFolder",
            )
        assert "List items must be unique" in str(exc_info.value)

        # Test tag field
        with pytest.raises(ValidationError) as exc_info:
            DecryptionRuleCreateModel(
                name="test_rule",
                action="no-decrypt",
                from_=["trust"],
                to_=["untrust"],
                source=["any"],
                destination=["any"],
                tag=["tag1", "tag2", "tag1"],
                folder="TestFolder",
            )
        assert "List items must be unique" in str(exc_info.value)

        # Test source_user field
        with pytest.raises(ValidationError) as exc_info:
            DecryptionRuleCreateModel(
                name="test_rule",
                action="no-decrypt",
                from_=["trust"],
                to_=["untrust"],
                source=["any"],
                destination=["any"],
                source_user=["user1", "user2", "user1"],
                folder="TestFolder",
            )
        assert "List items must be unique" in str(exc_info.value)

        # Test source_hip field
        with pytest.raises(ValidationError) as exc_info:
            DecryptionRuleCreateModel(
                name="test_rule",
                action="no-decrypt",
                from_=["trust"],
                to_=["untrust"],
                source=["any"],
                destination=["any"],
                source_hip=["hip1", "hip1"],
                folder="TestFolder",
            )
        assert "List items must be unique" in str(exc_info.value)

        # Test destination_hip field
        with pytest.raises(ValidationError) as exc_info:
            DecryptionRuleCreateModel(
                name="test_rule",
                action="no-decrypt",
                from_=["trust"],
                to_=["untrust"],
                source=["any"],
                destination=["any"],
                destination_hip=["hip1", "hip2", "hip1"],
                folder="TestFolder",
            )
        assert "List items must be unique" in str(exc_info.value)

    def test_update_model_from_and_to_allow_non_unique(self):
        """Test that DecryptionRuleUpdateModel also allows non-unique values in from_ and to_."""
        data = {
            "id": str(uuid.uuid4()),
            "name": "updated_rule",
            "action": "no-decrypt",
            "from_": ["zone1", "zone1", "zone2"],
            "to_": ["zone3", "zone3", "zone4"],
            "source": ["any"],
            "destination": ["any"],
        }
        model = DecryptionRuleUpdateModel(**data)
        assert model.from_ == ["zone1", "zone1", "zone2"]
        assert model.to_ == ["zone3", "zone3", "zone4"]

    def test_response_model_from_and_to_allow_non_unique(self):
        """Test that DecryptionRuleResponseModel also allows non-unique values in from_ and to_."""
        data = {
            "id": str(uuid.uuid4()),
            "name": "response_rule",
            "action": "no-decrypt",
            "from_": ["zone1", "zone1", "zone2"],
            "to_": ["zone3", "zone3", "zone4"],
            "source": ["any"],
            "destination": ["any"],
            "folder": "TestFolder",
        }
        model = DecryptionRuleResponseModel(**data)
        assert model.from_ == ["zone1", "zone1", "zone2"]
        assert model.to_ == ["zone3", "zone3", "zone4"]


class TestExtraFieldsForbidden:
    """Tests for extra='forbid' validation on all models."""

    def test_create_model_rejects_extra_fields(self):
        """Test that extra fields are rejected in CreateModel."""
        data = DecryptionRuleCreateModelFactory.build_valid()
        data["unknown_field"] = "should_fail"
        with pytest.raises(ValidationError) as exc_info:
            DecryptionRuleCreateModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_update_model_rejects_extra_fields(self):
        """Test that extra fields are rejected in UpdateModel."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestRule",
            "action": "no-decrypt",
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            DecryptionRuleUpdateModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_response_model_ignores_extra_fields(self):
        """Test that extra fields are silently ignored in ResponseModel."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestRule",
            "action": "no-decrypt",
            "folder": "Texas",
            "unknown_field": "should_be_ignored",
        }
        model = DecryptionRuleResponseModel(**data)
        assert not hasattr(model, "unknown_field")

    def test_move_model_rejects_extra_fields(self):
        """Test that extra fields are rejected in MoveModel."""
        data = {
            "destination": "top",
            "rulebase": "pre",
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            DecryptionRuleMoveModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_type_model_rejects_extra_fields(self):
        """Test that extra fields are rejected in DecryptionRuleType."""
        data = {
            "ssl_forward_proxy": {},
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            DecryptionRuleType(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestEnumValues:
    """Tests for enum values."""

    def test_action_enum_values(self):
        """Test all DecryptionRuleAction enum values."""
        expected = {"decrypt", "no-decrypt"}
        actual = {v.value for v in DecryptionRuleAction}
        assert expected == actual

    def test_move_destination_enum_values(self):
        """Test all DecryptionRuleMoveDestination enum values."""
        expected = {"top", "bottom", "before", "after"}
        actual = {v.value for v in DecryptionRuleMoveDestination}
        assert expected == actual

    def test_rulebase_enum_values(self):
        """Test all DecryptionRuleRulebase enum values."""
        expected = {"pre", "post"}
        actual = {v.value for v in DecryptionRuleRulebase}
        assert expected == actual


class TestBoundaryValues:
    """Tests for boundary values on string fields."""

    def test_name_max_length_pattern(self):
        """Test that name field follows the correct pattern."""
        # Valid names
        model = DecryptionRuleCreateModel(
            name="valid_name-123.test",
            action="no-decrypt",
            folder="Texas",
        )
        assert model.name == "valid_name-123.test"

        # Name with spaces
        model = DecryptionRuleCreateModel(
            name="valid name with spaces",
            action="no-decrypt",
            folder="Texas",
        )
        assert model.name == "valid name with spaces"

    def test_name_invalid_characters(self):
        """Test that invalid characters in name are rejected."""
        with pytest.raises(ValidationError):
            DecryptionRuleCreateModel(
                name="invalid@name!",
                action="no-decrypt",
                folder="Texas",
            )

    def test_folder_max_length(self):
        """Test that folder respects max_length of 64."""
        long_folder = "a" * 65
        with pytest.raises(ValidationError):
            DecryptionRuleCreateModel(
                name="test-rule",
                action="no-decrypt",
                folder=long_folder,
            )

    def test_folder_valid_at_max_length(self):
        """Test that folder at exactly 64 characters is valid."""
        folder_64 = "a" * 64
        model = DecryptionRuleCreateModel(
            name="test-rule",
            action="no-decrypt",
            folder=folder_64,
        )
        assert model.folder == folder_64

    def test_snippet_max_length(self):
        """Test that snippet respects max_length of 64."""
        long_snippet = "a" * 65
        with pytest.raises(ValidationError):
            DecryptionRuleCreateModel(
                name="test-rule",
                action="no-decrypt",
                snippet=long_snippet,
            )

    def test_device_max_length(self):
        """Test that device respects max_length of 64."""
        long_device = "a" * 65
        with pytest.raises(ValidationError):
            DecryptionRuleCreateModel(
                name="test-rule",
                action="no-decrypt",
                device=long_device,
            )

    def test_folder_invalid_pattern(self):
        """Test that folder rejects invalid characters."""
        with pytest.raises(ValidationError):
            DecryptionRuleCreateModel(
                name="test-rule",
                action="no-decrypt",
                folder="invalid@folder!",
            )

    def test_snippet_invalid_pattern(self):
        """Test that snippet rejects invalid characters."""
        with pytest.raises(ValidationError):
            DecryptionRuleCreateModel(
                name="test-rule",
                action="no-decrypt",
                snippet="invalid@snippet!",
            )

    def test_device_invalid_pattern_on_base_model(self):
        """Test that device rejects invalid characters on CreateModel (base model pattern)."""
        with pytest.raises(ValidationError):
            DecryptionRuleCreateModel(
                name="test-rule",
                action="no-decrypt",
                device="invalid@device!",
            )


# -------------------- End of Test Classes --------------------
