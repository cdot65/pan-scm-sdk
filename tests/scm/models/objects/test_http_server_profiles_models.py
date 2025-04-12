# tests/scm/models/objects/test_http_server_profiles_models.py

from uuid import UUID

# External libraries
import pytest
from pydantic import ValidationError

# Local SDK imports
from scm.models.objects.http_server_profiles import (
    HTTPServerProfileCreateModel, HTTPServerProfileResponseModel,
    HTTPServerProfileUpdateModel)

# -------------------- Helper Functions --------------------


def create_valid_server():
    """Helper function to create a valid server model dict."""
    return {"name": "test-server", "address": "192.168.1.100", "protocol": "HTTP", "port": 80}


def create_valid_https_server():
    """Helper function to create a valid HTTPS server model dict."""
    return {
        "name": "test-https-server",
        "address": "secure.example.com",
        "protocol": "HTTPS",
        "port": 443,
        "tls_version": "1.2",
        "certificate_profile": "default",
        "http_method": "POST",
    }


def create_valid_profile_data(container_type="folder"):
    """Helper function to create a valid HTTP server profile data dict."""
    data = {
        "name": "test-http-profile",
        "description": "Test HTTP server profile for unit tests",
        "server": [create_valid_server(), create_valid_https_server()],
        "tag_registration": True,
        "format": {
            "traffic": {},
            "threat": {},
            "url": {},
        },
    }

    # Add the specified container
    if container_type == "folder":
        data["folder"] = "Security Profiles"
    elif container_type == "snippet":
        data["snippet"] = "TestSnippet"
    elif container_type == "device":
        data["device"] = "TestDevice"

    return data


# -------------------- Test Classes for Pydantic Models --------------------


class TestHTTPServerProfileCreateModel:
    """Tests for HTTPServerProfileCreateModel validation."""

    def test_invalid_data_error(self):
        """Test that ValidationError is raised when invalid data is provided."""
        data = {"invalid_field": "test"}
        with pytest.raises(ValidationError) as exc_info:
            HTTPServerProfileCreateModel(**data)
        error_msg = str(exc_info.value)
        assert "2 validation errors for HTTPServerProfileCreateModel" in error_msg
        assert "name\n  Field required" in error_msg
        assert "server\n  Field required" in error_msg

    def test_missing_required_fields(self):
        """Test validation when required fields are missing."""
        data = {"name": "test-profile"}
        with pytest.raises(ValidationError) as exc_info:
            HTTPServerProfileCreateModel(**data)
        error_msg = str(exc_info.value)
        assert "1 validation error for HTTPServerProfileCreateModel" in error_msg
        assert "server\n  Field required" in error_msg

    def test_multiple_containers_error(self):
        """Test validation when multiple containers are provided."""
        data = create_valid_profile_data()
        data["snippet"] = "TestSnippet"  # Adding a second container

        with pytest.raises(ValueError) as exc_info:
            HTTPServerProfileCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_no_container_error(self):
        """Test validation when no container is provided."""
        data = create_valid_profile_data()
        data.pop("folder")  # Remove the container

        with pytest.raises(ValueError) as exc_info:
            HTTPServerProfileCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_invalid_server_config(self):
        """Test validation for invalid server configuration."""
        data = create_valid_profile_data()
        data["server"] = [{"name": "test-server", "port": 80}]  # Missing required fields

        with pytest.raises(ValidationError) as exc_info:
            HTTPServerProfileCreateModel(**data)
        error_msg = str(exc_info.value)
        assert "server" in error_msg
        assert "address\n  Field required" in error_msg
        assert "protocol\n  Field required" in error_msg

    def test_invalid_protocol(self):
        """Test validation for invalid protocol value."""
        data = create_valid_profile_data()
        data["server"] = [
            {
                "name": "test-server",
                "address": "192.168.1.100",
                "protocol": "INVALID",  # Invalid protocol
                "port": 80,
            }
        ]

        with pytest.raises(ValidationError) as exc_info:
            HTTPServerProfileCreateModel(**data)
        error_msg = str(exc_info.value)
        assert "protocol\n  Input should be 'HTTP' or 'HTTPS'" in error_msg

    def test_valid_model_with_folder(self):
        """Test validation with valid data using folder container."""
        data = create_valid_profile_data("folder")
        model = HTTPServerProfileCreateModel(**data)
        assert model.name == data["name"]
        assert len(model.server) == 2
        assert model.server[0].name == data["server"][0]["name"]
        assert model.server[1].protocol == data["server"][1]["protocol"]
        assert model.folder == data["folder"]
        assert model.tag_registration == data["tag_registration"]
        assert model.format is not None
        assert "traffic" in model.format

    def test_valid_model_with_snippet(self):
        """Test validation with valid data using snippet container."""
        data = create_valid_profile_data("snippet")
        model = HTTPServerProfileCreateModel(**data)
        assert model.name == data["name"]
        assert model.snippet == data["snippet"]
        assert model.folder is None
        assert model.device is None

    def test_valid_model_with_device(self):
        """Test validation with valid data using device container."""
        data = create_valid_profile_data("device")
        model = HTTPServerProfileCreateModel(**data)
        assert model.name == data["name"]
        assert model.device == data["device"]
        assert model.folder is None
        assert model.snippet is None


