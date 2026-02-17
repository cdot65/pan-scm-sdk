# tests/scm/models/security/test_decryption_profiles_models.py

"""Tests for decryption profile security models."""

from uuid import UUID

from pydantic import ValidationError

# External libraries
import pytest

# Local SDK imports
from scm.models.security.decryption_profiles import (
    DecryptionProfileCreateModel,
    DecryptionProfileResponseModel,
    DecryptionProfileUpdateModel,
    SSLVersion,
)
from tests.factories.security.decryption_profile import (
    DecryptionProfileCreateModelFactory,
    DecryptionProfileResponseFactory,
    DecryptionProfileUpdateModelFactory,
)

# -------------------- Test Classes for Pydantic Models --------------------


class TestDecryptionProfileCreateModel:
    """Tests for DecryptionProfileCreateModel validation."""

    def test_decryption_profile_create_model_valid(self):
        """Test validation with valid data."""
        data = DecryptionProfileCreateModelFactory.build_valid()
        model = DecryptionProfileCreateModel(**data)
        assert model.name == data["name"]
        assert model.folder == data["folder"]
        assert model.ssl_protocol_settings.min_version == SSLVersion.tls1_0
        assert model.ssl_protocol_settings.max_version == SSLVersion.tls1_2

    def test_decryption_profile_create_model_invalid_name(self):
        """Test validation when an invalid name is provided."""
        data = DecryptionProfileCreateModelFactory.build_with_invalid_name()
        with pytest.raises(ValidationError) as exc_info:
            DecryptionProfileCreateModel(**data)
        assert "name\n  String should match pattern" in str(exc_info.value)

    def test_decryption_profile_create_model_invalid_ssl_versions(self):
        """Test validation when invalid SSL versions are provided."""
        data = DecryptionProfileCreateModelFactory.build_with_invalid_ssl_versions()
        with pytest.raises(ValidationError) as exc_info:
            DecryptionProfileCreateModel(**data)
        assert "max_version cannot be less than min_version" in str(exc_info.value)

    def test_decryption_profile_create_model_multiple_containers(self):
        """Test validation when multiple containers are provided."""
        data = DecryptionProfileCreateModelFactory.build_with_multiple_containers()
        with pytest.raises(ValueError) as exc_info:
            DecryptionProfileCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_decryption_profile_create_model_no_container(self):
        """Test validation when no container is provided."""
        data = DecryptionProfileCreateModelFactory.build_with_no_container()
        with pytest.raises(ValidationError) as exc_info:
            DecryptionProfileCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_decryption_profile_create_model_ssl_protocol_settings(self):
        """Test validation of SSL protocol settings."""
        data = DecryptionProfileCreateModelFactory.build_valid()
        data["ssl_protocol_settings"]["auth_algo_md5"] = "invalid"
        with pytest.raises(ValidationError) as exc_info:
            DecryptionProfileCreateModel(**data)
        assert "auth_algo_md5\n  Input should be a valid boolean" in str(exc_info.value)


class TestDecryptionProfileUpdateModel:
    """Tests for DecryptionProfileUpdateModel validation."""

    def test_decryption_profile_update_model_valid(self):
        """Test validation with valid update data."""
        data = DecryptionProfileUpdateModelFactory.build_valid()
        model = DecryptionProfileUpdateModel(**data)
        assert model.id == UUID(data["id"])
        assert model.name == data["name"]
        assert model.ssl_protocol_settings.min_version == SSLVersion.tls1_1
        assert model.ssl_protocol_settings.max_version == SSLVersion.tls1_3

    def test_decryption_profile_update_model_invalid_fields(self):
        """Test validation with multiple invalid fields."""
        data = DecryptionProfileUpdateModelFactory.build_with_invalid_fields()
        with pytest.raises(ValidationError) as exc_info:
            DecryptionProfileUpdateModel(**data)
        error_msg = str(exc_info.value)
        assert "id\n  Input should be a valid UUID" in error_msg
        assert "name\n  String should match pattern" in error_msg
        assert (
            "4 validation errors for DecryptionProfileUpdateModel\nname\n  String should match pattern '^[A-Za-z0-9]{1}[A-Za-z0-9_\\-\\.\\s]{0,}$'"
            in error_msg
        )

    def test_decryption_profile_update_model_minimal_update(self):
        """Test validation with minimal valid update fields."""
        data = DecryptionProfileUpdateModelFactory.build_minimal_update()
        model = DecryptionProfileUpdateModel(**data)
        assert model.id == UUID(data["id"])
        assert model.ssl_forward_proxy.block_client_cert

    def test_decryption_profile_update_model_invalid_ssl_versions(self):
        """Test validation when invalid SSL versions are provided in update."""
        data = DecryptionProfileUpdateModelFactory.build_valid()
        data["ssl_protocol_settings"]["min_version"] = "tls1-3"
        data["ssl_protocol_settings"]["max_version"] = "tls1-1"
        with pytest.raises(ValidationError) as exc_info:
            DecryptionProfileUpdateModel(**data)
        assert "max_version cannot be less than min_version" in str(exc_info.value)


