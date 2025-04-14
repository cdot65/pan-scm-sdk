# tests/scm/models/security/test_security_rules_models.py
import uuid
from uuid import UUID

from pydantic import ValidationError

# External libraries
import pytest

# Local SDK imports
from scm.models.security.security_rules import (
    SecurityRuleAction,
    SecurityRuleCreateModel,
    SecurityRuleMoveDestination,
    SecurityRuleMoveModel,
    SecurityRuleProfileSetting,
    SecurityRuleResponseModel,
    SecurityRuleUpdateModel,
)
from tests.factories.security import (
    SecurityRuleCreateApiFactory,
    SecurityRuleCreateModelFactory,
    SecurityRuleMoveApiFactory,
    SecurityRuleMoveModelFactory,
    SecurityRuleResponseFactory,
    SecurityRuleUpdateModelFactory,
)

# -------------------- Test Classes for Pydantic Models --------------------


class TestSecurityRuleCreateModel:
    """Tests for SecurityRuleCreateModel validation."""

    def test_security_rule_create_model_valid(self):
        """Test validation with valid data."""
        data = SecurityRuleCreateModelFactory.build_valid()
        model = SecurityRuleCreateModel(**data)
        assert model.name == data["name"]
        assert model.folder == data["folder"]
        assert model.action == SecurityRuleAction.allow
        assert model.from_ == data["from_"]
        assert model.to_ == data["to_"]
        assert model.source == data["source"]
        assert model.destination == data["destination"]

    def test_security_rule_create_model_invalid_name(self):
        """Test validation when an invalid name is provided."""
        data = SecurityRuleCreateModelFactory.build_with_invalid_name()
        with pytest.raises(ValidationError) as exc_info:
            SecurityRuleCreateModel(**data)
        assert "name\n  String should match pattern" in str(exc_info.value)

    def test_security_rule_create_model_invalid_action(self):
        """Test validation when an invalid action is provided."""
        data = SecurityRuleCreateModelFactory.build_with_invalid_action()
        with pytest.raises(ValidationError) as exc_info:
            SecurityRuleCreateModel(**data)
        assert "action\n  Input should be" in str(exc_info.value)

    def test_security_rule_create_model_duplicate_items(self):
        """Test validation when lists contain duplicate items."""
        data = SecurityRuleCreateModelFactory.build_with_duplicate_items()
        with pytest.raises(ValidationError) as exc_info:
            SecurityRuleCreateModel(**data)
        assert "List items must be unique" in str(exc_info.value)

    def test_security_rule_create_model_with_snippet(self):
        """Test creation with snippet container."""
        model = SecurityRuleCreateApiFactory.with_snippet()
        assert model.snippet == "TestSnippet"
        assert model.folder is None
        assert model.device is None

    def test_security_rule_create_model_with_device(self):
        """Test creation with device container."""
        model = SecurityRuleCreateApiFactory.with_device()
        assert model.device == "TestDevice"
        assert model.folder is None
        assert model.snippet is None

    def test_security_rule_create_model_with_custom_zones(self):
        """Test creation with custom security zones."""
        model = SecurityRuleCreateApiFactory.with_custom_zones(
            from_zones=["trust"], to_zones=["untrust"]
        )
        assert model.from_ == ["trust"]
        assert model.to_ == ["untrust"]

    def test_security_rule_create_model_string_to_list_conversion(self):
        """Test that string values are converted to lists for list fields."""
        data = SecurityRuleCreateModelFactory.build_valid()
        data["source"] = "any"  # Provide string instead of list
        model = SecurityRuleCreateModel(**data)
        assert isinstance(model.source, list)
        assert model.source == ["any"]

    def test_security_rule_create_model_invalid_list_type(self):
        """Test validation when invalid type is provided for list fields."""
        data = SecurityRuleCreateModelFactory.build_valid()
        data["source"] = {"invalid": "type"}
        with pytest.raises(ValidationError) as exc_info:
            SecurityRuleCreateModel(**data)
        assert "Value must be a list of strings" in str(exc_info.value)

    def test_security_rule_create_model_no_container(self):
        """Test validation when no container is provided."""
        data = SecurityRuleCreateModelFactory.build_valid()
        data.pop("folder")  # Remove the container field
        with pytest.raises(ValueError) as exc_info:
            SecurityRuleCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_security_rule_create_model_multiple_containers(self):
        """Test validation when multiple containers are provided."""
        data = SecurityRuleCreateModelFactory.build_valid()
        data["snippet"] = "TestSnippet"  # Add a second container
        with pytest.raises(ValueError) as exc_info:
            SecurityRuleCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_security_rule_create_model_all_containers(self):
        """Test validation when all containers are provided."""
        data = SecurityRuleCreateModelFactory.build_valid()
        data["snippet"] = "TestSnippet"
        data["device"] = "TestDevice"
        with pytest.raises(ValueError) as exc_info:
            SecurityRuleCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )


class TestSecurityRuleUpdateModel:
    """Tests for SecurityRuleUpdateModel validation."""

    def test_security_rule_update_model_valid(self):
        """Test validation with valid update data."""
        data = SecurityRuleUpdateModelFactory.build_valid()
        model = SecurityRuleUpdateModel(**data)
        assert model.name == "UpdatedRule"
        assert model.action == SecurityRuleAction.deny
        assert model.source == ["updated-source"]
        assert model.destination == ["updated-dest"]

    def test_security_rule_update_model_invalid_fields(self):
        """Test validation with multiple invalid fields."""
        data = SecurityRuleUpdateModelFactory.build_with_invalid_fields()
        with pytest.raises(ValidationError) as exc_info:
            SecurityRuleUpdateModel(**data)
        error_msg = str(exc_info.value)
        assert "name\n  String should match pattern" in error_msg
        assert "action\n  Input should be" in error_msg
        assert "List items must be unique" in error_msg

    def test_security_rule_update_model_minimal_update(self):
        """Test validation with minimal valid update fields."""
        data = SecurityRuleUpdateModelFactory.build_minimal_update()
        model = SecurityRuleUpdateModel(**data)
        assert model.description == "Updated description"

    def test_security_rule_update_model_with_action_update(self):
        """Test update with modified action."""
        model = SecurityRuleCreateApiFactory.with_post_rulebase(action=SecurityRuleAction.deny)
        assert model.action == SecurityRuleAction.deny

    def test_security_rule_update_model_with_zones_update(self):
        """Test update with modified security zones."""
        model = SecurityRuleCreateApiFactory.with_post_rulebase(
            from_=["new-trust"],
            to_=["new-untrust"],
        )
        assert model.from_ == ["new-trust"]
        assert model.to_ == ["new-untrust"]


class TestSecurityRuleMoveModel:
    """Tests for SecurityRuleMoveModel validation."""

    def test_security_rule_move_model_valid_before(self):
        """Test validation with valid before move configuration."""
        data = SecurityRuleMoveModelFactory.build_valid_before()
        model = SecurityRuleMoveModel(**data)
        assert model.destination == SecurityRuleMoveDestination.BEFORE
        assert model.destination_rule is not None

    def test_security_rule_move_model_invalid_destination(self):
        """Test validation with invalid destination."""
        data = SecurityRuleMoveModelFactory.build_with_invalid_destination()
        with pytest.raises(ValidationError) as exc_info:
            SecurityRuleMoveModel(**data)
        assert "destination\n  Input should be" in str(exc_info.value)

    def test_security_rule_move_model_missing_destination_rule(self):
        """Test validation when destination_rule is missing for before/after moves."""
        data = SecurityRuleMoveModelFactory.build_missing_destination_rule()
        with pytest.raises(ValueError) as exc_info:
            SecurityRuleMoveModel(**data)
        assert "destination_rule is required when destination is 'before'" in str(exc_info.value)

    def test_security_rule_move_model_top_with_destination_rule(self):
        """Test validation when destination_rule is provided for top/bottom moves."""
        with pytest.raises(ValidationError) as exc_info:
            SecurityRuleMoveApiFactory(
                destination=SecurityRuleMoveDestination.TOP,
                destination_rule="some-rule-id",
            )
        assert "1 validation error for SecurityRuleMoveModel" in str(exc_info.value)