class TestHTTPServerProfileUpdateModel:
    """Tests for HTTPServerProfileUpdateModel validation."""

    def test_invalid_data_error(self):
        """Test that ValidationError is raised when invalid data is provided."""
        data = {"invalid": "data"}
        with pytest.raises(ValidationError) as exc_info:
            HTTPServerProfileUpdateModel(**data)
        error_msg = str(exc_info.value)
        assert "validation error" in error_msg
        assert "name\n  Field required" in error_msg
        assert "server\n  Field required" in error_msg
        assert "id\n  Field required" in error_msg

    def test_missing_id(self):
        """Test validation when 'id' field is missing."""
        data = create_valid_profile_data()
        with pytest.raises(ValidationError) as exc_info:
            HTTPServerProfileUpdateModel(**data)
        assert "id\n  Field required" in str(exc_info.value)

    def test_invalid_id_format(self):
        """Test validation for invalid UUID format."""
        data = create_valid_profile_data()
        data["id"] = "invalid-uuid"

        with pytest.raises(ValidationError) as exc_info:
            HTTPServerProfileUpdateModel(**data)
        assert "id\n  Input should be a valid UUID" in str(exc_info.value)

    def test_valid_model(self):
        """Test validation with valid data."""
        data = create_valid_profile_data()
        data["id"] = "123e4567-e89b-12d3-a456-426655440000"

        model = HTTPServerProfileUpdateModel(**data)
        assert model.id == UUID(data["id"])
        assert model.name == data["name"]
        assert len(model.server) == 2
        assert model.server[0].protocol == "HTTP"
        assert model.server[1].protocol == "HTTPS"
        assert model.folder == data["folder"]

    def test_minimal_update(self):
        """Test updating with minimal required fields."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "updated-profile",
            "server": [create_valid_server()],
        }

        model = HTTPServerProfileUpdateModel(**data)
        assert model.id == UUID(data["id"])
        assert model.name == data["name"]
        assert len(model.server) == 1
        assert model.server[0].name == data["server"][0]["name"]
        assert model.tag_registration is None
        assert model.format is None
        assert model.folder is None
        assert model.snippet is None
        assert model.device is None


class TestHTTPServerProfileResponseModel:
    """Tests for HTTPServerProfileResponseModel validation."""

    def test_valid_model(self):
        """Test validation with valid response data."""
        data = create_valid_profile_data()
        data["id"] = "123e4567-e89b-12d3-a456-426655440000"

        model = HTTPServerProfileResponseModel(**data)
        assert model.id == UUID(data["id"])
        assert model.name == data["name"]
        assert model.description == data["description"]
        assert len(model.server) == 2
        assert model.server[0].protocol == "HTTP"
        assert model.server[1].protocol == "HTTPS"
        assert model.folder == data["folder"]
        assert model.tag_registration == data["tag_registration"]

    def test_with_snippet(self):
        """Test validation with snippet container."""
        data = create_valid_profile_data("snippet")
        data["id"] = "123e4567-e89b-12d3-a456-426655440000"

        model = HTTPServerProfileResponseModel(**data)
        assert model.id == UUID(data["id"])
        assert model.snippet == data["snippet"]
        assert model.folder is None
        assert model.device is None

    def test_with_device(self):
        """Test validation with device container."""
        data = create_valid_profile_data("device")
        data["id"] = "123e4567-e89b-12d3-a456-426655440000"

        model = HTTPServerProfileResponseModel(**data)
        assert model.id == UUID(data["id"])
        assert model.device == data["device"]
        assert model.folder is None
        assert model.snippet is None

    def test_missing_required_fields(self):
        """Test validation when required fields are missing."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
        }
        with pytest.raises(ValidationError) as exc_info:
            HTTPServerProfileResponseModel(**data)
        error_msg = str(exc_info.value)
        assert "2 validation errors for HTTPServerProfileResponseModel" in error_msg
        assert "name\n  Field required" in error_msg
        assert "server\n  Field required" in error_msg
