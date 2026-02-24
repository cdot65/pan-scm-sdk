# tests/scm/models/security/test_authentication_rule_models.py

"""Tests for authentication rule models."""

import uuid
from uuid import UUID

from pydantic import ValidationError

# External libraries
import pytest

# Local SDK imports
from scm.models.security.authentication_rules import (
    AuthenticationRuleCreateModel,
    AuthenticationRuleMoveDestination,
    AuthenticationRuleMoveModel,
    AuthenticationRuleResponseModel,
    AuthenticationRuleRulebase,
    AuthenticationRuleUpdateModel,
)


# -------------------- Test Classes for Enum Values --------------------


class TestEnumValues:
    """Tests for enum values."""

    def test_move_destination_enum_values(self):
        """Test all AuthenticationRuleMoveDestination enum values."""
        expected = {"top", "bottom", "before", "after"}
        actual = {v.value for v in AuthenticationRuleMoveDestination}
        assert expected == actual

    def test_rulebase_enum_values(self):
        """Test all AuthenticationRuleRulebase enum values."""
        expected = {"pre", "post"}
        actual = {v.value for v in AuthenticationRuleRulebase}
        assert expected == actual

    def test_move_destination_is_str_enum(self):
        """Test that MoveDestination values can be used as strings."""
        assert AuthenticationRuleMoveDestination.TOP == "top"
        assert AuthenticationRuleMoveDestination.BOTTOM == "bottom"
        assert AuthenticationRuleMoveDestination.BEFORE == "before"
        assert AuthenticationRuleMoveDestination.AFTER == "after"

    def test_rulebase_is_str_enum(self):
        """Test that Rulebase values can be used as strings."""
        assert AuthenticationRuleRulebase.PRE == "pre"
        assert AuthenticationRuleRulebase.POST == "post"


# -------------------- Test Classes for Base Model Validators --------------------


