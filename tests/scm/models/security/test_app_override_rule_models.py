# tests/scm/models/security/test_app_override_rule_models.py

"""Tests for app override rule security models."""

# Standard libraries
import uuid

# External libraries
from pydantic import ValidationError
import pytest

# Local SDK imports
from scm.models.security.app_override_rules import (
    AppOverrideRuleCreateModel,
    AppOverrideRuleMoveDestination,
    AppOverrideRuleMoveModel,
    AppOverrideRuleProtocol,
    AppOverrideRuleResponseModel,
    AppOverrideRuleRulebase,
    AppOverrideRuleUpdateModel,
)
from tests.factories.security.app_override_rule import (
    AppOverrideRuleCreateModelFactory,
    AppOverrideRuleMoveModelFactory,
    AppOverrideRuleUpdateModelFactory,
)

# -------------------- Test Classes for Pydantic Models --------------------


class TestAppOverrideRuleCreateModel:
    """Tests for AppOverrideRuleCreateModel validation."""

    def test_create_model_valid(self):
        """Test validation with valid data."""
        data = AppOverrideRuleCreateModelFactory.build_valid()
        model = AppOverrideRuleCreateModel(**data)
        assert model.name == data["name"]
        assert model.folder == data["folder"]
        assert model.application == data["application"]
        assert model.port == data["port"]
        assert model.protocol == AppOverrideRuleProtocol.tcp

    def test_create_model_from_alias(self):
        """Test that from_ alias 'from' is handled correctly."""
        data = AppOverrideRuleCreateModelFactory.build_valid()
        model = AppOverrideRuleCreateModel(**data)
        assert model.from_ == data["from_"]

        # Test serialization with alias
        dumped = model.model_dump(by_alias=True)
        assert "from" in dumped
        assert dumped["from"] == data["from_"]

    def test_create_model_to_alias(self):
        """Test that to_ alias 'to' is handled correctly."""
        data = AppOverrideRuleCreateModelFactory.build_valid()
        model = AppOverrideRuleCreateModel(**data)
        assert model.to_ == data["to_"]

        # Test serialization with alias
        dumped = model.model_dump(by_alias=True)
        assert "to" in dumped
        assert dumped["to"] == data["to_"]

    def test_create_model_multiple_containers(self):
        """Test validation when multiple containers are provided."""
        data = AppOverrideRuleCreateModelFactory.build_valid()
        data["snippet"] = "TestSnippet"
        with pytest.raises(ValueError) as exc_info:
            AppOverrideRuleCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_create_model_no_container(self):
        """Test validation when no container is provided."""
        data = AppOverrideRuleCreateModelFactory.build_valid()
        data["folder"] = None
        with pytest.raises(ValueError) as exc_info:
            AppOverrideRuleCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_create_model_with_snippet(self):
        """Test creation with snippet container."""
        data = AppOverrideRuleCreateModelFactory.build_valid()
        data["folder"] = None
        data["snippet"] = "TestSnippet"
        model = AppOverrideRuleCreateModel(**data)
        assert model.snippet == "TestSnippet"
        assert model.folder is None
        assert model.device is None

    def test_create_model_with_device(self):
        """Test creation with device container."""
        data = AppOverrideRuleCreateModelFactory.build_valid()
        data["folder"] = None
        data["device"] = "TestDevice"
        model = AppOverrideRuleCreateModel(**data)
        assert model.device == "TestDevice"
        assert model.folder is None
        assert model.snippet is None

    def test_create_model_with_rulebase(self):
        """Test creation with rulebase field."""
        data = AppOverrideRuleCreateModelFactory.build_valid()
        data["rulebase"] = "post"
        model = AppOverrideRuleCreateModel(**data)
        assert model.rulebase == AppOverrideRuleRulebase.POST

    def test_create_model_udp_protocol(self):
        """Test creation with UDP protocol."""
        data = AppOverrideRuleCreateModelFactory.build_valid()
        data["protocol"] = "udp"
        model = AppOverrideRuleCreateModel(**data)
        assert model.protocol == AppOverrideRuleProtocol.udp

    def test_create_model_duplicate_source(self):
        """Test validation rejects duplicate source items."""
        data = AppOverrideRuleCreateModelFactory.build_valid()
        data["source"] = ["192.168.1.1", "192.168.1.1"]
        with pytest.raises(ValueError, match="List items must be unique"):
            AppOverrideRuleCreateModel(**data)

    def test_create_model_duplicate_destination(self):
        """Test validation rejects duplicate destination items."""
        data = AppOverrideRuleCreateModelFactory.build_valid()
        data["destination"] = ["any", "any"]
        with pytest.raises(ValueError, match="List items must be unique"):
            AppOverrideRuleCreateModel(**data)

    def test_create_model_duplicate_tag(self):
        """Test validation rejects duplicate tag items."""
        data = AppOverrideRuleCreateModelFactory.build_valid()
        data["tag"] = ["tag1", "tag1"]
        with pytest.raises(ValueError, match="List items must be unique"):
            AppOverrideRuleCreateModel(**data)

    def test_create_model_duplicate_from(self):
        """Test validation rejects duplicate from_ items."""
        data = AppOverrideRuleCreateModelFactory.build_valid()
        data["from_"] = ["trust", "trust"]
        with pytest.raises(ValueError, match="List items must be unique"):
            AppOverrideRuleCreateModel(**data)

    def test_create_model_duplicate_to(self):
        """Test validation rejects duplicate to_ items."""
        data = AppOverrideRuleCreateModelFactory.build_valid()
        data["to_"] = ["untrust", "untrust"]
        with pytest.raises(ValueError, match="List items must be unique"):
            AppOverrideRuleCreateModel(**data)

    def test_create_model_single_string_to_list(self):
        """Test that single string values for list fields are converted to lists."""
        model = AppOverrideRuleCreateModel(
            name="TestRule",
            folder="Texas",
            application="web-browsing",
            port="80",
            protocol="tcp",
            source="192.168.1.1",
        )
        assert model.source == ["192.168.1.1"]

    def test_create_model_invalid_source_type(self):
        """Test that invalid types for list fields raise ValueError."""
        with pytest.raises(ValueError, match="Value must be a list of strings"):
            AppOverrideRuleCreateModel(
                name="TestRule",
                folder="Texas",
                application="web-browsing",
                port="80",
                protocol="tcp",
                source=123,
            )

    def test_create_model_non_string_items_in_list(self):
        """Test that non-string items in list fields raise ValueError."""
        with pytest.raises(ValueError, match="All items must be strings"):
            AppOverrideRuleCreateModel(
                name="TestRule",
                folder="Texas",
                application="web-browsing",
                port="80",
                protocol="tcp",
                source=["192.168.1.1", 123],
            )


