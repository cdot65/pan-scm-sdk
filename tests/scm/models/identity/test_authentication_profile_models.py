# tests/scm/models/identity/test_authentication_profile_models.py

"""Tests for authentication profile identity models."""

# External libraries
from pydantic import ValidationError
import pytest

# Local SDK imports
from scm.models.identity.authentication_profiles import (
    AuthenticationProfileCreateModel,
    AuthenticationProfileResponseModel,
    AuthenticationProfileUpdateModel,
    AuthProfileLockout,
    AuthProfileMethod,
    AuthProfileMethodLdap,
    AuthProfileMethodRadius,
    AuthProfileMethodSamlIdp,
)
from tests.factories.identity.authentication_profile import (
    AuthenticationProfileCreateModelFactory,
    AuthenticationProfileUpdateModelFactory,
)

# -------------------- Test Classes for Pydantic Models --------------------


class TestAuthenticationProfileCreateModel:
    """Tests for AuthenticationProfileCreateModel validation."""

    def test_create_model_valid(self):
        """Test validation with valid data."""
        data = AuthenticationProfileCreateModelFactory.build_valid()
        model = AuthenticationProfileCreateModel(**data)
        assert model.name == data["name"]
        assert model.folder == data["folder"]

    def test_create_model_with_method(self):
        """Test validation with method configuration."""
        data = AuthenticationProfileCreateModelFactory.build_valid()
        model = AuthenticationProfileCreateModel(**data)
        assert model.method is not None
        assert isinstance(model.method, AuthProfileMethod)
        assert model.method.local_database == {}

    def test_create_model_multiple_containers(self):
        """Test validation when multiple containers are provided."""
        data = AuthenticationProfileCreateModelFactory.build_with_multiple_containers()
        with pytest.raises(ValueError) as exc_info:
            AuthenticationProfileCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_create_model_no_container(self):
        """Test validation when no container is provided."""
        data = AuthenticationProfileCreateModelFactory.build_with_no_container()
        with pytest.raises(ValueError) as exc_info:
            AuthenticationProfileCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )


class TestAuthenticationProfileUpdateModel:
    """Tests for AuthenticationProfileUpdateModel validation."""

    def test_update_model_valid(self):
        """Test validation with valid update data."""
        data = AuthenticationProfileUpdateModelFactory.build_valid()
        model = AuthenticationProfileUpdateModel(**data)
        assert model.name == data["name"]
        assert str(model.id) == data["id"]


class TestAuthenticationProfileResponseModel:
    """Tests for AuthenticationProfileResponseModel validation."""

    def test_response_model_valid(self):
        """Test validation with valid response data."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestProfile",
            "folder": "Texas",
            "method": {"local_database": {}},
        }
        model = AuthenticationProfileResponseModel(**data)
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
            AuthenticationProfileResponseModel(**data)
        assert "Input should be a valid UUID" in str(exc_info.value)

    def test_response_model_ignores_extra_fields(self):
        """Test that extra fields are silently ignored in ResponseModel."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestProfile",
            "folder": "Texas",
            "unknown_field": "should_be_ignored",
        }
        model = AuthenticationProfileResponseModel(**data)
        assert not hasattr(model, "unknown_field")


class TestAuthProfileMethod:
    """Tests for AuthProfileMethod component model."""

    def test_method_local_database(self):
        """Test local_database method configuration."""
        model = AuthProfileMethod(local_database={})
        assert model.local_database == {}

    def test_method_saml_idp(self):
        """Test SAML IDP method configuration."""
        saml_data = {"server_profile": "saml-profile", "enable_single_logout": True}
        model = AuthProfileMethod(saml_idp=saml_data)
        assert isinstance(model.saml_idp, AuthProfileMethodSamlIdp)
        assert model.saml_idp.server_profile == "saml-profile"

    def test_method_ldap(self):
        """Test LDAP method configuration."""
        ldap_data = {"server_profile": "ldap-profile", "login_attribute": "uid"}
        model = AuthProfileMethod(ldap=ldap_data)
        assert isinstance(model.ldap, AuthProfileMethodLdap)
        assert model.ldap.server_profile == "ldap-profile"

    def test_method_radius(self):
        """Test RADIUS method configuration."""
        radius_data = {"server_profile": "radius-profile", "checkgroup": True}
        model = AuthProfileMethod(radius=radius_data)
        assert isinstance(model.radius, AuthProfileMethodRadius)
        assert model.radius.server_profile == "radius-profile"

    def test_method_rejects_extra_fields(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            AuthProfileMethod(unknown_method={})
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestAuthProfileLockout:
    """Tests for AuthProfileLockout component model."""

    def test_lockout_valid(self):
        """Test valid lockout configuration."""
        model = AuthProfileLockout(failed_attempts=5, lockout_time=30)
        assert model.failed_attempts == 5
        assert model.lockout_time == 30

    def test_lockout_rejects_extra_fields(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            AuthProfileLockout(failed_attempts=5, unknown="value")
        assert "Extra inputs are not permitted" in str(exc_info.value)


# -------------------- End of Test Classes --------------------
