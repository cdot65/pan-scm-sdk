# tests/scm/models/identity/test_radius_server_profile_models.py

"""Tests for RADIUS server profile identity models."""

# External libraries
from pydantic import ValidationError
import pytest

# Local SDK imports
from scm.models.identity.radius_server_profiles import (
    RadiusProtocol,
    RadiusServer,
    RadiusServerProfileCreateModel,
    RadiusServerProfileResponseModel,
    RadiusServerProfileUpdateModel,
)
from tests.factories.identity.radius_server_profile import (
    RadiusServerProfileCreateModelFactory,
    RadiusServerProfileUpdateModelFactory,
)

# -------------------- Test Classes for Pydantic Models --------------------


class TestRadiusServerProfileCreateModel:
    """Tests for RadiusServerProfileCreateModel validation."""

    def test_create_model_valid(self):
        """Test validation with valid data."""
        data = RadiusServerProfileCreateModelFactory.build_valid()
        model = RadiusServerProfileCreateModel(**data)
        assert model.name == data["name"]
        assert model.folder == data["folder"]

    def test_create_model_with_servers(self):
        """Test validation with server entries."""
        data = RadiusServerProfileCreateModelFactory.build_valid()
        model = RadiusServerProfileCreateModel(**data)
        assert model.server is not None
        assert len(model.server) > 0
        assert isinstance(model.server[0], RadiusServer)

    def test_create_model_with_protocol(self):
        """Test validation with protocol configuration."""
        data = RadiusServerProfileCreateModelFactory.build_valid()
        model = RadiusServerProfileCreateModel(**data)
        assert model.protocol is not None
        assert isinstance(model.protocol, RadiusProtocol)
        assert model.protocol.CHAP == {}

    def test_create_model_multiple_containers(self):
        """Test validation when multiple containers are provided."""
        data = RadiusServerProfileCreateModelFactory.build_with_multiple_containers()
        with pytest.raises(ValueError) as exc_info:
            RadiusServerProfileCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_create_model_no_container(self):
        """Test validation when no container is provided."""
        data = RadiusServerProfileCreateModelFactory.build_with_no_container()
        with pytest.raises(ValueError) as exc_info:
            RadiusServerProfileCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )


class TestRadiusServerProfileUpdateModel:
    """Tests for RadiusServerProfileUpdateModel validation."""

    def test_update_model_valid(self):
        """Test validation with valid update data."""
        data = RadiusServerProfileUpdateModelFactory.build_valid()
        model = RadiusServerProfileUpdateModel(**data)
        assert model.name == data["name"]
        assert str(model.id) == data["id"]


class TestRadiusServerProfileResponseModel:
    """Tests for RadiusServerProfileResponseModel validation."""

    def test_response_model_valid(self):
        """Test validation with valid response data."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestProfile",
            "folder": "Texas",
            "protocol": {"CHAP": {}},
            "timeout": 5,
            "retries": 3,
        }
        model = RadiusServerProfileResponseModel(**data)
        assert str(model.id) == data["id"]
        assert model.name == data["name"]
        assert model.folder == data["folder"]

    def test_response_model_invalid_uuid(self):
        """Test validation with invalid UUID format."""
        data = {
            "id": "invalid-uuid",
            "name": "TestProfile",
            "folder": "Texas",
        }
        with pytest.raises(ValidationError) as exc_info:
            RadiusServerProfileResponseModel(**data)
        assert "Input should be a valid UUID" in str(exc_info.value)

    def test_response_model_ignores_extra_fields(self):
        """Test that extra fields are silently ignored in ResponseModel."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestProfile",
            "folder": "Texas",
            "unknown_field": "should_be_ignored",
        }
        model = RadiusServerProfileResponseModel(**data)
        assert not hasattr(model, "unknown_field")


class TestRadiusServerModel:
    """Tests for RadiusServer component model."""

    def test_server_valid(self):
        """Test validation with valid server data."""
        data = {"name": "radius1", "ip_address": "10.0.0.1", "port": 1812, "secret": "secret123"}
        model = RadiusServer(**data)
        assert model.name == "radius1"
        assert model.ip_address == "10.0.0.1"
        assert model.port == 1812

    def test_server_invalid_port(self):
        """Test validation with invalid port."""
        data = {"name": "radius1", "ip_address": "10.0.0.1", "port": 0}
        with pytest.raises(ValidationError) as exc_info:
            RadiusServer(**data)
        assert "greater than or equal to 1" in str(exc_info.value)

    def test_server_rejects_extra_fields(self):
        """Test that extra fields are rejected."""
        data = {"name": "radius1", "ip_address": "10.0.0.1", "unknown": "value"}
        with pytest.raises(ValidationError) as exc_info:
            RadiusServer(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestRadiusProtocolModel:
    """Tests for RadiusProtocol component model."""

    def test_protocol_chap(self):
        """Test CHAP protocol configuration."""
        model = RadiusProtocol(CHAP={})
        assert model.CHAP == {}

    def test_protocol_pap(self):
        """Test PAP protocol configuration."""
        model = RadiusProtocol(PAP={})
        assert model.PAP == {}

    def test_protocol_eap_ttls(self):
        """Test EAP-TTLS with PAP protocol configuration."""
        model = RadiusProtocol(EAP_TTLS_with_PAP={})
        assert model.EAP_TTLS_with_PAP == {}

    def test_protocol_rejects_extra_fields(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RadiusProtocol(unknown_protocol={})
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestRadiusRetries:
    """Tests for retries field validation."""

    def test_retries_valid(self):
        """Test valid retries value."""
        data = RadiusServerProfileCreateModelFactory.build_valid(retries=3)
        model = RadiusServerProfileCreateModel(**data)
        assert model.retries == 3

    def test_retries_too_high(self):
        """Test retries exceeding maximum."""
        data = RadiusServerProfileCreateModelFactory.build_valid(retries=6)
        with pytest.raises(ValidationError) as exc_info:
            RadiusServerProfileCreateModel(**data)
        assert "less than or equal to 5" in str(exc_info.value)

    def test_retries_too_low(self):
        """Test retries below minimum."""
        data = RadiusServerProfileCreateModelFactory.build_valid(retries=0)
        with pytest.raises(ValidationError) as exc_info:
            RadiusServerProfileCreateModel(**data)
        assert "greater than or equal to 1" in str(exc_info.value)


# -------------------- End of Test Classes --------------------
