# tests/scm/models/objects/test_log_forwarding_profile_models.py

"""Tests for log forwarding profile models."""

from uuid import UUID

from pydantic import ValidationError

# External libraries
import pytest

# Local SDK imports
from scm.models.objects.log_forwarding_profile import (
    LogForwardingProfileCreateModel,
    LogForwardingProfileResponseModel,
    LogForwardingProfileUpdateModel,
)
from tests.factories.objects.log_forwarding_profile import (
    LogForwardingProfileCreateModelFactory,
    LogForwardingProfileResponseModelFactory,
    LogForwardingProfileUpdateModelFactory,
)

# -------------------- Test Classes for Pydantic Models --------------------


class TestLogForwardingProfileCreateModel:
    """Tests for LogForwardingProfileCreateModel validation."""

    def test_invalid_data_error(self):
        """Test that ValidationError is raised when invalid data is provided."""
        data = {"invalid_field": "test"}
        with pytest.raises(ValidationError) as exc_info:
            LogForwardingProfileCreateModel(**data)
        error_msg = str(exc_info.value)
        assert "validation error for LogForwardingProfileCreateModel" in error_msg
        assert "name\n  Field required" in error_msg

    def test_missing_required_fields(self):
        """Test validation when required fields are missing."""
        data = {"name": "test-profile"}
        with pytest.raises(ValidationError) as exc_info:
            LogForwardingProfileCreateModel(**data)
        error_msg = str(exc_info.value)
        assert "1 validation error for LogForwardingProfileCreateModel" in error_msg

    def test_multiple_containers_error(self):
        """Test validation when multiple containers are provided."""
        data = LogForwardingProfileCreateModelFactory.build_with_multiple_containers()

        with pytest.raises(ValueError) as exc_info:
            LogForwardingProfileCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_no_container_error(self):
        """Test validation when no container is provided."""
        data = LogForwardingProfileCreateModelFactory.build_with_no_containers()

        with pytest.raises(ValueError) as exc_info:
            LogForwardingProfileCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_invalid_match_list_item(self):
        """Test validation for invalid match_list item configuration."""
        data = LogForwardingProfileCreateModelFactory.build_with_invalid_match_list()

        with pytest.raises(ValidationError) as exc_info:
            LogForwardingProfileCreateModel(**data)
        error_msg = str(exc_info.value)
        assert "log_type" in error_msg
        assert "Input should be" in error_msg

    def test_valid_model_with_folder(self):
        """Test validation with valid data using folder container."""
        data = LogForwardingProfileCreateModelFactory.build_valid(folder="My Folder")
        model = LogForwardingProfileCreateModel(**data)
        assert model.name == data["name"]
        assert model.folder == data["folder"]
        assert model.snippet is None
        assert model.device is None
        assert len(model.match_list) == len(data["match_list"])

    def test_valid_model_with_snippet(self):
        """Test validation with valid data using snippet container."""
        data = LogForwardingProfileCreateModelFactory.build_valid()
        data.pop("folder")
        data["snippet"] = "Test Snippet"

        model = LogForwardingProfileCreateModel(**data)
        assert model.name == data["name"]
        assert model.snippet == data["snippet"]
        assert model.folder is None
        assert model.device is None

    def test_valid_model_with_device(self):
        """Test validation with valid data using device container."""
        data = LogForwardingProfileCreateModelFactory.build_valid()
        data.pop("folder")
        data["device"] = "Test Device"

        model = LogForwardingProfileCreateModel(**data)
        assert model.name == data["name"]
        assert model.device == data["device"]
        assert model.folder is None
        assert model.snippet is None