class TestAuthenticationRuleBaseModel:
    """Tests for AuthenticationRuleBaseModel validators."""

    def test_ensure_list_of_strings_with_string_input(self):
        """Test that a single string is converted to a list containing that string."""
        model = AuthenticationRuleCreateModel(
            name="test-rule",
            source="192.168.1.1",
            folder="Texas",
        )
        assert isinstance(model.source, list)
        assert model.source == ["192.168.1.1"]

    def test_ensure_list_of_strings_with_list_input(self):
        """Test that a list of strings passes validation."""
        model = AuthenticationRuleCreateModel(
            name="test-rule",
            source=["192.168.1.1", "10.0.0.0/8"],
            folder="Texas",
        )
        assert model.source == ["192.168.1.1", "10.0.0.0/8"]

    def test_ensure_list_of_strings_with_invalid_type(self):
        """Test that a non-string, non-list value raises a ValueError."""
        with pytest.raises(ValidationError, match="Value must be a list of strings"):
            AuthenticationRuleCreateModel(
                name="test-rule",
                source=123,
                folder="Texas",
            )

    def test_ensure_list_of_strings_with_dict_type(self):
        """Test that a dict value raises a ValueError."""
        with pytest.raises(ValidationError, match="Value must be a list of strings"):
            AuthenticationRuleCreateModel(
                name="test-rule",
                source={"invalid": "type"},
                folder="Texas",
            )

    def test_ensure_list_of_strings_with_non_string_items(self):
        """Test that a list containing non-string items raises a ValueError."""
        with pytest.raises(ValidationError, match="All items must be strings"):
            AuthenticationRuleCreateModel(
                name="test-rule",
                source=["valid", 123, "also-valid"],
                folder="Texas",
            )

    def test_ensure_list_of_strings_with_nested_structures(self):
        """Test that a list containing nested structures raises a ValueError."""
        with pytest.raises(ValidationError, match="All items must be strings"):
            AuthenticationRuleCreateModel(
                name="test-rule",
                source=["valid", ["nested"], "invalid"],
                folder="Texas",
            )

    def test_ensure_list_of_strings_with_mixed_types(self):
        """Test that a list containing mixed types raises a ValueError."""
        with pytest.raises(ValidationError, match="All items must be strings"):
            AuthenticationRuleCreateModel(
                name="test-rule",
                source=["valid", {"key": "value"}, 123],
                folder="Texas",
            )

    def test_ensure_list_of_strings_none_for_optional(self):
        """Test that None is accepted for optional list fields like hip_profiles."""
        model = AuthenticationRuleCreateModel(
            name="test-rule",
            folder="Texas",
            hip_profiles=None,
        )
        assert model.hip_profiles is None

    def test_ensure_list_of_strings_string_conversion_for_from(self):
        """Test that from_ field converts a string to a list."""
        model = AuthenticationRuleCreateModel(
            name="test-rule",
            folder="Texas",
            from_="trust",
        )
        assert model.from_ == ["trust"]

    def test_ensure_list_of_strings_string_conversion_for_to(self):
        """Test that to_ field converts a string to a list."""
        model = AuthenticationRuleCreateModel(
            name="test-rule",
            folder="Texas",
            to_="untrust",
        )
        assert model.to_ == ["untrust"]

    def test_ensure_list_of_strings_string_conversion_for_tag(self):
        """Test that tag field converts a string to a list."""
        model = AuthenticationRuleCreateModel(
            name="test-rule",
            folder="Texas",
            tag="my-tag",
        )
        assert model.tag == ["my-tag"]

    def test_ensure_list_of_strings_string_conversion_for_hip_profiles(self):
        """Test that hip_profiles field converts a string to a list."""
        model = AuthenticationRuleCreateModel(
            name="test-rule",
            folder="Texas",
            hip_profiles="profile1",
        )
        assert model.hip_profiles == ["profile1"]

    def test_ensure_unique_items_duplicate_source(self):
        """Test that duplicate items in source raise a ValueError."""
        with pytest.raises(ValidationError, match="List items must be unique"):
            AuthenticationRuleCreateModel(
                name="test-rule",
                source=["192.168.1.1", "192.168.1.1"],
                folder="Texas",
            )

    def test_ensure_unique_items_duplicate_destination(self):
        """Test that duplicate items in destination raise a ValueError."""
        with pytest.raises(ValidationError, match="List items must be unique"):
            AuthenticationRuleCreateModel(
                name="test-rule",
                destination=["dest1", "dest2", "dest1"],
                folder="Texas",
            )

    def test_ensure_unique_items_duplicate_source_user(self):
        """Test that duplicate items in source_user raise a ValueError."""
        with pytest.raises(ValidationError, match="List items must be unique"):
            AuthenticationRuleCreateModel(
                name="test-rule",
                source_user=["user1", "user1"],
                folder="Texas",
            )

    def test_ensure_unique_items_duplicate_source_hip(self):
        """Test that duplicate items in source_hip raise a ValueError."""
        with pytest.raises(ValidationError, match="List items must be unique"):
            AuthenticationRuleCreateModel(
                name="test-rule",
                source_hip=["hip1", "hip1"],
                folder="Texas",
            )

    def test_ensure_unique_items_duplicate_destination_hip(self):
        """Test that duplicate items in destination_hip raise a ValueError."""
        with pytest.raises(ValidationError, match="List items must be unique"):
            AuthenticationRuleCreateModel(
                name="test-rule",
                destination_hip=["hip1", "hip2", "hip1"],
                folder="Texas",
            )

    def test_ensure_unique_items_duplicate_service(self):
        """Test that duplicate items in service raise a ValueError."""
        with pytest.raises(ValidationError, match="List items must be unique"):
            AuthenticationRuleCreateModel(
                name="test-rule",
                service=["tcp/80", "tcp/443", "tcp/80"],
                folder="Texas",
            )

    def test_ensure_unique_items_duplicate_category(self):
        """Test that duplicate items in category raise a ValueError."""
        with pytest.raises(ValidationError, match="List items must be unique"):
            AuthenticationRuleCreateModel(
                name="test-rule",
                category=["social", "news", "social"],
                folder="Texas",
            )

    def test_ensure_unique_items_duplicate_tag(self):
        """Test that duplicate items in tag raise a ValueError."""
        with pytest.raises(ValidationError, match="List items must be unique"):
            AuthenticationRuleCreateModel(
                name="test-rule",
                tag=["tag1", "tag2", "tag1"],
                folder="Texas",
            )

    def test_ensure_unique_items_duplicate_hip_profiles(self):
        """Test that duplicate items in hip_profiles raise a ValueError."""
        with pytest.raises(ValidationError, match="List items must be unique"):
            AuthenticationRuleCreateModel(
                name="test-rule",
                hip_profiles=["profile1", "profile1"],
                folder="Texas",
            )

    def test_from_field_allows_non_unique_values(self):
        """Test that the from_ field allows duplicate values (no unique validator on from_)."""
        model = AuthenticationRuleCreateModel(
            name="test-rule",
            from_=["trust", "trust", "dmz"],
            folder="Texas",
        )
        assert model.from_ == ["trust", "trust", "dmz"]

    def test_to_field_allows_non_unique_values(self):
        """Test that the to_ field allows duplicate values (no unique validator on to_)."""
        model = AuthenticationRuleCreateModel(
            name="test-rule",
            to_=["untrust", "dmz", "untrust"],
            folder="Texas",
        )
        assert model.to_ == ["untrust", "dmz", "untrust"]


