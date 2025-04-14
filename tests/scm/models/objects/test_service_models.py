# tests/scm/models/objects/test_service_models.py

# External libraries
import pytest
from pydantic import ValidationError

# Local SDK imports
from scm.models.objects import ServiceCreateModel, ServiceResponseModel, ServiceUpdateModel
from scm.models.objects.service import Override, Protocol, TCPProtocol, UDPProtocol
from tests.test_factories.objects.service import ServiceCreateModelFactory, ServiceUpdateModelFactory

# -------------------- Test Classes for Pydantic Models --------------------


class TestOverrideModel:
    """Tests for Override model validation."""

    def test_override_model_valid(self):
        """Test validation with valid data."""
        data = {
            "timeout": 10,
            "halfclose_timeout": 10,
            "timewait_timeout": 10,
        }
        model = Override(**data)
        assert model.timeout == data["timeout"]
        assert model.halfclose_timeout == data["halfclose_timeout"]
        assert model.timewait_timeout == data["timewait_timeout"]

    def test_override_model_optional_fields(self):
        """Test that all fields are optional."""
        data = {}
        model = Override(**data)
        assert model.timeout is None
        assert model.halfclose_timeout is None
        assert model.timewait_timeout is None

    def test_override_model_invalid_timeout(self):
        """Test validation with invalid timeout values."""
        data = {
            "timeout": "invalid",
            "halfclose_timeout": "invalid",
            "timewait_timeout": "invalid",
        }
        with pytest.raises(ValidationError) as exc_info:
            Override(**data)
        assert "Input should be a valid integer" in str(exc_info.value)


class TestProtocolModels:
    """Tests for Protocol-related models validation."""

    def test_tcp_protocol_valid(self):
        """Test validation of TCP protocol with valid data."""
        data = {
            "port": "80,443",
            "override": {
                "timeout": 10,
                "halfclose_timeout": 10,
            },
        }
        model = TCPProtocol(**data)
        assert model.port == data["port"]
        assert isinstance(model.override, Override)
        assert model.override.timeout == 10

    def test_tcp_protocol_invalid_port(self):
        """Test validation with invalid TCP port format."""
        data = {"port": 1}
        with pytest.raises(ValidationError) as exc_info:
            TCPProtocol(**data)
        assert "1 validation error for TCPProtocol" in str(exc_info.value)

    def test_udp_protocol_valid(self):
        """Test validation of UDP protocol with valid data."""
        data = {
            "port": "53",
            "override": {
                "timeout": 10,
            },
        }
        model = UDPProtocol(**data)
        assert model.port == data["port"]
        assert isinstance(model.override, Override)
        assert model.override.timeout == 10

    def test_protocol_tcp_only(self):
        """Test Protocol model with TCP only."""
        data = {
            "tcp": {"port": "80"},
        }
        model = Protocol(**data)
        assert model.tcp is not None
        assert model.udp is None
        assert model.tcp.port == "80"

    def test_protocol_udp_only(self):
        """Test Protocol model with UDP only."""
        data = {
            "udp": {"port": "53"},
        }
        model = Protocol(**data)
        assert model.udp is not None
        assert model.tcp is None
        assert model.udp.port == "53"

    def test_protocol_both_types_error(self):
        """Test validation when both TCP and UDP are provided."""
        data = {
            "tcp": {"port": "80"},
            "udp": {"port": "53"},
        }
        with pytest.raises(ValueError) as exc_info:
            Protocol(**data)
        assert "Exactly one of 'tcp' or 'udp' must be provided in 'protocol'." in str(
            exc_info.value
        )

    def test_protocol_no_type_error(self):
        """Test validation when no protocol type is provided."""
        data = {}
        with pytest.raises(ValueError) as exc_info:
            Protocol(**data)
        assert "Exactly one of 'tcp' or 'udp' must be provided in 'protocol'." in str(
            exc_info.value
        )


