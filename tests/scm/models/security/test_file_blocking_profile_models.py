# tests/scm/models/security/test_file_blocking_profile_models.py

"""Tests for file blocking profile security models."""

# External libraries
from pydantic import ValidationError
import pytest

# Local SDK imports
from scm.models.security.file_blocking_profiles import (
    FileBlockingAction,
    FileBlockingDirection,
    FileBlockingProfileCreateModel,
    FileBlockingProfileResponseModel,
    FileBlockingProfileUpdateModel,
    FileBlockingRule,
)
from tests.factories.security.file_blocking_profile import (
    FileBlockingProfileCreateModelFactory,
    FileBlockingProfileUpdateModelFactory,
)

# -------------------- Test Classes for Pydantic Models --------------------


class TestFileBlockingRule:
    """Tests for FileBlockingRule validation."""

    def test_rule_valid(self):
        """Test validation with valid data."""
        data = {
            "name": "TestRule",
            "action": "alert",
            "application": ["any"],
            "direction": "both",
            "file_type": ["any"],
        }
        model = FileBlockingRule(**data)
        assert model.name == data["name"]
        assert model.action == FileBlockingAction.alert
        assert model.application == data["application"]
        assert model.direction == FileBlockingDirection.both
        assert model.file_type == data["file_type"]

    def test_rule_invalid_action(self):
        """Test validation with invalid action."""
        data = {
            "name": "TestRule",
            "action": "invalid",
        }
        with pytest.raises(ValidationError) as exc_info:
            FileBlockingRule(**data)
        assert "Input should be 'alert'" in str(exc_info.value)

    def test_rule_invalid_direction(self):
        """Test validation with invalid direction."""
        data = {
            "name": "TestRule",
            "direction": "invalid",
        }
        with pytest.raises(ValidationError) as exc_info:
            FileBlockingRule(**data)
        assert "Input should be 'download'" in str(exc_info.value)

    def test_rule_defaults(self):
        """Test that default values are set correctly."""
        data = {"name": "TestRule"}
        model = FileBlockingRule(**data)
        assert model.action == FileBlockingAction.alert
        assert model.application == ["any"]
        assert model.direction == FileBlockingDirection.both
        assert model.file_type == ["any"]

    def test_rule_block_action(self):
        """Test rule with block action."""
        data = {
            "name": "BlockRule",
            "action": "block",
            "file_type": ["exe", "dll"],
        }
        model = FileBlockingRule(**data)
        assert model.action == FileBlockingAction.block
        assert model.file_type == ["exe", "dll"]

    def test_rule_continue_action(self):
        """Test rule with continue action."""
        data = {
            "name": "ContinueRule",
            "action": "continue",
        }
        model = FileBlockingRule(**data)
        assert model.action == FileBlockingAction.continue_


class TestFileBlockingProfileCreateModel:
    """Tests for FileBlockingProfileCreateModel validation."""

    def test_profile_create_model_valid(self):
        """Test validation with valid data."""
        data = FileBlockingProfileCreateModelFactory.build_valid()
        model = FileBlockingProfileCreateModel(**data)
        assert model.name == data["name"]
        assert model.folder == data["folder"]
        assert len(model.rules) > 0
        assert isinstance(model.rules[0], FileBlockingRule)

    def test_profile_create_model_multiple_containers(self):
        """Test validation when multiple containers are provided."""
        data = FileBlockingProfileCreateModelFactory.build_with_multiple_containers()
        with pytest.raises(ValueError) as exc_info:
            FileBlockingProfileCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_profile_create_model_no_container(self):
        """Test validation when no container is provided."""
        data = FileBlockingProfileCreateModelFactory.build_with_no_container()
        with pytest.raises(ValueError) as exc_info:
            FileBlockingProfileCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_profile_create_model_with_snippet(self):
        """Test creation with snippet container."""
        data = FileBlockingProfileCreateModelFactory.build_with_snippet()
        model = FileBlockingProfileCreateModel(**data)
        assert model.snippet == "TestSnippet"
        assert model.folder is None
        assert model.device is None

    def test_profile_create_model_with_device(self):
        """Test creation with device container."""
        data = FileBlockingProfileCreateModelFactory.build_with_device()
        model = FileBlockingProfileCreateModel(**data)
        assert model.device == "TestDevice"
        assert model.folder is None
        assert model.snippet is None

    def test_profile_create_model_without_rules(self):
        """Test creation without rules field."""
        data = FileBlockingProfileCreateModelFactory.build_valid()
        data.pop("rules", None)
        model = FileBlockingProfileCreateModel(**data)
        assert model.rules is None