# -------------------- Test Classes for CreateModel --------------------


class TestAuthenticationRuleCreateModel:
    """Tests for AuthenticationRuleCreateModel validation."""

    def test_create_model_valid_minimal(self):
        """Test creation with only required fields."""
        model = AuthenticationRuleCreateModel(
            name="test-rule",
            folder="Texas",
        )
        assert model.name == "test-rule"
        assert model.folder == "Texas"
        assert model.disabled is False
        assert model.from_ == ["any"]
        assert model.to_ == ["any"]
        assert model.source == ["any"]
        assert model.destination == ["any"]
        assert model.service == ["any"]
        assert model.category == ["any"]
        assert model.source_user == ["any"]
        assert model.source_hip == ["any"]
        assert model.destination_hip == ["any"]
        assert model.negate_source is False
        assert model.negate_destination is False
        assert model.authentication_enforcement is None
        assert model.hip_profiles is None
        assert model.group_tag is None
        assert model.timeout is None
        assert model.log_setting is None
        assert model.log_authentication_timeout is False

    def test_create_model_valid_all_fields(self):
        """Test creation with all fields populated."""
        model = AuthenticationRuleCreateModel(
            name="full-rule",
            folder="Texas",
            disabled=True,
            description="A fully populated authentication rule",
            tag=["tag1", "tag2"],
            from_=["trust"],
            source=["10.0.0.0/8"],
            negate_source=True,
            source_user=["admin"],
            source_hip=["compliant"],
            to_=["untrust"],
            destination=["192.168.1.0/24"],
            negate_destination=True,
            destination_hip=["non-compliant"],
            service=["tcp/443"],
            category=["social-networking"],
            authentication_enforcement="auth-profile-1",
            hip_profiles=["hip1"],
            group_tag="my-group-tag",
            timeout=60,
            log_setting="default-logging",
            log_authentication_timeout=True,
            rulebase=AuthenticationRuleRulebase.POST,
        )
        assert model.name == "full-rule"
        assert model.folder == "Texas"
        assert model.disabled is True
        assert model.description == "A fully populated authentication rule"
        assert model.tag == ["tag1", "tag2"]
        assert model.from_ == ["trust"]
        assert model.source == ["10.0.0.0/8"]
        assert model.negate_source is True
        assert model.source_user == ["admin"]
        assert model.source_hip == ["compliant"]
        assert model.to_ == ["untrust"]
        assert model.destination == ["192.168.1.0/24"]
        assert model.negate_destination is True
        assert model.destination_hip == ["non-compliant"]
        assert model.service == ["tcp/443"]
        assert model.category == ["social-networking"]
        assert model.authentication_enforcement == "auth-profile-1"
        assert model.hip_profiles == ["hip1"]
        assert model.group_tag == "my-group-tag"
        assert model.timeout == 60
        assert model.log_setting == "default-logging"
        assert model.log_authentication_timeout is True
        assert model.rulebase == AuthenticationRuleRulebase.POST

    def test_create_model_invalid_name(self):
        """Test validation when an invalid name is provided."""
        with pytest.raises(ValidationError) as exc_info:
            AuthenticationRuleCreateModel(
                name="@invalid-name#",
                folder="Texas",
            )
        assert "name\n  String should match pattern" in str(exc_info.value)

    def test_create_model_with_folder(self):
        """Test creation with folder container."""
        model = AuthenticationRuleCreateModel(
            name="test-rule",
            folder="Texas",
        )
        assert model.folder == "Texas"
        assert model.snippet is None
        assert model.device is None

    def test_create_model_with_snippet(self):
        """Test creation with snippet container."""
        model = AuthenticationRuleCreateModel(
            name="test-rule",
            snippet="TestSnippet",
        )
        assert model.snippet == "TestSnippet"
        assert model.folder is None
        assert model.device is None

    def test_create_model_with_device(self):
        """Test creation with device container."""
        model = AuthenticationRuleCreateModel(
            name="test-rule",
            device="TestDevice",
        )
        assert model.device == "TestDevice"
        assert model.folder is None
        assert model.snippet is None

    def test_create_model_no_container(self):
        """Test validation when no container is provided."""
        with pytest.raises(ValueError) as exc_info:
            AuthenticationRuleCreateModel(name="test-rule")
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_create_model_multiple_containers(self):
        """Test validation when multiple containers are provided."""
        with pytest.raises(ValueError) as exc_info:
            AuthenticationRuleCreateModel(
                name="test-rule",
                folder="Texas",
                snippet="TestSnippet",
            )
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_create_model_all_containers(self):
        """Test validation when all containers are provided."""
        with pytest.raises(ValueError) as exc_info:
            AuthenticationRuleCreateModel(
                name="test-rule",
                folder="Texas",
                snippet="TestSnippet",
                device="TestDevice",
            )
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_create_model_from_alias(self):
        """Test that the from_ field can be set using the 'from' alias."""
        data = {
            "name": "test-rule",
            "folder": "Texas",
            "from": ["trust"],
        }
        model = AuthenticationRuleCreateModel(**data)
        assert model.from_ == ["trust"]

    def test_create_model_to_alias(self):
        """Test that the to_ field can be set using the 'to' alias."""
        data = {
            "name": "test-rule",
            "folder": "Texas",
            "to": ["untrust"],
        }
        model = AuthenticationRuleCreateModel(**data)
        assert model.to_ == ["untrust"]

    def test_create_model_timeout_valid_min(self):
        """Test timeout at minimum valid value."""
        model = AuthenticationRuleCreateModel(
            name="test-rule",
            folder="Texas",
            timeout=1,
        )
        assert model.timeout == 1

    def test_create_model_timeout_valid_max(self):
        """Test timeout at maximum valid value."""
        model = AuthenticationRuleCreateModel(
            name="test-rule",
            folder="Texas",
            timeout=1440,
        )
        assert model.timeout == 1440

    def test_create_model_timeout_below_min(self):
        """Test that timeout below minimum raises a validation error."""
        with pytest.raises(ValidationError) as exc_info:
            AuthenticationRuleCreateModel(
                name="test-rule",
                folder="Texas",
                timeout=0,
            )
        assert "timeout" in str(exc_info.value)

    def test_create_model_timeout_above_max(self):
        """Test that timeout above maximum raises a validation error."""
        with pytest.raises(ValidationError) as exc_info:
            AuthenticationRuleCreateModel(
                name="test-rule",
                folder="Texas",
                timeout=1441,
            )
        assert "timeout" in str(exc_info.value)

    def test_create_model_rulebase_pre(self):
        """Test creation with pre rulebase."""
        model = AuthenticationRuleCreateModel(
            name="test-rule",
            folder="Texas",
            rulebase=AuthenticationRuleRulebase.PRE,
        )
        assert model.rulebase == AuthenticationRuleRulebase.PRE

    def test_create_model_rulebase_post(self):
        """Test creation with post rulebase."""
        model = AuthenticationRuleCreateModel(
            name="test-rule",
            folder="Texas",
            rulebase=AuthenticationRuleRulebase.POST,
        )
        assert model.rulebase == AuthenticationRuleRulebase.POST

    def test_create_model_rulebase_none(self):
        """Test creation without rulebase (defaults to None)."""
        model = AuthenticationRuleCreateModel(
            name="test-rule",
            folder="Texas",
        )
        assert model.rulebase is None

    def test_create_model_duplicate_items_in_source(self):
        """Test validation when source contains duplicate items."""
        with pytest.raises(ValidationError, match="List items must be unique"):
            AuthenticationRuleCreateModel(
                name="test-rule",
                folder="Texas",
                source=["any", "any"],
            )