class TestAppOverrideRuleUpdateModel:
    """Tests for AppOverrideRuleUpdateModel validation."""

    def test_update_model_valid(self):
        """Test validation with valid update data."""
        data = AppOverrideRuleUpdateModelFactory.build_valid()
        model = AppOverrideRuleUpdateModel(**data)
        assert model.name == data["name"]
        assert model.application == data["application"]

    def test_update_model_minimal(self):
        """Test validation with minimal update data."""
        data = AppOverrideRuleUpdateModelFactory.build_minimal_update()
        model = AppOverrideRuleUpdateModel(**data)
        assert model.name == data["name"]
        assert model.description == data["description"]

    def test_update_model_invalid_uuid(self):
        """Test validation with invalid UUID format."""
        data = AppOverrideRuleUpdateModelFactory.build_valid()
        data["id"] = "invalid-uuid"
        with pytest.raises(ValidationError) as exc_info:
            AppOverrideRuleUpdateModel(**data)
        assert "Input should be a valid UUID" in str(exc_info.value)

    def test_update_model_with_from_to_aliases(self):
        """Test that from_ and to_ aliases work in update model."""
        data = AppOverrideRuleUpdateModelFactory.build_valid()
        data["from_"] = ["trust"]
        data["to_"] = ["untrust"]
        model = AppOverrideRuleUpdateModel(**data)
        dumped = model.model_dump(by_alias=True)
        assert "from" in dumped
        assert "to" in dumped
        assert dumped["from"] == ["trust"]
        assert dumped["to"] == ["untrust"]


