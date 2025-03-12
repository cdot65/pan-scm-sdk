# tests/scm/models/objects/test_syslog_server_profiles_models.py

from uuid import UUID

# External libraries
import pytest
from pydantic import ValidationError

# Local SDK imports
from scm.models.objects.syslog_server_profiles import (
    SyslogServerProfileCreateModel,
    SyslogServerProfileUpdateModel,
    SyslogServerProfileResponseModel,
    SyslogServerModel,
    FormatModel,
    EscapingModel,
)


# -------------------- Helper Functions --------------------


def create_valid_server():
    """Helper function to create a valid server model dict."""
    return {
        "name": "test-server",
        "server": "192.168.1.100",
        "transport": "UDP",
        "port": 514,
        "format": "BSD",
        "facility": "LOG_USER",
    }


def create_valid_format():
    """Helper function to create a valid format model dict."""
    return {
        "traffic": "$format_string_traffic",
        "threat": "$format_string_threat",
        "escaping": {"escape_character": "\\", "escaped_characters": "%"},
    }


def create_valid_profile_data(container_type="folder"):
    """Helper function to create a valid syslog server profile data dict."""
    data = {
        "name": "test-syslog-profile",
        "servers": {"name": create_valid_server()},
        "format": create_valid_format(),
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


class TestSyslogServerModel:
    """Tests for SyslogServerModel validation."""

    def test_valid_server(self):
        """Test that a valid server configuration is accepted."""
        server_data = create_valid_server()
        server = SyslogServerModel(**server_data)
        assert server.name == server_data["name"]
        assert server.server == server_data["server"]
        assert server.transport == server_data["transport"]
        assert server.port == server_data["port"]
        assert server.format == server_data["format"]
        assert server.facility == server_data["facility"]

    def test_invalid_transport(self):
        """Test that an invalid transport protocol is rejected."""
        server_data = create_valid_server()
        server_data["transport"] = "INVALID"

        with pytest.raises(ValidationError) as exc_info:
            SyslogServerModel(**server_data)
        error_msg = str(exc_info.value)
        assert "transport" in error_msg
        assert "Input should be 'UDP' or 'TCP'" in error_msg

    def test_invalid_format(self):
        """Test that an invalid format is rejected."""
        server_data = create_valid_server()
        server_data["format"] = "INVALID"

        with pytest.raises(ValidationError) as exc_info:
            SyslogServerModel(**server_data)
        error_msg = str(exc_info.value)
        assert "format" in error_msg
        assert "Input should be 'BSD' or 'IETF'" in error_msg

    def test_invalid_facility(self):
        """Test that an invalid facility is rejected."""
        server_data = create_valid_server()
        server_data["facility"] = "INVALID"

        with pytest.raises(ValidationError) as exc_info:
            SyslogServerModel(**server_data)
        error_msg = str(exc_info.value)
        assert "facility" in error_msg
        assert "Input should be 'LOG_USER'" in error_msg

    def test_port_range(self):
        """Test port number validation."""
        server_data = create_valid_server()

        # Test port below minimum
        server_data["port"] = 0
        with pytest.raises(ValidationError) as exc_info:
            SyslogServerModel(**server_data)
        assert "port" in str(exc_info.value)
        assert "Input should be greater than or equal to 1" in str(exc_info.value)

        # Test port above maximum
        server_data["port"] = 65536
        with pytest.raises(ValidationError) as exc_info:
            SyslogServerModel(**server_data)
        assert "port" in str(exc_info.value)
        assert "Input should be less than or equal to 65535" in str(exc_info.value)


class TestFormatModel:
    """Tests for FormatModel validation."""

    def test_valid_format(self):
        """Test that a valid format configuration is accepted."""
        format_data = create_valid_format()
        format_model = FormatModel(**format_data)
        assert format_model.traffic == format_data["traffic"]
        assert format_model.threat == format_data["threat"]
        assert format_model.escaping.escape_character == format_data["escaping"]["escape_character"]
        assert (
            format_model.escaping.escaped_characters
            == format_data["escaping"]["escaped_characters"]
        )

    def test_escaping_model(self):
        """Test EscapingModel validation."""
        escaping_data = {"escape_character": "\\", "escaped_characters": "%$[]"}
        escaping = EscapingModel(**escaping_data)
        assert escaping.escape_character == escaping_data["escape_character"]
        assert escaping.escaped_characters == escaping_data["escaped_characters"]

    def test_escape_character_length(self):
        """Test that escape_character must be a single character."""
        escaping_data = {
            "escape_character": "\\\\",  # More than one character
            "escaped_characters": "%",
        }
        with pytest.raises(ValidationError) as exc_info:
            EscapingModel(**escaping_data)
        assert "escape_character" in str(exc_info.value)
        assert "String should have at most 1 character" in str(exc_info.value)


class TestSyslogServerProfileCreateModel:
    """Tests for SyslogServerProfileCreateModel validation."""

    def test_invalid_data_error(self):
        """Test that ValidationError is raised when invalid data is provided."""
        data = {"invalid_field": "test"}
        with pytest.raises(ValidationError) as exc_info:
            SyslogServerProfileCreateModel(**data)
        error_msg = str(exc_info.value)
        assert "name\n  Field required" in error_msg
        assert "servers\n  Field required" in error_msg

    def test_missing_required_fields(self):
        """Test validation when required fields are missing."""
        data = {"name": "test-profile"}
        with pytest.raises(ValidationError) as exc_info:
            SyslogServerProfileCreateModel(**data)
        error_msg = str(exc_info.value)
        assert "servers\n  Field required" in error_msg

    def test_multiple_containers_error(self):
        """Test validation when multiple containers are provided."""
        data = create_valid_profile_data()
        data["snippet"] = "TestSnippet"  # Adding a second container

        with pytest.raises(ValueError) as exc_info:
            SyslogServerProfileCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_no_container_error(self):
        """Test validation when no container is provided."""
        data = create_valid_profile_data()
        data.pop("folder")  # Remove the container

        with pytest.raises(ValueError) as exc_info:
            SyslogServerProfileCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_valid_model_with_folder(self):
        """Test validation with valid data using folder container."""
        data = create_valid_profile_data("folder")
        model = SyslogServerProfileCreateModel(**data)
        assert model.name == data["name"]
        assert model.servers == data["servers"]
        assert model.folder == data["folder"]
        assert model.format.traffic == data["format"]["traffic"]
        assert model.format.threat == data["format"]["threat"]

    def test_valid_model_with_snippet(self):
        """Test validation with valid data using snippet container."""
        data = create_valid_profile_data("snippet")
        model = SyslogServerProfileCreateModel(**data)
        assert model.name == data["name"]
        assert model.snippet == data["snippet"]
        assert model.folder is None
        assert model.device is None

    def test_valid_model_with_device(self):
        """Test validation with valid data using device container."""
        data = create_valid_profile_data("device")
        model = SyslogServerProfileCreateModel(**data)
        assert model.name == data["name"]
        assert model.device == data["device"]
        assert model.folder is None
        assert model.snippet is None


class TestSyslogServerProfileUpdateModel:
    """Tests for SyslogServerProfileUpdateModel validation."""

    def test_invalid_data_error(self):
        """Test that ValidationError is raised when invalid data is provided."""
        data = {"invalid": "data"}
        with pytest.raises(ValidationError) as exc_info:
            SyslogServerProfileUpdateModel(**data)
        error_msg = str(exc_info.value)
        assert "validation error" in error_msg
        assert "name\n  Field required" in error_msg
        assert "servers\n  Field required" in error_msg
        assert "id\n  Field required" in error_msg

    def test_missing_id(self):
        """Test validation when 'id' field is missing."""
        data = create_valid_profile_data()
        with pytest.raises(ValidationError) as exc_info:
            SyslogServerProfileUpdateModel(**data)
        assert "id\n  Field required" in str(exc_info.value)

    def test_invalid_id_format(self):
        """Test validation for invalid UUID format."""
        data = create_valid_profile_data()
        data["id"] = "invalid-uuid"

        with pytest.raises(ValidationError) as exc_info:
            SyslogServerProfileUpdateModel(**data)
        assert "id\n  Input should be a valid UUID" in str(exc_info.value)

    def test_valid_model(self):
        """Test validation with valid data."""
        data = create_valid_profile_data()
        data["id"] = "123e4567-e89b-12d3-a456-426655440000"

        model = SyslogServerProfileUpdateModel(**data)
        assert model.id == UUID(data["id"])
        assert model.name == data["name"]
        assert model.servers == data["servers"]
        assert model.folder == data["folder"]

    def test_minimal_update(self):
        """Test updating with minimal required fields."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "updated-profile",
            "servers": {"server1": create_valid_server()},
        }

        model = SyslogServerProfileUpdateModel(**data)
        assert model.id == UUID(data["id"])
        assert model.name == data["name"]
        assert model.servers == data["servers"]
        assert model.format is None
        assert model.folder is None
        assert model.snippet is None
        assert model.device is None


class TestSyslogServerProfileResponseModel:
    """Tests for SyslogServerProfileResponseModel validation."""

    def test_valid_model(self):
        """Test validation with valid response data."""
        data = create_valid_profile_data()
        data["id"] = "123e4567-e89b-12d3-a456-426655440000"

        model = SyslogServerProfileResponseModel(**data)
        assert model.id == UUID(data["id"])
        assert model.name == data["name"]
        assert model.servers == data["servers"]
        assert model.folder == data["folder"]
        assert model.format.traffic == data["format"]["traffic"]
        assert model.format.threat == data["format"]["threat"]

    def test_with_snippet(self):
        """Test validation with snippet container."""
        data = create_valid_profile_data("snippet")
        data["id"] = "123e4567-e89b-12d3-a456-426655440000"

        model = SyslogServerProfileResponseModel(**data)
        assert model.id == UUID(data["id"])
        assert model.snippet == data["snippet"]
        assert model.folder is None
        assert model.device is None

    def test_with_device(self):
        """Test validation with device container."""
        data = create_valid_profile_data("device")
        data["id"] = "123e4567-e89b-12d3-a456-426655440000"

        model = SyslogServerProfileResponseModel(**data)
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
            SyslogServerProfileResponseModel(**data)
        error_msg = str(exc_info.value)
        assert "2 validation errors for SyslogServerProfileResponseModel" in error_msg
        assert "name\n  Field required" in error_msg
        assert "servers\n  Field required" in error_msg
