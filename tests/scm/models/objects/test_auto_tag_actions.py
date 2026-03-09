# tests/scm/models/objects/test_auto_tag_actions.py

"""Tests for auto tag action model validation."""

from pydantic import ValidationError
import pytest

from scm.models.objects.auto_tag_actions import (
    AutoTagActionCreateModel,
    AutoTagActionResponseModel,
    AutoTagActionUpdateModel,
)
from tests.factories.objects.auto_tag_actions import (
    AutoTagActionCreateModelFactory,
    AutoTagActionUpdateModelFactory,
)


class TestAutoTagActionCreateModel:
    """Tests for AutoTagActionCreateModel validation."""

    def test_create_valid(self):
        """Test creating a valid auto tag action model."""
        data = AutoTagActionCreateModelFactory.build_valid()
        model = AutoTagActionCreateModel(**data)
        assert model.name == "TestAutoTagAction"
        assert model.folder == "Texas"

    def test_create_no_container_error(self):
        """Test that creating without container raises ValidationError."""
        data = AutoTagActionCreateModelFactory.build_with_no_container()
        with pytest.raises(ValidationError):
            AutoTagActionCreateModel(**data)

    def test_create_multiple_containers_error(self):
        """Test that creating with multiple containers raises ValidationError."""
        data = AutoTagActionCreateModelFactory.build_with_multiple_containers()
        with pytest.raises(ValidationError):
            AutoTagActionCreateModel(**data)

    def test_create_with_snippet(self):
        """Test creating with snippet container."""
        data = {"name": "TestAction", "snippet": "MySnippet"}
        model = AutoTagActionCreateModel(**data)
        assert model.snippet == "MySnippet"
        assert model.folder is None

    def test_create_with_device(self):
        """Test creating with device container."""
        data = {"name": "TestAction", "device": "MyDevice"}
        model = AutoTagActionCreateModel(**data)
        assert model.device == "MyDevice"
        assert model.folder is None

    def test_create_name_too_long(self):
        """Test that name exceeding max_length raises ValidationError."""
        data = {"name": "a" * 64, "folder": "Texas"}
        with pytest.raises(ValidationError):
            AutoTagActionCreateModel(**data)

    def test_create_name_invalid_chars(self):
        """Test that name with invalid characters raises ValidationError."""
        data = {"name": "invalid@name!", "folder": "Texas"}
        with pytest.raises(ValidationError):
            AutoTagActionCreateModel(**data)


class TestAutoTagActionUpdateModel:
    """Tests for AutoTagActionUpdateModel validation."""

    def test_update_valid(self):
        """Test creating a valid update model."""
        data = AutoTagActionUpdateModelFactory.build_valid()
        model = AutoTagActionUpdateModel(**data)
        assert model.name == "UpdatedAutoTagAction"
        assert str(model.id) == "123e4567-e89b-12d3-a456-426655440000"

    def test_update_without_id(self):
        """Test update model without id (allowed)."""
        data = {"name": "TestAction"}
        model = AutoTagActionUpdateModel(**data)
        assert model.id is None


class TestAutoTagActionResponseModel:
    """Tests for AutoTagActionResponseModel validation."""

    def test_response_valid(self):
        """Test creating a valid response model."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestAction",
            "folder": "Texas",
        }
        model = AutoTagActionResponseModel(**data)
        assert model.name == "TestAction"
        assert model.folder == "Texas"

    def test_response_ignores_extra_fields(self):
        """Test that response model ignores extra fields."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestAction",
            "folder": "Texas",
            "unknown_field": "should be ignored",
        }
        model = AutoTagActionResponseModel(**data)
        assert model.name == "TestAction"

    def test_response_with_actions(self):
        """Test response model with actions list."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestAction",
            "folder": "Texas",
            "actions": [
                {
                    "name": "tag-action",
                    "type": {
                        "tagging": {
                            "action": "add-tag",
                            "target": "source-address",
                            "tags": ["malware-host"],
                            "timeout": 86400,
                        }
                    },
                }
            ],
            "filter": "( severity eq critical )",
            "log_type": "threat",
        }
        model = AutoTagActionResponseModel(**data)
        assert model.name == "TestAction"
        assert len(model.actions) == 1
        assert model.actions[0].name == "tag-action"
        assert model.actions[0].type.tagging.action == "add-tag"
        assert model.actions[0].type.tagging.tags == ["malware-host"]
        assert model.filter == "( severity eq critical )"
        assert model.log_type == "threat"