# -------------------- Test Classes for UpdateModel --------------------


class TestAuthenticationRuleUpdateModel:
    """Tests for AuthenticationRuleUpdateModel validation."""

    def test_update_model_valid(self):
        """Test validation with valid update data."""
        model = AuthenticationRuleUpdateModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedRule",
            source=["updated-source"],
            destination=["updated-dest"],
        )
        assert model.name == "UpdatedRule"
        assert model.source == ["updated-source"]
        assert model.destination == ["updated-dest"]
        assert isinstance(model.id, UUID)

    def test_update_model_minimal(self):
        """Test validation with minimal valid update fields."""
        model = AuthenticationRuleUpdateModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-rule",
            description="Updated description",
        )
        assert model.description == "Updated description"

    def test_update_model_invalid_fields(self):
        """Test validation with multiple invalid fields."""
        with pytest.raises(ValidationError) as exc_info:
            AuthenticationRuleUpdateModel(
                id="invalid-uuid",
                name="@invalid-name",
                source=["source", "source"],
            )
        error_msg = str(exc_info.value)
        assert "name\n  String should match pattern" in error_msg

    def test_update_model_with_rulebase(self):
        """Test update model with rulebase set."""
        model = AuthenticationRuleUpdateModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-rule",
            rulebase=AuthenticationRuleRulebase.POST,
        )
        assert model.rulebase == AuthenticationRuleRulebase.POST

    def test_update_model_with_all_fields(self):
        """Test update model with all fields populated."""
        model = AuthenticationRuleUpdateModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="full-update",
            disabled=True,
            description="Updated",
            tag=["tag1"],
            from_=["trust"],
            source=["10.0.0.0/8"],
            to_=["untrust"],
            destination=["192.168.1.0/24"],
            authentication_enforcement="auth-profile",
            hip_profiles=["hip1"],
            group_tag="group-tag",
            timeout=120,
            log_setting="my-log-setting",
            log_authentication_timeout=True,
        )
        assert model.name == "full-update"
        assert model.disabled is True
        assert model.authentication_enforcement == "auth-profile"
        assert model.hip_profiles == ["hip1"]
        assert model.group_tag == "group-tag"
        assert model.timeout == 120
        assert model.log_authentication_timeout is True

    def test_update_model_from_to_allow_non_unique(self):
        """Test that update model allows non-unique values in from_ and to_."""
        model = AuthenticationRuleUpdateModel(
            id=str(uuid.uuid4()),
            name="test-rule",
            from_=["zone1", "zone1", "zone2"],
            to_=["zone3", "zone3", "zone4"],
        )
        assert model.from_ == ["zone1", "zone1", "zone2"]
        assert model.to_ == ["zone3", "zone3", "zone4"]