class TestServiceCreateModel:
    """Tests for ServiceCreateModel validation."""

    def test_service_create_model_valid_tcp(self):
        """Test validation with valid TCP service data."""
        data = ServiceCreateModelFactory.build_valid_tcp()
        model = ServiceCreateModel(**data)
        assert model.name == data["name"]
        assert model.folder == data["folder"]
        assert model.protocol.tcp is not None
        assert model.protocol.tcp.port == data["protocol"]["tcp"]["port"]

    def test_service_create_model_valid_udp(self):
        """Test validation with valid UDP service data."""
        data = ServiceCreateModelFactory.build_valid_udp()
        model = ServiceCreateModel(**data)
        assert model.name == data["name"]
        assert model.folder == data["folder"]
        assert model.protocol.udp is not None
        assert model.protocol.udp.port == data["protocol"]["udp"]["port"]

    def test_service_create_model_invalid_data_error(self):
        """Test that ValidationError is raised when invalid data is provided."""
        data = {"invalid_field": "test"}
        with pytest.raises(ValidationError) as exc_info:
            ServiceCreateModel(**data)
        error_msg = str(exc_info.value)
        assert "2 validation errors for ServiceCreateModel" in error_msg
        assert "name\n  Field required" in error_msg
        assert "protocol\n  Field required" in error_msg

    def test_service_create_model_multiple_containers_provided(self):
        """Test validation when multiple containers are provided."""
        data = ServiceCreateModelFactory.build_with_multiple_containers()
        with pytest.raises(ValueError) as exc_info:
            ServiceCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_service_create_model_missing_required_fields(self):
        """Test validation when required fields are missing."""
        data = {"name": "test-service"}
        with pytest.raises(ValidationError) as exc_info:
            ServiceCreateModel(**data)
        error_msg = str(exc_info.value)
        assert "1 validation error for ServiceCreateModel" in error_msg
        assert "protocol\n  Field required" in error_msg

    def test_service_create_model_invalid_name(self):
        """Test validation of name field constraints."""
        data = {
            "name": "invalid@name#",
            "folder": "Texas",
            "protocol": {"tcp": {"port": "80"}},
        }
        with pytest.raises(ValidationError) as exc_info:
            ServiceCreateModel(**data)
        assert "String should match pattern" in str(exc_info.value)


class TestServiceUpdateModel:
    """Tests for ServiceUpdateModel validation."""

    def test_service_update_model_valid(self):
        """Test validation with valid update data."""
        data = ServiceUpdateModelFactory.build_valid()
        model = ServiceUpdateModel(**data)
        assert model.name == data["name"]
        assert model.protocol.tcp.port == data["protocol"]["tcp"]["port"]
        assert str(model.id) == data["id"]

    def test_service_update_model_invalid_data_error(self):
        """Test that ValidationError is raised when invalid data is provided."""
        data = {"invalid": "data"}
        with pytest.raises(ValidationError) as exc_info:
            ServiceUpdateModel(**data)
        error_msg = str(exc_info.value)
        assert "3 validation errors for ServiceUpdateModel" in error_msg
        assert "name\n  Field required" in error_msg
        assert "protocol\n  Field required" in error_msg
        assert "id\n  Field required" in error_msg

    def test_service_update_model_partial_update(self):
        """Test validation with partial update data."""
        data = {
            "name": "updated-service",
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "protocol": {"tcp": {"port": "8080"}},
            "description": "Updated description",
        }
        model = ServiceUpdateModel(**data)
        assert model.name == data["name"]
        assert model.protocol.tcp.port == "8080"
        assert model.description == "Updated description"

    def test_service_update_model_invalid_uuid(self):
        """Test validation with invalid UUID format."""
        data = {
            "id": "invalid-uuid",
            "name": "test-service",
            "protocol": {"tcp": {"port": "80"}},
        }
        with pytest.raises(ValidationError) as exc_info:
            ServiceUpdateModel(**data)
        assert "Input should be a valid UUID" in str(exc_info.value)


class TestServiceResponseModel:
    """Tests for ServiceResponseModel validation."""

    def test_service_response_model_valid(self):
        """Test validation with valid response data."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-service",
            "protocol": {"tcp": {"port": "80"}},
            "folder": "Texas",
        }
        model = ServiceResponseModel(**data)
        assert str(model.id) == data["id"]
        assert model.name == data["name"]
        assert model.protocol.tcp.port == "80"
        assert model.folder == "Texas"

    def test_service_response_model_optional_fields(self):
        """Test validation with optional fields in response."""
        data = {
            "name": "test-service",
            "protocol": {"tcp": {"port": "80"}},
        }
        model = ServiceResponseModel(**data)
        assert model.id is None
        assert model.description is None
        assert model.tag is None

    def test_service_response_model_invalid_uuid(self):
        """Test validation of UUID format in response."""
        data = {
            "id": "invalid-uuid",
            "name": "test-service",
            "protocol": {"tcp": {"port": "80"}},
        }
        with pytest.raises(ValidationError) as exc_info:
            ServiceResponseModel(**data)
        assert "Input should be a valid UUID" in str(exc_info.value)


# -------------------- End of Test Classes --------------------
