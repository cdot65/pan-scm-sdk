# tests/scm/models/objects/test_http_server_profiles_models.py

from uuid import UUID

# External libraries
import pytest
from pydantic import ValidationError

# Local SDK imports
from scm.models.objects.http_server_profiles import (
    HTTPServerProfileCreateModel,
    HTTPServerProfileResponseModel,
    HTTPServerProfileUpdateModel,
)
from tests.test_factories.objects.http_server_profiles import (
    HTTPServerProfileCreateModelFactory,
    HTTPServerProfileResponseModelFactory,
    HTTPServerProfileUpdateModelFactory,
)

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
        data = HTTPServerProfileCreateModelFactory.build_with_multiple_containers()

        with pytest.raises(ValueError) as exc_info:
            HTTPServerProfileCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_no_container_error(self):
        """Test validation when no container is provided."""
        data = HTTPServerProfileCreateModelFactory.build_with_no_containers()

        with pytest.raises(ValueError) as exc_info:
            HTTPServerProfileCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_invalid_server_config(self):
        """Test validation for invalid server configuration."""
        data = HTTPServerProfileCreateModelFactory.build_valid()
        data["server"] = [{"name": "test-server", "port": 80}]  # Missing required fields

        with pytest.raises(ValidationError) as exc_info:
            HTTPServerProfileCreateModel(**data)
        error_msg = str(exc_info.value)
        assert "server" in error_msg
        assert "address\n  Field required" in error_msg
        assert "protocol\n  Field required" in error_msg

    def test_invalid_protocol(self):
        """Test validation for invalid protocol value."""
        data = HTTPServerProfileCreateModelFactory.build_valid()
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
        data = HTTPServerProfileCreateModelFactory.build_valid(folder="Test Folder")
        model = HTTPServerProfileCreateModel(**data)
        assert model.name == data["name"]
        assert len(model.server) == len(data["server"])
        assert model.server[0].name == data["server"][0]["name"]
        assert model.folder == data["folder"]
        assert model.snippet is None
        assert model.device is None

    def test_valid_model_with_snippet(self):
        """Test validation with valid data using snippet container."""
        data = HTTPServerProfileCreateModelFactory.build_valid()
        data.pop("folder")
        data["snippet"] = "Test Snippet"

        model = HTTPServerProfileCreateModel(**data)
        assert model.name == data["name"]
        assert len(model.server) == len(data["server"])
        assert model.snippet == data["snippet"]
        assert model.folder is None
        assert model.device is None

    def test_valid_model_with_device(self):
        """Test validation with valid data using device container."""
        data = HTTPServerProfileCreateModelFactory.build_valid()
        data.pop("folder")
        data["device"] = "Test Device"

        model = HTTPServerProfileCreateModel(**data)
        assert model.name == data["name"]
        assert len(model.server) == len(data["server"])
        assert model.device == data["device"]
        assert model.folder is None
        assert model.snippet is None


class TestHTTPServerProfileUpdateModel:
    """Tests for HTTPServerProfileUpdateModel validation."""

    def test_invalid_data_error(self):
        """Test that ValidationError is raised when invalid data is provided."""
        data = {"invalid_field": "test"}
        with pytest.raises(ValidationError) as exc_info:
            HTTPServerProfileUpdateModel(**data)
        error_msg = str(exc_info.value)
        assert "3 validation errors for HTTPServerProfileUpdateModel" in error_msg
        assert "id\n  Field required" in error_msg
        assert "name\n  Field required" in error_msg
        assert "server\n  Field required" in error_msg

    def test_missing_id(self):
        """Test validation when 'id' field is missing."""
        data = HTTPServerProfileUpdateModelFactory.build_without_id()
        with pytest.raises(ValidationError) as exc_info:
            HTTPServerProfileUpdateModel(**data)
        error_msg = str(exc_info.value)
        assert "id\n  Field required" in error_msg

    def test_invalid_id_format(self):
        """Test validation for invalid UUID format."""
        data = HTTPServerProfileUpdateModelFactory.build_with_invalid_id()
        with pytest.raises(ValidationError) as exc_info:
            HTTPServerProfileUpdateModel(**data)
        error_msg = str(exc_info.value)
        assert "id\n  Input should be a valid UUID" in error_msg

    def test_valid_model(self):
        """Test validation with valid data."""
        data = HTTPServerProfileUpdateModelFactory.build_valid()
        model = HTTPServerProfileUpdateModel(**data)
        assert model.id == UUID(data["id"])
        assert model.name == data["name"]
        assert len(model.server) == len(data["server"])

    def test_minimal_update(self):
        """Test updating with minimal required fields."""
        data = {
            "id": "12345678-1234-5678-1234-567812345678",
            "name": "minimal-profile",
            "server": [
                {
                    "name": "minimal-server",
                    "address": "192.168.1.1",
                    "protocol": "HTTP",
                    "port": 8080,
                }
            ],
        }
        model = HTTPServerProfileUpdateModel(**data)
        assert model.id == UUID(data["id"])
        assert model.name == data["name"]
        assert model.server[0].name == data["server"][0]["name"]
        assert model.description is None
        assert model.tag_registration is None
        assert model.format is None


class TestHTTPServerProfileResponseModel:
    """Tests for HTTPServerProfileResponseModel validation."""

    def test_valid_model(self):
        """Test validation with valid response data."""
        data = HTTPServerProfileResponseModelFactory.build_valid()
        model = HTTPServerProfileResponseModel(**data)
        assert model.id == UUID(data["id"])
        assert model.name == data["name"]
        assert model.folder == data["folder"]
        assert len(model.server) == len(data["server"])

    def test_with_snippet(self):
        """Test validation with snippet container."""
        data = HTTPServerProfileResponseModelFactory.build_valid()
        data.pop("folder")
        data["snippet"] = "Test Snippet"

        model = HTTPServerProfileResponseModel(**data)
        assert model.id == UUID(data["id"])
        assert model.name == data["name"]
        assert model.snippet == data["snippet"]
        assert model.folder is None
        assert model.device is None

    def test_with_device(self):
        """Test validation with device container."""
        data = HTTPServerProfileResponseModelFactory.build_valid()
        data.pop("folder")
        data["device"] = "Test Device"

        model = HTTPServerProfileResponseModel(**data)
        assert model.id == UUID(data["id"])
        assert model.name == data["name"]
        assert model.device == data["device"]
        assert model.folder is None
        assert model.snippet is None

    def test_missing_required_fields(self):
        """Test validation when required fields are missing."""
        data = HTTPServerProfileResponseModelFactory.build_without_id()
        with pytest.raises(ValidationError) as exc_info:
            HTTPServerProfileResponseModel(**data)
        error_msg = str(exc_info.value)
        assert "id\n  Field required" in error_msg