# -------------------- Test Classes for ResponseModel --------------------


class TestAuthenticationRuleResponseModel:
    """Tests for AuthenticationRuleResponseModel validation."""

    def test_response_model_valid(self):
        """Test validation with valid response data."""
        model = AuthenticationRuleResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-rule",
            folder="Texas",
        )
        assert isinstance(model.id, UUID)
        assert model.name == "test-rule"
        assert model.folder == "Texas"

    def test_response_model_ignores_extra_fields(self):
        """Test that extra fields are silently ignored in ResponseModel."""
        model = AuthenticationRuleResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-rule",
            folder="Texas",
            unknown_field="should_be_ignored",
        )
        assert not hasattr(model, "unknown_field")

    def test_response_model_with_device_string(self):
        """Test response model with device container as string."""
        model = AuthenticationRuleResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-rule",
            device="TestDevice",
        )
        assert model.device == "TestDevice"

    def test_response_model_with_device_empty_dict(self):
        """Test response model with device container as empty dictionary."""
        model = AuthenticationRuleResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-rule",
            device={},
        )
        assert model.device == {}

    def test_response_model_device_validation_non_empty_dict(self):
        """Test that device validation rejects non-empty dictionaries."""
        with pytest.raises(
            ValueError,
            match="If device is a dictionary, it must be empty",
        ):
            AuthenticationRuleResponseModel(
                id=uuid.uuid4(),
                name="test-rule",
                device={"some_key": "some_value"},
            )

    def test_response_model_with_rulebase(self):
        """Test response model with rulebase field."""
        model = AuthenticationRuleResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-rule",
            folder="Texas",
            rulebase=AuthenticationRuleRulebase.PRE,
        )
        assert model.rulebase == AuthenticationRuleRulebase.PRE

    def test_response_model_with_all_fields(self):
        """Test response model with all fields populated."""
        model = AuthenticationRuleResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="full-response",
            folder="Texas",
            disabled=True,
            description="Full response rule",
            tag=["tag1"],
            from_=["trust"],
            source=["10.0.0.0/8"],
            to_=["untrust"],
            destination=["192.168.1.0/24"],
            service=["tcp/443"],
            category=["social-networking"],
            authentication_enforcement="auth-profile",
            hip_profiles=["hip1"],
            group_tag="my-group",
            timeout=120,
            log_setting="default-logging",
            log_authentication_timeout=True,
            rulebase=AuthenticationRuleRulebase.POST,
        )
        assert model.name == "full-response"
        assert model.authentication_enforcement == "auth-profile"
        assert model.hip_profiles == ["hip1"]
        assert model.group_tag == "my-group"
        assert model.timeout == 120
        assert model.log_authentication_timeout is True

    def test_response_model_from_to_allow_non_unique(self):
        """Test that response model allows non-unique values in from_ and to_."""
        model = AuthenticationRuleResponseModel(
            id=str(uuid.uuid4()),
            name="test-rule",
            folder="Texas",
            from_=["zone1", "zone1", "zone2"],
            to_=["zone3", "zone3", "zone4"],
        )
        assert model.from_ == ["zone1", "zone1", "zone2"]
        assert model.to_ == ["zone3", "zone3", "zone4"]

    def test_response_model_device_none(self):
        """Test response model with device as None."""
        model = AuthenticationRuleResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-rule",
            folder="Texas",
            device=None,
        )
        assert model.device is None


