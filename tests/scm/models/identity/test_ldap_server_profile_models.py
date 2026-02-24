# tests/scm/models/identity/test_ldap_server_profile_models.py

"""Tests for LDAP server profile identity models."""

# External libraries
from pydantic import ValidationError
import pytest

# Local SDK imports
from scm.models.identity.ldap_server_profiles import (
    LdapServer,
    LdapServerProfileCreateModel,
    LdapServerProfileResponseModel,
    LdapServerProfileUpdateModel,
    LdapType,
)
from tests.factories.identity.ldap_server_profile import (
    LdapServerProfileCreateModelFactory,
    LdapServerProfileUpdateModelFactory,
)

# -------------------- Test Classes for Pydantic Models --------------------


class TestLdapServerProfileCreateModel:
    """Tests for LdapServerProfileCreateModel validation."""

    def test_create_model_valid(self):
        """Test validation with valid data."""
        data = LdapServerProfileCreateModelFactory.build_valid()
        model = LdapServerProfileCreateModel(**data)
        assert model.name == data["name"]
        assert model.folder == data["folder"]
        assert model.ldap_type == LdapType.active_directory

    def test_create_model_with_servers(self):
        """Test validation with server entries."""
        data = LdapServerProfileCreateModelFactory.build_valid()
        model = LdapServerProfileCreateModel(**data)
        assert model.server is not None
        assert len(model.server) > 0
        assert isinstance(model.server[0], LdapServer)

    def test_create_model_multiple_containers(self):
        """Test validation when multiple containers are provided."""
        data = LdapServerProfileCreateModelFactory.build_with_multiple_containers()
        with pytest.raises(ValueError) as exc_info:
            LdapServerProfileCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_create_model_no_container(self):
        """Test validation when no container is provided."""
        data = LdapServerProfileCreateModelFactory.build_with_no_container()
        with pytest.raises(ValueError) as exc_info:
            LdapServerProfileCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_create_model_invalid_ldap_type(self):
        """Test validation with invalid ldap_type."""
        data = LdapServerProfileCreateModelFactory.build_valid()
        data["ldap_type"] = "INVALID"
        with pytest.raises(ValidationError) as exc_info:
            LdapServerProfileCreateModel(**data)
        assert "Input should be 'active-directory'" in str(exc_info.value)


class TestLdapServerProfileUpdateModel:
    """Tests for LdapServerProfileUpdateModel validation."""

    def test_update_model_valid(self):
        """Test validation with valid update data."""
        data = LdapServerProfileUpdateModelFactory.build_valid()
        model = LdapServerProfileUpdateModel(**data)
        assert model.name == data["name"]
        assert str(model.id) == data["id"]


class TestLdapServerProfileResponseModel:
    """Tests for LdapServerProfileResponseModel validation."""

    def test_response_model_valid(self):
        """Test validation with valid response data."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestProfile",
            "folder": "Texas",
            "base": "dc=example,dc=com",
            "ldap_type": "active-directory",
        }
        model = LdapServerProfileResponseModel(**data)
        assert str(model.id) == data["id"]
        assert model.name == data["name"]
        assert model.ldap_type == LdapType.active_directory

    def test_response_model_invalid_uuid(self):
        """Test validation with invalid UUID format."""
        data = {
            "id": "invalid-uuid",
            "name": "TestProfile",
            "folder": "Texas",
        }
        with pytest.raises(ValidationError) as exc_info:
            LdapServerProfileResponseModel(**data)
        assert "Input should be a valid UUID" in str(exc_info.value)

    def test_response_model_ignores_extra_fields(self):
        """Test that extra fields are silently ignored in ResponseModel."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestProfile",
            "folder": "Texas",
            "unknown_field": "should_be_ignored",
        }
        model = LdapServerProfileResponseModel(**data)
        assert not hasattr(model, "unknown_field")


class TestLdapServerModel:
    """Tests for LdapServer component model."""

    def test_server_valid(self):
        """Test validation with valid server data."""
        data = {"name": "ldap1", "address": "10.0.0.1", "port": 389}
        model = LdapServer(**data)
        assert model.name == "ldap1"
        assert model.address == "10.0.0.1"
        assert model.port == 389

    def test_server_invalid_port(self):
        """Test validation with invalid port."""
        data = {"name": "ldap1", "address": "10.0.0.1", "port": 0}
        with pytest.raises(ValidationError) as exc_info:
            LdapServer(**data)
        assert "greater than or equal to 1" in str(exc_info.value)

    def test_server_rejects_extra_fields(self):
        """Test that extra fields are rejected."""
        data = {"name": "ldap1", "address": "10.0.0.1", "unknown": "value"}
        with pytest.raises(ValidationError) as exc_info:
            LdapServer(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)


# -------------------- End of Test Classes --------------------