class TestAppOverrideRuleResponseModel:
    """Tests for AppOverrideRuleResponseModel validation."""

    def test_response_model_valid(self):
        """Test validation with valid response data."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestRule",
            "folder": "Texas",
            "application": "web-browsing",
            "port": "80",
            "protocol": "tcp",
            "source": ["any"],
            "destination": ["any"],
            "from": ["any"],
            "to": ["any"],
        }
        model = AppOverrideRuleResponseModel(**data)
        assert str(model.id) == data["id"]
        assert model.name == data["name"]
        assert model.folder == data["folder"]
        assert model.application == data["application"]

    def test_response_model_invalid_uuid(self):
        """Test validation with invalid UUID format."""
        data = {
            "id": "invalid-uuid",
            "name": "TestRule",
            "folder": "Texas",
            "application": "web-browsing",
            "port": "80",
            "protocol": "tcp",
        }
        with pytest.raises(ValidationError) as exc_info:
            AppOverrideRuleResponseModel(**data)
        assert "Input should be a valid UUID" in str(exc_info.value)

    def test_response_model_ignores_extra_fields(self):
        """Test that extra fields are silently ignored in ResponseModel."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestRule",
            "folder": "Texas",
            "application": "web-browsing",
            "port": "80",
            "protocol": "tcp",
            "unknown_field": "should_be_ignored",
        }
        model = AppOverrideRuleResponseModel(**data)
        assert not hasattr(model, "unknown_field")

    def test_response_model_from_to_aliases(self):
        """Test that from and to fields are properly deserialized using aliases."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestRule",
            "folder": "Texas",
            "application": "web-browsing",
            "port": "80",
            "protocol": "tcp",
            "from": ["trust"],
            "to": ["untrust"],
        }
        model = AppOverrideRuleResponseModel(**data)
        assert model.from_ == ["trust"]
        assert model.to_ == ["untrust"]

    def test_response_model_with_empty_dict_device(self):
        """Test that response model accepts empty dict device value."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestRule",
            "folder": None,
            "device": {},
            "application": "web-browsing",
            "port": "80",
            "protocol": "tcp",
        }
        model = AppOverrideRuleResponseModel(**data)
        assert model.device == {}

    def test_response_model_with_non_empty_dict_device_fails(self):
        """Test that response model rejects non-empty dict device value."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestRule",
            "folder": None,
            "device": {"key": "value"},
            "application": "web-browsing",
            "port": "80",
            "protocol": "tcp",
        }
        with pytest.raises(ValidationError) as exc_info:
            AppOverrideRuleResponseModel(**data)
        assert "If device is a dictionary, it must be empty" in str(exc_info.value)

    def test_response_model_with_rulebase(self):
        """Test that response model accepts rulebase."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestRule",
            "folder": "Texas",
            "application": "web-browsing",
            "port": "80",
            "protocol": "tcp",
            "rulebase": "pre",
        }
        model = AppOverrideRuleResponseModel(**data)
        assert model.rulebase == AppOverrideRuleRulebase.PRE


class TestAppOverrideRuleMoveModel:
    """Tests for AppOverrideRuleMoveModel validation."""

    def test_move_model_valid_top(self):
        """Test valid move to top."""
        model = AppOverrideRuleMoveModel(
            destination=AppOverrideRuleMoveDestination.TOP,
            rulebase=AppOverrideRuleRulebase.PRE,
        )
        assert model.destination == AppOverrideRuleMoveDestination.TOP
        assert model.rulebase == AppOverrideRuleRulebase.PRE
        assert model.destination_rule is None

    def test_move_model_valid_bottom(self):
        """Test valid move to bottom."""
        model = AppOverrideRuleMoveModel(
            destination=AppOverrideRuleMoveDestination.BOTTOM,
            rulebase=AppOverrideRuleRulebase.POST,
        )
        assert model.destination == AppOverrideRuleMoveDestination.BOTTOM
        assert model.rulebase == AppOverrideRuleRulebase.POST

    def test_move_model_valid_before(self):
        """Test valid move before a rule."""
        data = AppOverrideRuleMoveModelFactory.build_valid_before()
        model = AppOverrideRuleMoveModel(**data)
        assert model.destination == AppOverrideRuleMoveDestination.BEFORE
        assert model.destination_rule is not None

    def test_move_model_valid_after(self):
        """Test valid move after a rule."""
        dest_rule = str(uuid.uuid4())
        model = AppOverrideRuleMoveModel(
            destination=AppOverrideRuleMoveDestination.AFTER,
            rulebase=AppOverrideRuleRulebase.PRE,
            destination_rule=dest_rule,
        )
        assert model.destination == AppOverrideRuleMoveDestination.AFTER
        assert str(model.destination_rule) == dest_rule

    def test_move_model_invalid_destination(self):
        """Test move with invalid destination value."""
        data = AppOverrideRuleMoveModelFactory.build_with_invalid_destination()
        with pytest.raises(ValidationError) as exc_info:
            AppOverrideRuleMoveModel(**data)
        assert "Input should be 'top', 'bottom', 'before' or 'after'" in str(exc_info.value)

    def test_move_model_missing_destination_rule_before(self):
        """Test move before missing destination_rule."""
        data = AppOverrideRuleMoveModelFactory.build_missing_destination_rule()
        with pytest.raises(ValidationError) as exc_info:
            AppOverrideRuleMoveModel(**data)
        assert "destination_rule is required when destination is 'before'" in str(exc_info.value)

    def test_move_model_missing_destination_rule_after(self):
        """Test move after missing destination_rule."""
        with pytest.raises(ValidationError) as exc_info:
            AppOverrideRuleMoveModel(
                destination=AppOverrideRuleMoveDestination.AFTER,
                rulebase=AppOverrideRuleRulebase.PRE,
            )
        assert "destination_rule is required when destination is 'after'" in str(exc_info.value)

    def test_move_model_unexpected_destination_rule_top(self):
        """Test that providing destination_rule with 'top' raises a ValueError."""
        with pytest.raises(
            ValueError,
            match="destination_rule should not be provided when destination is 'top'",
        ):
            AppOverrideRuleMoveModel(
                destination=AppOverrideRuleMoveDestination.TOP,
                rulebase=AppOverrideRuleRulebase.PRE,
                destination_rule=uuid.uuid4(),
            )

    def test_move_model_unexpected_destination_rule_bottom(self):
        """Test that providing destination_rule with 'bottom' raises a ValueError."""
        with pytest.raises(
            ValueError,
            match="destination_rule should not be provided when destination is 'bottom'",
        ):
            AppOverrideRuleMoveModel(
                destination=AppOverrideRuleMoveDestination.BOTTOM,
                rulebase=AppOverrideRuleRulebase.PRE,
                destination_rule=uuid.uuid4(),
            )


