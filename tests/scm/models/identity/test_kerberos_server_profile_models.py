# tests/scm/models/identity/test_kerberos_server_profile_models.py

"""Tests for Kerberos server profile identity models."""

# External libraries
from pydantic import ValidationError
import pytest

# Local SDK imports
from scm.models.identity.kerberos_server_profiles import (
    KerberosServer,
    KerberosServerProfileCreateModel,
    KerberosServerProfileResponseModel,
    KerberosServerProfileUpdateModel,
)
from tests.factories.identity.kerberos_server_profile import (
    KerberosServerProfileCreateModelFactory,
    KerberosServerProfileUpdateModelFactory,
)

# -------------------- Test Classes for Pydantic Models --------------------


class TestKerberosServerProfileCreateModel:
    """Tests for KerberosServerProfileCreateModel validation."""

    def test_create_model_valid(self):
        """Test validation with valid data."""
        data = KerberosServerProfileCreateModelFactory.build_valid()
        model = KerberosServerProfileCreateModel(**data)
        assert model.name == data["name"]
        assert model.folder == data["folder"]

    def test_create_model_with_servers(self):
        """Test validation with server entries."""
        data = KerberosServerProfileCreateModelFactory.build_valid()
        model = KerberosServerProfileCreateModel(**data)
        assert model.server is not None
        assert len(model.server) > 0
        assert isinstance(model.server[0], KerberosServer)

    def test_create_model_multiple_containers(self):
        """Test validation when multiple containers are provided."""
        data = KerberosServerProfileCreateModelFactory.build_with_multiple_containers()
        with pytest.raises(ValueError) as exc_info:
            KerberosServerProfileCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_create_model_no_container(self):
        """Test validation when no container is provided."""
        data = KerberosServerProfileCreateModelFactory.build_with_no_container()
        with pytest.raises(ValueError) as exc_info:
            KerberosServerProfileCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )


class TestKerberosServerProfileUpdateModel:
    """Tests for KerberosServerProfileUpdateModel validation."""

    def test_update_model_valid(self):
        """Test validation with valid update data."""
        data = KerberosServerProfileUpdateModelFactory.build_valid()
        model = KerberosServerProfileUpdateModel(**data)
        assert model.name == data["name"]
        assert str(model.id) == data["id"]


class TestKerberosServerProfileResponseModel:
    """Tests for KerberosServerProfileResponseModel validation."""

    def test_response_model_valid(self):
        """Test validation with valid response data."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestProfile",
            "folder": "Texas",
            "server": [{"name": "kdc1", "host": "10.0.0.1", "port": 88}],
        }
        model = KerberosServerProfileResponseModel(**data)
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
            KerberosServerProfileResponseModel(**data)
        assert "Input should be a valid UUID" in str(exc_info.value)

    def test_response_model_ignores_extra_fields(self):
        """Test that extra fields are silently ignored in ResponseModel."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestProfile",
            "folder": "Texas",
            "unknown_field": "should_be_ignored",
        }
        model = KerberosServerProfileResponseModel(**data)
        assert not hasattr(model, "unknown_field")


class TestKerberosServerModel:
    """Tests for KerberosServer component model."""

    def test_server_valid(self):
        """Test validation with valid server data."""
        data = {"name": "kdc1", "host": "10.0.0.1", "port": 88}
        model = KerberosServer(**data)
        assert model.name == "kdc1"
        assert model.host == "10.0.0.1"
        assert model.port == 88

    def test_server_invalid_port(self):
        """Test validation with invalid port."""
        data = {"name": "kdc1", "host": "10.0.0.1", "port": 0}
        with pytest.raises(ValidationError) as exc_info:
            KerberosServer(**data)
        assert "greater than or equal to 1" in str(exc_info.value)

    def test_server_port_too_high(self):
        """Test validation with port exceeding maximum."""
        data = {"name": "kdc1", "host": "10.0.0.1", "port": 65536}
        with pytest.raises(ValidationError) as exc_info:
            KerberosServer(**data)
        assert "less than or equal to 65535" in str(exc_info.value)

    def test_server_rejects_extra_fields(self):
        """Test that extra fields are rejected."""
        data = {"name": "kdc1", "host": "10.0.0.1", "unknown": "value"}
        with pytest.raises(ValidationError) as exc_info:
            KerberosServer(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)


# -------------------- End of Test Classes --------------------