class TestSecurityRuleResponseModel:
    """Tests for SecurityRuleResponseModel validation."""

    def test_security_rule_response_model_valid(self):
        """Test validation with valid response data."""
        data = SecurityRuleResponseFactory().model_dump()
        model = SecurityRuleResponseModel(**data)
        assert isinstance(model.id, UUID)
        assert model.name.startswith("security_rule_")
        assert model.folder == "Texas"
        assert model.action == SecurityRuleAction.allow

    def test_security_rule_response_model_from_request(self):
        """Test creation of response model from request data."""
        request_data = SecurityRuleCreateModelFactory.build_valid()
        request_model = SecurityRuleCreateModel(**request_data)
        response_data = SecurityRuleResponseFactory.from_request(request_model)
        model = SecurityRuleResponseModel(**response_data.model_dump())
        assert isinstance(model.id, UUID)
        assert model.name == request_model.name
        assert model.folder == request_model.folder
        assert model.action == request_model.action

    def test_security_rule_response_model_with_snippet(self):
        """Test response model with snippet container."""
        data = SecurityRuleResponseFactory.with_snippet()
        model = SecurityRuleResponseModel(**data.model_dump())
        assert model.snippet == "TestSnippet"
        assert model.folder is None
        assert model.device is None

    def test_security_rule_response_model_with_device_string(self):
        """Test response model with device container as string."""
        data = SecurityRuleResponseFactory.with_device("TestDevice")
        model = SecurityRuleResponseModel(**data.model_dump())
        assert model.device == "TestDevice"
        assert model.folder is None
        assert model.snippet is None

    def test_security_rule_response_model_with_device_empty_dict(self):
        """Test response model with device container as empty dictionary."""
        data = SecurityRuleResponseFactory.with_empty_dict_device()
        model = SecurityRuleResponseModel(**data.model_dump())
        assert model.device == {}
        assert model.folder is None
        assert model.snippet is None

    def test_security_rule_response_model_device_validation(self):
        """Test that device validation rejects non-empty dictionaries."""
        with pytest.raises(
            ValueError,
            match="If device is a dictionary, it must be empty",
        ):
            SecurityRuleResponseModel(
                id=uuid.uuid4(),
                name="test_rule",
                device={"some_key": "some_value"},
            )


class TestSecurityRuleProfileSetting:
    """Tests for SecurityRuleProfileSetting validation."""

    def test_profile_setting_with_duplicate_groups(self):
        """Test validation when group list contains duplicate items."""
        with pytest.raises(ValueError) as exc_info:
            SecurityRuleProfileSetting(group=["best-practice", "best-practice"])
        assert "List items in 'group' must be unique" in str(exc_info.value)

    def test_profile_setting_with_valid_groups(self):
        """Test validation with valid unique groups."""
        model = SecurityRuleProfileSetting(group=["best-practice", "strict"])
        assert model.group == ["best-practice", "strict"]

    def test_profile_setting_with_none_group(self):
        """Test validation when group is None."""
        model = SecurityRuleProfileSetting(group=None)
        assert model.group is None


class TestSecurityRuleBaseModel:
    """Tests for SecurityRuleBaseModel validators."""

    def test_ensure_list_of_strings_with_non_string_items(self):
        """Test validation when list contains non-string items."""
        data = SecurityRuleCreateModelFactory.build_valid()
        data["source"] = ["valid", 123, "also-valid"]  # Include a non-string item
        with pytest.raises(ValueError) as exc_info:
            SecurityRuleCreateModel(**data)
        assert "All items must be strings" in str(exc_info.value)

    def test_ensure_list_of_strings_with_nested_structures(self):
        """Test validation when list contains nested structures."""
        data = SecurityRuleCreateModelFactory.build_valid()
        data["source"] = ["valid", ["nested"], "invalid"]
        with pytest.raises(ValueError) as exc_info:
            SecurityRuleCreateModel(**data)
        assert "All items must be strings" in str(exc_info.value)

    def test_ensure_list_of_strings_with_mixed_types(self):
        """Test validation when list contains mixed types."""
        data = SecurityRuleCreateModelFactory.build_valid()
        data["source"] = ["valid", {"key": "value"}, 123]
        with pytest.raises(ValueError) as exc_info:
            SecurityRuleCreateModel(**data)
        assert "All items must be strings" in str(exc_info.value)


# -------------------- End of Test Classes --------------------