class TestLogForwardingProfileUpdateModel:
    """Tests for LogForwardingProfileUpdateModel validation."""

    def test_invalid_data_error(self):
        """Test that ValidationError is raised when invalid data is provided."""
        data = {"invalid_field": "test"}
        with pytest.raises(ValidationError) as exc_info:
            LogForwardingProfileUpdateModel(**data)
        error_msg = str(exc_info.value)
        assert "validation error" in error_msg
        assert "id\n  Field required" in error_msg

    def test_missing_id(self):
        """Test validation when 'id' field is missing."""
        data = LogForwardingProfileUpdateModelFactory.build_without_id()
        with pytest.raises(ValidationError) as exc_info:
            LogForwardingProfileUpdateModel(**data)
        assert "id\n  Field required" in str(exc_info.value)

    def test_invalid_id_format(self):
        """Test validation for invalid UUID format."""
        data = LogForwardingProfileUpdateModelFactory.build_valid()
        data["id"] = "not-a-uuid"  # Invalid UUID format
        with pytest.raises(ValidationError) as exc_info:
            LogForwardingProfileUpdateModel(**data)
        assert "id\n  Input should be a valid UUID" in str(exc_info.value)

    def test_valid_model(self):
        """Test validation with valid data."""
        data = LogForwardingProfileUpdateModelFactory.build_valid()
        model = LogForwardingProfileUpdateModel(**data)
        assert model.id == UUID(data["id"])
        assert model.name == data["name"]
        assert len(model.match_list) == len(data["match_list"])
        assert model.folder == data["folder"]

    def test_minimal_update(self):
        """Test updating with minimal required fields."""
        data = {
            "id": "12345678-1234-5678-1234-567812345678",
            "name": "minimal-profile",
            "match_list": [
                {
                    "name": "minimal-match",
                    "log_type": "traffic",
                    "filter": "addr.src in 10.0.0.0/8",
                }
            ],
            "folder": "My Folder",
        }
        model = LogForwardingProfileUpdateModel(**data)
        assert model.id == UUID(data["id"])
        assert model.name == data["name"]
        assert model.match_list[0].name == "minimal-match"
        assert model.description is None
        assert model.enhanced_application_logging is None


class TestLogForwardingProfileResponseModel:
    """Tests for LogForwardingProfileResponseModel validation."""

    def test_valid_model(self):
        """Test validation with valid response data."""
        data = LogForwardingProfileResponseModelFactory.build_valid()
        model = LogForwardingProfileResponseModel(**data)
        assert model.id == UUID(data["id"])
        assert model.name == data["name"]
        assert model.folder == data["folder"]
        assert len(model.match_list) == len(data["match_list"])

    def test_with_snippet(self):
        """Test validation with snippet container."""
        data = LogForwardingProfileResponseModelFactory.build_valid()
        data.pop("folder")
        data["snippet"] = "Test Snippet"

        model = LogForwardingProfileResponseModel(**data)
        assert model.id == UUID(data["id"])
        assert model.name == data["name"]
        assert model.snippet == data["snippet"]
        assert model.folder is None
        assert model.device is None

    def test_with_device(self):
        """Test validation with device container."""
        data = LogForwardingProfileResponseModelFactory.build_valid()
        data.pop("folder")
        data["device"] = "Test Device"

        model = LogForwardingProfileResponseModel(**data)
        assert model.id == UUID(data["id"])
        assert model.name == data["name"]
        assert model.device == data["device"]
        assert model.folder is None
        assert model.snippet is None

    def test_predefined_snippet_without_id(self):
        """Test with predefined-snippet doesn't require ID."""
        data = LogForwardingProfileResponseModelFactory.build_predefined_snippet()
        model = LogForwardingProfileResponseModel(**data)
        assert model.id is None
        assert model.name == data["name"]
        assert model.snippet == "predefined-snippet"

    def test_non_predefined_missing_id_error(self):
        """Test that non-predefined profiles require ID."""
        data = LogForwardingProfileResponseModelFactory.build_without_id()
        with pytest.raises(ValueError) as exc_info:
            LogForwardingProfileResponseModel(**data)
        assert "ID is required for non-predefined profiles" in str(exc_info.value)

    def test_with_enhanced_application_logging(self):
        """Test with enhanced_application_logging field."""
        data = LogForwardingProfileResponseModelFactory.build_valid(
            enhanced_application_logging=True
        )
        model = LogForwardingProfileResponseModel(**data)
        assert model.enhanced_application_logging is True

    def test_missing_required_fields(self):
        """Test validation when required fields are missing."""
        data = LogForwardingProfileResponseModelFactory.build_without_id()
        # Remove required fields
        data.pop("name", None)
        data.pop("match_list", None)

        with pytest.raises(ValidationError) as exc_info:
            LogForwardingProfileResponseModel(**data)
        error_msg = str(exc_info.value)
        assert "validation error" in error_msg
        assert "name\n  Field required" in error_msg
