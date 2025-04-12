# tests/scm/models/objects/test_log_forwarding_profile_models.py

from uuid import UUID

# External libraries
import pytest
from pydantic import ValidationError

# Local SDK imports
from scm.models.objects.log_forwarding_profile import (
    LogForwardingProfileCreateModel,
    LogForwardingProfileResponseModel,
    LogForwardingProfileUpdateModel,
)

# -------------------- Helper Functions --------------------


def create_valid_match_list_item():
    """Helper function to create a valid match list item dict."""
    return {
        "name": "test-match",
        "log_type": "traffic",
        "filter": "addr.src in 192.168.0.0/24",
        "send_http": ["test-http-profile"],
    }


def create_valid_profile_data(container_type="folder"):
    """Helper function to create a valid log forwarding profile data dict."""
    data = {
        "name": "test-log-profile",
        "description": "Test log forwarding profile for unit tests",
        "match_list": [create_valid_match_list_item()],
    }

    # Add the specified container
    if container_type == "folder":
        data["folder"] = "Shared"
    elif container_type == "snippet":
        data["snippet"] = "TestSnippet"
    elif container_type == "device":
        data["device"] = "TestDevice"

    return data


# -------------------- Test Classes for Pydantic Models --------------------


class TestLogForwardingProfileCreateModel:
    """Tests for LogForwardingProfileCreateModel validation."""

    def test_invalid_data_error(self):
        """Test that ValidationError is raised when invalid data is provided."""
        data = {"invalid_field": "test"}
        with pytest.raises(ValidationError) as exc_info:
            LogForwardingProfileCreateModel(**data)
        error_msg = str(exc_info.value)
        assert "name\n  Field required" in error_msg

    def test_missing_required_fields(self):
        """Test validation when required fields are missing."""
        data = {"folder": "Shared"}
        with pytest.raises(ValidationError) as exc_info:
            LogForwardingProfileCreateModel(**data)
        error_msg = str(exc_info.value)
        assert "name\n  Field required" in error_msg

    def test_multiple_containers_error(self):
        """Test validation when multiple containers are provided."""
        data = create_valid_profile_data()
        data["snippet"] = "TestSnippet"  # Adding a second container

        with pytest.raises(ValueError) as exc_info:
            LogForwardingProfileCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_no_container_error(self):
        """Test validation when no container is provided."""
        data = create_valid_profile_data()
        data.pop("folder")  # Remove the container

        with pytest.raises(ValueError) as exc_info:
            LogForwardingProfileCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_invalid_match_list_item(self):
        """Test validation for invalid match_list item configuration."""
        data = create_valid_profile_data()
        data["match_list"] = [{"name": "invalid-match", "log_type": "invalid-type"}]

        with pytest.raises(ValidationError) as exc_info:
            LogForwardingProfileCreateModel(**data)
        error_msg = str(exc_info.value)
        assert "log_type\n  Input should be" in error_msg

    def test_valid_model_with_folder(self):
        """Test validation with valid data using folder container."""
        data = create_valid_profile_data("folder")
        model = LogForwardingProfileCreateModel(**data)
        assert model.name == data["name"]
        assert len(model.match_list) == 1
        assert model.match_list[0].name == data["match_list"][0]["name"]
        assert model.match_list[0].log_type == data["match_list"][0]["log_type"]
        assert model.folder == data["folder"]
        assert model.description == data["description"]

    def test_valid_model_with_snippet(self):
        """Test validation with valid data using snippet container."""
        data = create_valid_profile_data("snippet")
        model = LogForwardingProfileCreateModel(**data)
        assert model.name == data["name"]
        assert model.snippet == data["snippet"]
        assert model.folder is None
        assert model.device is None

    def test_valid_model_with_device(self):
        """Test validation with valid data using device container."""
        data = create_valid_profile_data("device")
        model = LogForwardingProfileCreateModel(**data)
        assert model.name == data["name"]
        assert model.device == data["device"]
        assert model.folder is None
        assert model.snippet is None