class TestExtraFieldsForbidden:
    """Tests for extra='forbid' validation on all models."""

    def test_create_model_rejects_extra_fields(self):
        """Test that extra fields are rejected in CreateModel."""
        data = AppOverrideRuleCreateModelFactory.build_valid()
        data["unknown_field"] = "should_fail"
        with pytest.raises(ValidationError) as exc_info:
            AppOverrideRuleCreateModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_update_model_rejects_extra_fields(self):
        """Test that extra fields are rejected in UpdateModel."""
        data = AppOverrideRuleUpdateModelFactory.build_valid()
        data["unknown_field"] = "should_fail"
        with pytest.raises(ValidationError) as exc_info:
            AppOverrideRuleUpdateModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_move_model_rejects_extra_fields(self):
        """Test that extra fields are rejected in MoveModel."""
        data = {
            "destination": "top",
            "rulebase": "pre",
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            AppOverrideRuleMoveModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestEnumValues:
    """Tests for enum values."""

    def test_protocol_enum_values(self):
        """Test all AppOverrideRuleProtocol enum values."""
        expected = {"tcp", "udp"}
        actual = {v.value for v in AppOverrideRuleProtocol}
        assert expected == actual

    def test_rulebase_enum_values(self):
        """Test all AppOverrideRuleRulebase enum values."""
        expected = {"pre", "post"}
        actual = {v.value for v in AppOverrideRuleRulebase}
        assert expected == actual

    def test_move_destination_enum_values(self):
        """Test all AppOverrideRuleMoveDestination enum values."""
        expected = {"top", "bottom", "before", "after"}
        actual = {v.value for v in AppOverrideRuleMoveDestination}
        assert expected == actual


class TestContainerValidation:
    """Tests for container validation on CreateModel."""

    def test_create_no_container(self):
        """Test that not providing any container raises ValueError."""
        with pytest.raises(
            ValueError,
            match="Exactly one of 'folder', 'snippet', or 'device' must be provided.",
        ):
            AppOverrideRuleCreateModel(
                name="TestRule",
                application="web-browsing",
                port="80",
                protocol="tcp",
            )

    def test_create_multiple_containers(self):
        """Test that providing multiple containers raises ValueError."""
        with pytest.raises(
            ValueError,
            match="Exactly one of 'folder', 'snippet', or 'device' must be provided.",
        ):
            AppOverrideRuleCreateModel(
                name="TestRule",
                application="web-browsing",
                port="80",
                protocol="tcp",
                folder="Texas",
                snippet="MySnippet",
            )


# -------------------- End of Test Classes --------------------