# -------------------- Test Classes for MoveModel --------------------


class TestAuthenticationRuleMoveModel:
    """Tests for AuthenticationRuleMoveModel validation."""

    def test_move_model_valid_top(self):
        """Test validation with valid top move configuration."""
        model = AuthenticationRuleMoveModel(
            destination=AuthenticationRuleMoveDestination.TOP,
            rulebase=AuthenticationRuleRulebase.PRE,
        )
        assert model.destination == AuthenticationRuleMoveDestination.TOP
        assert model.rulebase == AuthenticationRuleRulebase.PRE
        assert model.destination_rule is None

    def test_move_model_valid_bottom(self):
        """Test validation with valid bottom move configuration."""
        model = AuthenticationRuleMoveModel(
            destination=AuthenticationRuleMoveDestination.BOTTOM,
            rulebase=AuthenticationRuleRulebase.POST,
        )
        assert model.destination == AuthenticationRuleMoveDestination.BOTTOM
        assert model.rulebase == AuthenticationRuleRulebase.POST

    def test_move_model_valid_before(self):
        """Test validation with valid before move configuration."""
        dest_rule = uuid.uuid4()
        model = AuthenticationRuleMoveModel(
            destination=AuthenticationRuleMoveDestination.BEFORE,
            rulebase=AuthenticationRuleRulebase.PRE,
            destination_rule=dest_rule,
        )
        assert model.destination == AuthenticationRuleMoveDestination.BEFORE
        assert model.destination_rule == dest_rule

    def test_move_model_valid_after(self):
        """Test validation with valid after move configuration."""
        dest_rule = uuid.uuid4()
        model = AuthenticationRuleMoveModel(
            destination=AuthenticationRuleMoveDestination.AFTER,
            rulebase=AuthenticationRuleRulebase.PRE,
            destination_rule=dest_rule,
        )
        assert model.destination == AuthenticationRuleMoveDestination.AFTER
        assert model.destination_rule == dest_rule

    def test_move_model_invalid_destination(self):
        """Test validation with invalid destination."""
        with pytest.raises(ValidationError) as exc_info:
            AuthenticationRuleMoveModel(
                destination="invalid",
                rulebase="pre",
            )
        assert "destination\n  Input should be" in str(exc_info.value)

    def test_move_model_missing_destination_rule_before(self):
        """Test validation when destination_rule is missing for 'before' move."""
        with pytest.raises(ValueError) as exc_info:
            AuthenticationRuleMoveModel(
                destination=AuthenticationRuleMoveDestination.BEFORE,
                rulebase=AuthenticationRuleRulebase.PRE,
            )
        assert "destination_rule is required when destination is 'before'" in str(exc_info.value)

    def test_move_model_missing_destination_rule_after(self):
        """Test validation when destination_rule is missing for 'after' move."""
        with pytest.raises(ValueError) as exc_info:
            AuthenticationRuleMoveModel(
                destination=AuthenticationRuleMoveDestination.AFTER,
                rulebase=AuthenticationRuleRulebase.PRE,
            )
        assert "destination_rule is required when destination is 'after'" in str(exc_info.value)

    def test_move_model_unexpected_destination_rule_top(self):
        """Test validation when destination_rule is provided for 'top' move."""
        with pytest.raises(ValueError) as exc_info:
            AuthenticationRuleMoveModel(
                destination=AuthenticationRuleMoveDestination.TOP,
                rulebase=AuthenticationRuleRulebase.PRE,
                destination_rule=uuid.uuid4(),
            )
        assert "destination_rule should not be provided when destination is 'top'" in str(
            exc_info.value
        )

    def test_move_model_unexpected_destination_rule_bottom(self):
        """Test validation when destination_rule is provided for 'bottom' move."""
        with pytest.raises(ValueError) as exc_info:
            AuthenticationRuleMoveModel(
                destination=AuthenticationRuleMoveDestination.BOTTOM,
                rulebase=AuthenticationRuleRulebase.PRE,
                destination_rule=uuid.uuid4(),
            )
        assert "destination_rule should not be provided when destination is 'bottom'" in str(
            exc_info.value
        )


# -------------------- Test Classes for Extra Fields --------------------


class TestExtraFieldsForbidden:
    """Tests for extra='forbid' validation on all models."""

    def test_create_model_rejects_extra_fields(self):
        """Test that extra fields are rejected in CreateModel."""
        with pytest.raises(ValidationError) as exc_info:
            AuthenticationRuleCreateModel(
                name="test-rule",
                folder="Texas",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_update_model_rejects_extra_fields(self):
        """Test that extra fields are rejected in UpdateModel."""
        with pytest.raises(ValidationError) as exc_info:
            AuthenticationRuleUpdateModel(
                id="123e4567-e89b-12d3-a456-426655440000",
                name="TestRule",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_response_model_ignores_extra_fields(self):
        """Test that extra fields are silently ignored in ResponseModel."""
        model = AuthenticationRuleResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="TestRule",
            folder="Texas",
            unknown_field="should_be_ignored",
        )
        assert not hasattr(model, "unknown_field")

    def test_move_model_rejects_extra_fields(self):
        """Test that extra fields are rejected in MoveModel."""
        with pytest.raises(ValidationError) as exc_info:
            AuthenticationRuleMoveModel(
                destination="top",
                rulebase="pre",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)


# -------------------- End of Test Classes --------------------