class TestFileBlockingProfileUpdateModel:
    """Tests for FileBlockingProfileUpdateModel validation."""

    def test_profile_update_model_valid(self):
        """Test validation with valid update data."""
        data = FileBlockingProfileUpdateModelFactory.build_valid()
        model = FileBlockingProfileUpdateModel(**data)
        assert model.name == data["name"]
        assert model.description == data["description"]
        assert isinstance(model.rules[0], FileBlockingRule)

    def test_profile_update_model_partial_update(self):
        """Test validation with partial update data."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "UpdatedProfile",
            "description": "Updated description",
            "rules": [],
        }
        model = FileBlockingProfileUpdateModel(**data)
        assert model.name == data["name"]
        assert model.description == data["description"]
        assert len(model.rules) == 0


class TestFileBlockingProfileResponseModel:
    """Tests for FileBlockingProfileResponseModel validation."""

    def test_profile_response_model_valid(self):
        """Test validation with valid response data."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestProfile",
            "folder": "Texas",
            "rules": [
                {
                    "name": "TestRule",
                    "action": "block",
                    "file_type": ["exe"],
                }
            ],
        }
        model = FileBlockingProfileResponseModel(**data)
        assert str(model.id) == data["id"]
        assert model.name == data["name"]
        assert model.folder == data["folder"]
        assert isinstance(model.rules[0], FileBlockingRule)

    def test_profile_response_model_invalid_uuid(self):
        """Test validation with invalid UUID format."""
        data = {
            "id": "invalid-uuid",
            "name": "TestProfile",
            "folder": "Texas",
            "rules": [],
        }
        with pytest.raises(ValidationError) as exc_info:
            FileBlockingProfileResponseModel(**data)
        assert "Input should be a valid UUID" in str(exc_info.value)

    def test_profile_response_model_without_rules(self):
        """Test response model without rules."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestProfile",
            "folder": "Texas",
        }
        model = FileBlockingProfileResponseModel(**data)
        assert model.rules is None

    def test_profile_response_model_with_empty_rules(self):
        """Test response model with empty rules list."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestProfile",
            "folder": "Texas",
            "rules": [],
        }
        model = FileBlockingProfileResponseModel(**data)
        assert model.rules == []


class TestExtraFieldsForbidden:
    """Tests for extra='forbid' validation on all models."""

    def test_profile_create_model_rejects_extra_fields(self):
        """Test that extra fields are rejected in CreateModel."""
        data = FileBlockingProfileCreateModelFactory.build_valid()
        data["unknown_field"] = "should_fail"
        with pytest.raises(ValidationError) as exc_info:
            FileBlockingProfileCreateModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_profile_update_model_rejects_extra_fields(self):
        """Test that extra fields are rejected in UpdateModel."""
        data = FileBlockingProfileUpdateModelFactory.build_valid()
        data["unknown_field"] = "should_fail"
        with pytest.raises(ValidationError) as exc_info:
            FileBlockingProfileUpdateModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_profile_response_model_ignores_extra_fields(self):
        """Test that extra fields are silently ignored in ResponseModel."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestProfile",
            "folder": "Texas",
            "unknown_field": "should_be_ignored",
        }
        model = FileBlockingProfileResponseModel(**data)
        assert not hasattr(model, "unknown_field")

    def test_rule_rejects_extra_fields(self):
        """Test that extra fields are rejected in FileBlockingRule."""
        data = {
            "name": "TestRule",
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            FileBlockingRule(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestEnumValues:
    """Tests for enum values."""

    def test_action_enum_values(self):
        """Test all FileBlockingAction enum values."""
        expected = {"alert", "block", "continue"}
        actual = {v.value for v in FileBlockingAction}
        assert expected == actual

    def test_direction_enum_values(self):
        """Test all FileBlockingDirection enum values."""
        expected = {"download", "upload", "both"}
        actual = {v.value for v in FileBlockingDirection}
        assert expected == actual


# -------------------- End of Test Classes --------------------
