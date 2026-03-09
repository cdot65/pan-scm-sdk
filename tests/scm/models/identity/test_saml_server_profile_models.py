# tests/scm/models/identity/test_saml_server_profile_models.py

"""Tests for SAML server profile identity models."""

# External libraries
from pydantic import ValidationError
import pytest

# Local SDK imports
from scm.models.identity.saml_server_profiles import (
    SamlServerProfileCreateModel,
    SamlServerProfileResponseModel,
    SamlServerProfileUpdateModel,
    SamlSloBindings,
    SamlSsoBindings,
)
from tests.factories.identity.saml_server_profile import (
    SamlServerProfileCreateModelFactory,
    SamlServerProfileUpdateModelFactory,
)

# -------------------- Test Classes for Pydantic Models --------------------


class TestSamlServerProfileCreateModel:
    """Tests for SamlServerProfileCreateModel validation."""

    def test_create_model_valid(self):
        """Test validation with valid data."""
        data = SamlServerProfileCreateModelFactory.build_valid()
        model = SamlServerProfileCreateModel(**data)
        assert model.name == data["name"]
        assert model.folder == data["folder"]
        assert model.entity_id == data["entity_id"]
        assert model.certificate == data["certificate"]
        assert model.sso_url == data["sso_url"]
        assert model.sso_bindings == SamlSsoBindings.post

    def test_create_model_missing_entity_id(self):
        """Test validation with missing entity_id."""
        data = SamlServerProfileCreateModelFactory.build_valid()
        del data["entity_id"]
        with pytest.raises(ValidationError) as exc_info:
            SamlServerProfileCreateModel(**data)
        assert "entity_id" in str(exc_info.value)

    def test_create_model_missing_certificate(self):
        """Test validation with missing certificate."""
        data = SamlServerProfileCreateModelFactory.build_valid()
        del data["certificate"]
        with pytest.raises(ValidationError) as exc_info:
            SamlServerProfileCreateModel(**data)
        assert "certificate" in str(exc_info.value)

    def test_create_model_missing_sso_url(self):
        """Test validation with missing sso_url."""
        data = SamlServerProfileCreateModelFactory.build_valid()
        del data["sso_url"]
        with pytest.raises(ValidationError) as exc_info:
            SamlServerProfileCreateModel(**data)
        assert "sso_url" in str(exc_info.value)

    def test_create_model_missing_sso_bindings(self):
        """Test validation with missing sso_bindings."""
        data = SamlServerProfileCreateModelFactory.build_valid()
        del data["sso_bindings"]
        with pytest.raises(ValidationError) as exc_info:
            SamlServerProfileCreateModel(**data)
        assert "sso_bindings" in str(exc_info.value)

    def test_create_model_invalid_sso_bindings(self):
        """Test validation with invalid sso_bindings."""
        data = SamlServerProfileCreateModelFactory.build_valid()
        data["sso_bindings"] = "invalid"
        with pytest.raises(ValidationError) as exc_info:
            SamlServerProfileCreateModel(**data)
        assert "Input should be 'post'" in str(exc_info.value)

    def test_create_model_multiple_containers(self):
        """Test validation when multiple containers are provided."""
        data = SamlServerProfileCreateModelFactory.build_with_multiple_containers()
        with pytest.raises(ValueError) as exc_info:
            SamlServerProfileCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_create_model_no_container(self):
        """Test validation when no container is provided."""
        data = SamlServerProfileCreateModelFactory.build_with_no_container()
        with pytest.raises(ValueError) as exc_info:
            SamlServerProfileCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )


class TestSamlServerProfileUpdateModel:
    """Tests for SamlServerProfileUpdateModel validation."""

    def test_update_model_valid(self):
        """Test validation with valid update data."""
        data = SamlServerProfileUpdateModelFactory.build_valid()
        model = SamlServerProfileUpdateModel(**data)
        assert model.name == data["name"]
        assert str(model.id) == data["id"]


class TestSamlServerProfileResponseModel:
    """Tests for SamlServerProfileResponseModel validation."""

    def test_response_model_valid(self):
        """Test validation with valid response data."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestProfile",
            "folder": "Texas",
            "entity_id": "https://idp.example.com/saml",
            "certificate": "test-cert",
            "sso_url": "https://idp.example.com/sso",
            "sso_bindings": "post",
        }
        model = SamlServerProfileResponseModel(**data)
        assert str(model.id) == data["id"]
        assert model.name == data["name"]
        assert model.sso_bindings == SamlSsoBindings.post

    def test_response_model_invalid_uuid(self):
        """Test validation with invalid UUID format."""
        data = {
            "id": "invalid-uuid",
            "name": "TestProfile",
            "folder": "Texas",
            "entity_id": "https://idp.example.com/saml",
            "certificate": "test-cert",
            "sso_url": "https://idp.example.com/sso",
            "sso_bindings": "post",
        }
        with pytest.raises(ValidationError) as exc_info:
            SamlServerProfileResponseModel(**data)
        assert "Input should be a valid UUID" in str(exc_info.value)

    def test_response_model_ignores_extra_fields(self):
        """Test that extra fields are silently ignored in ResponseModel."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestProfile",
            "folder": "Texas",
            "entity_id": "https://idp.example.com/saml",
            "certificate": "test-cert",
            "sso_url": "https://idp.example.com/sso",
            "sso_bindings": "post",
            "unknown_field": "should_be_ignored",
        }
        model = SamlServerProfileResponseModel(**data)
        assert not hasattr(model, "unknown_field")


class TestSamlBindings:
    """Tests for SAML binding enums."""

    def test_sso_bindings_post(self):
        """Test SSO binding post value."""
        assert SamlSsoBindings.post == "post"

    def test_sso_bindings_redirect(self):
        """Test SSO binding redirect value."""
        assert SamlSsoBindings.redirect == "redirect"

    def test_slo_bindings_post(self):
        """Test SLO binding post value."""
        assert SamlSloBindings.post == "post"

    def test_slo_bindings_redirect(self):
        """Test SLO binding redirect value."""
        assert SamlSloBindings.redirect == "redirect"


class TestSamlMaxClockSkew:
    """Tests for max_clock_skew field validation."""

    def test_max_clock_skew_valid(self):
        """Test valid max_clock_skew value."""
        data = SamlServerProfileCreateModelFactory.build_valid(max_clock_skew=60)
        model = SamlServerProfileCreateModel(**data)
        assert model.max_clock_skew == 60

    def test_max_clock_skew_too_high(self):
        """Test max_clock_skew exceeding maximum."""
        data = SamlServerProfileCreateModelFactory.build_valid(max_clock_skew=901)
        with pytest.raises(ValidationError) as exc_info:
            SamlServerProfileCreateModel(**data)
        assert "less than or equal to 900" in str(exc_info.value)

    def test_max_clock_skew_too_low(self):
        """Test max_clock_skew below minimum."""
        data = SamlServerProfileCreateModelFactory.build_valid(max_clock_skew=0)
        with pytest.raises(ValidationError) as exc_info:
            SamlServerProfileCreateModel(**data)
        assert "greater than or equal to 1" in str(exc_info.value)


# -------------------- End of Test Classes --------------------