class TestDecryptionProfileResponseModel:
    """Tests for DecryptionProfileResponseModel validation."""

    def test_decryption_profile_response_model_valid(self):
        """Test validation with valid response data."""
        data = DecryptionProfileResponseFactory().model_dump()
        model = DecryptionProfileResponseModel(**data)
        assert isinstance(model.id, UUID)
        assert model.name == data["name"]
        assert model.folder == data["folder"]

    def test_decryption_profile_response_model_from_request(self):
        """Test creation of response model from request data."""
        request_data = DecryptionProfileCreateModelFactory.build_valid()
        request_model = DecryptionProfileCreateModel(**request_data)
        response_data = DecryptionProfileResponseFactory.from_request(request_model)
        model = DecryptionProfileResponseModel(**response_data.model_dump())
        assert isinstance(model.id, UUID)
        assert model.name == request_model.name
        assert model.folder == request_model.folder
        assert model.ssl_protocol_settings == request_model.ssl_protocol_settings

    def test_decryption_profile_response_model_with_snippet(self):
        """Test response model with snippet container."""
        data = DecryptionProfileResponseFactory.with_snippet()
        model = DecryptionProfileResponseModel(**data.model_dump())
        assert model.snippet == "TestSnippet"
        assert model.folder is None
        assert model.device is None

    def test_decryption_profile_response_model_with_device(self):
        """Test response model with device container."""
        data = DecryptionProfileResponseFactory.with_device()
        model = DecryptionProfileResponseModel(**data.model_dump())
        assert model.device == "TestDevice"
        assert model.folder is None
        assert model.snippet is None


class TestExtraFieldsForbidden:
    """Tests for extra='forbid' validation on all models."""

    def test_create_model_rejects_extra_fields(self):
        """Test that extra fields are rejected in CreateModel."""
        data = DecryptionProfileCreateModelFactory.build_valid()
        data["unknown_field"] = "should_fail"
        with pytest.raises(ValidationError) as exc_info:
            DecryptionProfileCreateModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_update_model_rejects_extra_fields(self):
        """Test that extra fields are rejected in UpdateModel."""
        data = DecryptionProfileUpdateModelFactory.build_valid()
        data["unknown_field"] = "should_fail"
        with pytest.raises(ValidationError) as exc_info:
            DecryptionProfileUpdateModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_response_model_ignores_extra_fields(self):
        """Test that extra fields are silently ignored in ResponseModel."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestProfile",
            "folder": "Texas",
            "unknown_field": "should_be_ignored",
        }
        model = DecryptionProfileResponseModel(**data)
        assert not hasattr(model, "unknown_field")

    def test_ssl_protocol_settings_rejects_extra_fields(self):
        """Test that extra fields are rejected in SSLProtocolSettings."""
        from scm.models.security.decryption_profiles import SSLProtocolSettings

        data = {
            "min_version": "tls1-0",
            "max_version": "tls1-2",
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            SSLProtocolSettings(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_ssl_forward_proxy_rejects_extra_fields(self):
        """Test that extra fields are rejected in SSLForwardProxy."""
        from scm.models.security.decryption_profiles import SSLForwardProxy

        data = {
            "block_client_cert": True,
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            SSLForwardProxy(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_ssl_inbound_proxy_rejects_extra_fields(self):
        """Test that extra fields are rejected in SSLInboundProxy."""
        from scm.models.security.decryption_profiles import SSLInboundProxy

        data = {
            "block_if_hsm_unavailable": True,
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            SSLInboundProxy(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_ssl_no_proxy_rejects_extra_fields(self):
        """Test that extra fields are rejected in SSLNoProxy."""
        from scm.models.security.decryption_profiles import SSLNoProxy

        data = {
            "block_expired_certificate": True,
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            SSLNoProxy(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestSSLVersionEnum:
    """Tests for SSLVersion enum values."""

    def test_all_ssl_version_values(self):
        """Test all SSLVersion enum values."""
        from scm.models.security.decryption_profiles import SSLProtocolSettings

        versions = ["sslv3", "tls1-0", "tls1-1", "tls1-2", "tls1-3", "max"]
        for version in versions:
            # Test max_version accepts all values
            settings = SSLProtocolSettings(
                min_version="sslv3",
                max_version=version,
            )
            assert settings.max_version.value == version

    def test_ssl_version_enum_members(self):
        """Test that SSLVersion enum has all expected members."""
        expected = {"sslv3", "tls1_0", "tls1_1", "tls1_2", "tls1_3", "max"}
        actual = {v.name for v in SSLVersion}
        assert expected == actual


# -------------------- End of Test Classes --------------------
