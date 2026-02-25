# tests/scm/models/identity/test_tacacs_server_profile_models.py

"""Tests for TACACS+ server profile identity models."""

# External libraries
from pydantic import ValidationError
import pytest

# Local SDK imports
from scm.models.identity.tacacs_server_profiles import (
    TacacsProtocol,
    TacacsServer,
    TacacsServerProfileCreateModel,
    TacacsServerProfileResponseModel,
    TacacsServerProfileUpdateModel,
)
from tests.factories.identity.tacacs_server_profile import (
    TacacsServerProfileCreateModelFactory,
    TacacsServerProfileUpdateModelFactory,
)

# -------------------- Test Classes for Pydantic Models --------------------


class TestTacacsServerProfileCreateModel:
    """Tests for TacacsServerProfileCreateModel validation."""

    def test_create_model_valid(self):
        """Test validation with valid data."""
        data = TacacsServerProfileCreateModelFactory.build_valid()
        model = TacacsServerProfileCreateModel(**data)
        assert model.name == data["name"]
        assert model.folder == data["folder"]
        assert model.protocol == TacacsProtocol.CHAP

    def test_create_model_with_servers(self):
        """Test validation with server entries."""
        data = TacacsServerProfileCreateModelFactory.build_valid()
        model = TacacsServerProfileCreateModel(**data)
        assert model.server is not None
        assert len(model.server) > 0
        assert isinstance(model.server[0], TacacsServer)

    def test_create_model_multiple_containers(self):
        """Test validation when multiple containers are provided."""
        data = TacacsServerProfileCreateModelFactory.build_with_multiple_containers()
        with pytest.raises(ValueError) as exc_info:
            TacacsServerProfileCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_create_model_no_container(self):
        """Test validation when no container is provided."""
        data = TacacsServerProfileCreateModelFactory.build_with_no_container()
        with pytest.raises(ValueError) as exc_info:
            TacacsServerProfileCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_create_model_invalid_protocol(self):
        """Test validation with invalid protocol."""
        data = TacacsServerProfileCreateModelFactory.build_valid()
        data["protocol"] = "INVALID"
        with pytest.raises(ValidationError) as exc_info:
            TacacsServerProfileCreateModel(**data)
        assert "Input should be 'CHAP'" in str(exc_info.value)


class TestTacacsServerProfileUpdateModel:
    """Tests for TacacsServerProfileUpdateModel validation."""

    def test_update_model_valid(self):
        """Test validation with valid update data."""
        data = TacacsServerProfileUpdateModelFactory.build_valid()
        model = TacacsServerProfileUpdateModel(**data)
        assert model.name == data["name"]
        assert str(model.id) == data["id"]


class TestTacacsServerProfileResponseModel:
    """Tests for TacacsServerProfileResponseModel validation."""

    def test_response_model_valid(self):
        """Test validation with valid response data."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestProfile",
            "folder": "Texas",
            "protocol": "CHAP",
            "timeout": 5,
        }
        model = TacacsServerProfileResponseModel(**data)
        assert str(model.id) == data["id"]
        assert model.name == data["name"]
        assert model.protocol == TacacsProtocol.CHAP

    def test_response_model_invalid_uuid(self):
        """Test validation with invalid UUID format."""
        data = {
            "id": "invalid-uuid",
            "name": "TestProfile",
            "folder": "Texas",
        }
        with pytest.raises(ValidationError) as exc_info:
            TacacsServerProfileResponseModel(**data)
        assert "Input should be a valid UUID" in str(exc_info.value)

    def test_response_model_ignores_extra_fields(self):
        """Test that extra fields are silently ignored in ResponseModel."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestProfile",
            "folder": "Texas",
            "unknown_field": "should_be_ignored",
        }
        model = TacacsServerProfileResponseModel(**data)
        assert not hasattr(model, "unknown_field")


class TestTacacsServerModel:
    """Tests for TacacsServer component model."""

    def test_server_valid(self):
        """Test validation with valid server data."""
        data = {"name": "tacacs1", "address": "10.0.0.1", "port": 49, "secret": "secret123"}
        model = TacacsServer(**data)
        assert model.name == "tacacs1"
        assert model.address == "10.0.0.1"
        assert model.port == 49

    def test_server_invalid_port(self):
        """Test validation with invalid port."""
        data = {"name": "tacacs1", "address": "10.0.0.1", "port": 0}
        with pytest.raises(ValidationError) as exc_info:
            TacacsServer(**data)
        assert "greater than or equal to 1" in str(exc_info.value)

    def test_server_rejects_extra_fields(self):
        """Test that extra fields are rejected."""
        data = {"name": "tacacs1", "address": "10.0.0.1", "unknown": "value"}
        with pytest.raises(ValidationError) as exc_info:
            TacacsServer(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestTacacsTimeout:
    """Tests for timeout field validation."""

    def test_timeout_valid(self):
        """Test valid timeout value."""
        data = TacacsServerProfileCreateModelFactory.build_valid(timeout=15)
        model = TacacsServerProfileCreateModel(**data)
        assert model.timeout == 15

    def test_timeout_too_high(self):
        """Test timeout exceeding maximum."""
        data = TacacsServerProfileCreateModelFactory.build_valid(timeout=31)
        with pytest.raises(ValidationError) as exc_info:
            TacacsServerProfileCreateModel(**data)
        assert "less than or equal to 30" in str(exc_info.value)

    def test_timeout_too_low(self):
        """Test timeout below minimum."""
        data = TacacsServerProfileCreateModelFactory.build_valid(timeout=0)
        with pytest.raises(ValidationError) as exc_info:
            TacacsServerProfileCreateModel(**data)
        assert "greater than or equal to 1" in str(exc_info.value)


# -------------------- End of Test Classes --------------------
