# tests/scm/models/objects/test_syslog_server_profiles_models.py

from uuid import UUID

# External libraries
import pytest
from pydantic import ValidationError

# Local SDK imports
from scm.models.objects.syslog_server_profiles import (
    EscapingModel, SyslogServerModel, SyslogServerProfileCreateModel,
    SyslogServerProfileResponseModel, SyslogServerProfileUpdateModel)
# Import the new factories
from tests.test_factories.objects.syslog_server_profiles import (
    EscapingModelFactory, FormatModelFactory, SyslogServerModelFactory,
    SyslogServerProfileCreateModelFactory,
    SyslogServerProfileResponseModelFactory,
    SyslogServerProfileUpdateModelFactory)

# -------------------- Test Classes for Pydantic Models --------------------


class TestSyslogServerModel:
    """Tests for SyslogServerModel validation."""

    def test_valid_server(self):
        """Test that a valid server configuration is accepted."""
        server = SyslogServerModelFactory()
        assert server.name is not None
        assert server.server is not None
        assert server.transport == "UDP"
        assert server.port == 514
        assert server.format == "BSD"
        assert server.facility == "LOG_USER"

    def test_invalid_transport(self):
        """Test that an invalid transport protocol is rejected."""
        server_data = SyslogServerModelFactory.build().__dict__
        server_data["transport"] = "INVALID"

        with pytest.raises(ValidationError) as exc_info:
            SyslogServerModel(**server_data)
        error_msg = str(exc_info.value)
        assert "transport" in error_msg
        assert "Input should be 'UDP' or 'TCP'" in error_msg

    def test_invalid_format(self):
        """Test that an invalid format is rejected."""
        server_data = SyslogServerModelFactory.build().__dict__
        server_data["format"] = "INVALID"

        with pytest.raises(ValidationError) as exc_info:
            SyslogServerModel(**server_data)
        error_msg = str(exc_info.value)
        assert "format" in error_msg
        assert "Input should be 'BSD' or 'IETF'" in error_msg

    def test_invalid_facility(self):
        """Test that an invalid facility is rejected."""
        server_data = SyslogServerModelFactory.build().__dict__
        server_data["facility"] = "INVALID"

        with pytest.raises(ValidationError) as exc_info:
            SyslogServerModel(**server_data)
        error_msg = str(exc_info.value)
        assert "facility" in error_msg
        assert "Input should be 'LOG_USER'" in error_msg

    def test_port_range(self):
        """Test port number validation."""
        server_data = SyslogServerModelFactory.build().__dict__

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
        format_model = FormatModelFactory()
        assert format_model.traffic == "$format_string_traffic"
        assert format_model.threat == "$format_string_threat"
        assert format_model.escaping.escape_character == "\\"
        assert format_model.escaping.escaped_characters == "%$[]"

    def test_escaping_model(self):
        """Test EscapingModel validation."""
        escaping = EscapingModelFactory()
        assert escaping.escape_character == "\\"
        assert escaping.escaped_characters == "%$[]"

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
        assert "server\n  Field required" in error_msg

    def test_missing_required_fields(self):
        """Test validation when required fields are missing."""
        data = {"name": "test-profile"}
        with pytest.raises(ValidationError) as exc_info:
            SyslogServerProfileCreateModel(**data)
        error_msg = str(exc_info.value)
        assert "server\n  Field required" in error_msg

    def test_multiple_containers_error(self):
        """Test validation when multiple containers are provided."""
        data = SyslogServerProfileCreateModelFactory.build_with_multiple_containers()

        with pytest.raises(ValueError) as exc_info:
            SyslogServerProfileCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_no_container_error(self):
        """Test validation when no container is provided."""
        model_data = SyslogServerProfileCreateModelFactory.build(folder="Shared").__dict__
        model_data.pop("folder")  # Remove the container

        with pytest.raises(ValueError) as exc_info:
            SyslogServerProfileCreateModel(**model_data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_with_folder(self):
        """Test creation with folder container."""
        model = SyslogServerProfileCreateModelFactory()
        assert model.folder == "Shared"
        assert model.snippet is None
        assert model.device is None
        assert len(model.server) > 0

    def test_with_snippet(self):
        """Test creation with snippet container."""
        model = SyslogServerProfileCreateModelFactory.with_snippet()
        assert model.snippet == "TestSnippet"
        assert model.folder is None
        assert model.device is None
        assert len(model.server) > 0

    def test_with_device(self):
        """Test creation with device container."""
        model = SyslogServerProfileCreateModelFactory.with_device()
        assert model.device == "TestDevice"
        assert model.folder is None
        assert model.snippet is None
        assert len(model.server) > 0

    def test_with_multiple_servers(self):
        """Test creation with multiple server configurations."""
        model = SyslogServerProfileCreateModelFactory.with_multiple_servers(count=3)
        assert len(model.server) == 3
        assert all(isinstance(server, SyslogServerModel) for server in model.server)

    def test_with_minimal_format(self):
        """Test creation with minimal format configuration."""
        model = SyslogServerProfileCreateModelFactory.with_minimal_format()
        assert model.format is not None
        assert model.format.traffic == "$format_string_traffic"
        assert model.format.threat == "$format_string_threat"
        assert model.format.wildfire is None


class TestSyslogServerProfileUpdateModel:
    """Tests for SyslogServerProfileUpdateModel validation."""

    def test_invalid_data_error(self):
        """Test that ValidationError is raised when invalid data is provided."""
        data = {"invalid_field": "test"}
        with pytest.raises(ValidationError) as exc_info:
            SyslogServerProfileUpdateModel(**data)
        assert "id\n  Field required" in str(exc_info.value)

    def test_missing_id(self):
        """Test validation when 'id' field is missing."""
        model_data = SyslogServerProfileUpdateModelFactory.build().__dict__
        model_data.pop("id")
        with pytest.raises(ValidationError) as exc_info:
            SyslogServerProfileUpdateModel(**model_data)
        assert "id\n  Field required" in str(exc_info.value)

    def test_invalid_id_format(self):
        """Test validation for invalid UUID format."""
        model_data = SyslogServerProfileUpdateModelFactory.build().__dict__
        model_data["id"] = "invalid-uuid"
        with pytest.raises(ValidationError) as exc_info:
            SyslogServerProfileUpdateModel(**model_data)
        assert "id\n  Input should be a valid UUID" in str(exc_info.value)

    def test_valid_model(self):
        """Test validation with valid data."""
        model = SyslogServerProfileUpdateModelFactory()
        assert isinstance(model.id, UUID)
        assert model.name is not None
        assert len(model.server) > 0

    def test_updated_servers(self):
        """Test updating server list."""
        model = SyslogServerProfileUpdateModelFactory.with_updated_servers()
        assert len(model.server) == 2
        assert model.server[0].name == "updated-server-1"
        assert model.server[1].name == "updated-server-2"
        assert model.server[1].transport == "TCP"

    def test_updated_format(self):
        """Test updating format configuration."""
        model = SyslogServerProfileUpdateModelFactory.with_updated_format()
        assert model.format.traffic == "$updated_traffic_format"
        assert model.format.threat == "$updated_threat_format"


class TestSyslogServerProfileResponseModel:
    """Tests for SyslogServerProfileResponseModel validation."""

    def test_valid_model(self):
        """Test validation with valid response data."""
        model = SyslogServerProfileResponseModelFactory()
        assert isinstance(model.id, UUID)
        assert model.name is not None
        assert model.folder == "Shared"
        assert len(model.server) > 0

    def test_with_snippet(self):
        """Test validation with snippet container."""
        model = SyslogServerProfileResponseModelFactory.with_snippet()
        assert model.snippet == "TestSnippet"
        assert model.folder is None
        assert model.device is None
        assert isinstance(model.id, UUID)

    def test_with_device(self):
        """Test validation with device container."""
        model = SyslogServerProfileResponseModelFactory.with_device()
        assert model.device == "TestDevice"
        assert model.folder is None
        assert model.snippet is None
        assert isinstance(model.id, UUID)

    def test_missing_required_fields(self):
        """Test validation when required fields are missing."""
        model_data = SyslogServerProfileResponseModelFactory.build().__dict__
        model_data.pop("id")
        with pytest.raises(ValidationError) as exc_info:
            SyslogServerProfileResponseModel(**model_data)
        assert "id\n  Field required" in str(exc_info.value)