class TestLogForwardingProfileUpdateModel:
    """Tests for LogForwardingProfileUpdateModel validation."""

    def test_invalid_data_error(self):
        """Test that ValidationError is raised when invalid data is provided."""
        data = {"invalid": "data"}
        with pytest.raises(ValidationError) as exc_info:
            LogForwardingProfileUpdateModel(**data)
        error_msg = str(exc_info.value)
        assert "validation error" in error_msg
        assert "name\n  Field required" in error_msg
        assert "id\n  Field required" in error_msg

    def test_missing_id(self):
        """Test validation when 'id' field is missing."""
        data = create_valid_profile_data()
        with pytest.raises(ValidationError) as exc_info:
            LogForwardingProfileUpdateModel(**data)
        assert "id\n  Field required" in str(exc_info.value)

    def test_invalid_id_format(self):
        """Test validation for invalid UUID format."""
        data = create_valid_profile_data()
        data["id"] = "invalid-uuid"

        with pytest.raises(ValidationError) as exc_info:
            LogForwardingProfileUpdateModel(**data)
        assert "id\n  Input should be a valid UUID" in str(exc_info.value)

    def test_valid_model(self):
        """Test validation with valid data."""
        data = create_valid_profile_data()
        data["id"] = "123e4567-e89b-12d3-a456-426655440000"

        model = LogForwardingProfileUpdateModel(**data)
        assert model.id == UUID(data["id"])
        assert model.name == data["name"]
        assert len(model.match_list) == 1
        assert model.match_list[0].log_type == "traffic"
        assert model.folder == data["folder"]

    def test_minimal_update(self):
        """Test updating with minimal required fields."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "updated-profile",
        }

        model = LogForwardingProfileUpdateModel(**data)
        assert model.id == UUID(data["id"])
        assert model.name == data["name"]
        assert model.match_list is None
        assert model.description is None
        assert model.folder is None
        assert model.snippet is None
        assert model.device is None


class TestLogForwardingProfileResponseModel:
    """Tests for LogForwardingProfileResponseModel validation."""

    def test_valid_model(self):
        """Test validation with valid response data."""
        data = create_valid_profile_data()
        data["id"] = "123e4567-e89b-12d3-a456-426655440000"

        model = LogForwardingProfileResponseModel(**data)
        assert model.id == UUID(data["id"])
        assert model.name == data["name"]
        assert model.description == data["description"]
        assert len(model.match_list) == 1
        assert model.match_list[0].log_type == "traffic"
        assert model.folder == data["folder"]

    def test_with_snippet(self):
        """Test validation with snippet container."""
        data = create_valid_profile_data("snippet")
        data["id"] = "123e4567-e89b-12d3-a456-426655440000"

        model = LogForwardingProfileResponseModel(**data)
        assert model.id == UUID(data["id"])
        assert model.snippet == data["snippet"]
        assert model.folder is None
        assert model.device is None

    def test_with_device(self):
        """Test validation with device container."""
        data = create_valid_profile_data("device")
        data["id"] = "123e4567-e89b-12d3-a456-426655440000"

        model = LogForwardingProfileResponseModel(**data)
        assert model.id == UUID(data["id"])
        assert model.device == data["device"]
        assert model.folder is None
        assert model.snippet is None

    def test_predefined_snippet_without_id(self):
        """Test with predefined-snippet doesn't require ID."""
        data = {
            "name": "Predefined Profile",
            "snippet": "predefined-snippet",
            "enhanced_application_logging": True,
            "match_list": [
                {
                    "name": "traffic-match",
                    "log_type": "traffic",
                    "filter": "All Logs",
                    "send_to_panorama": True,
                    "quarantine": False,
                }
            ],
        }

        model = LogForwardingProfileResponseModel(**data)
        assert model.id is None
        assert model.name == "Predefined Profile"
        assert model.snippet == "predefined-snippet"
        assert model.enhanced_application_logging is True
        assert len(model.match_list) == 1
        assert model.match_list[0].send_to_panorama is True
        assert model.match_list[0].quarantine is False

    def test_non_predefined_missing_id_error(self):
        """Test that non-predefined profiles require ID."""
        data = create_valid_profile_data()

        with pytest.raises(ValueError) as exc_info:
            LogForwardingProfileResponseModel(**data)
        assert "ID is required for non-predefined profiles" in str(exc_info.value)

    def test_with_enhanced_application_logging(self):
        """Test with enhanced_application_logging field."""
        data = create_valid_profile_data()
        data["id"] = "123e4567-e89b-12d3-a456-426655440000"
        data["enhanced_application_logging"] = True
        data["match_list"][0]["send_to_panorama"] = True
        data["match_list"][0]["quarantine"] = False

        model = LogForwardingProfileResponseModel(**data)
        assert model.enhanced_application_logging is True
        assert model.match_list[0].send_to_panorama is True
        assert model.match_list[0].quarantine is False

    def test_missing_required_fields(self):
        """Test validation when required fields are missing."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
        }
        with pytest.raises(ValidationError) as exc_info:
            LogForwardingProfileResponseModel(**data)
        error_msg = str(exc_info.value)
        assert "name\n  Field required" in error_msg
