# tests/scm/models/identity/test_tls_service_profile_models.py

"""Tests for TLS service profile identity models."""

# External libraries
from pydantic import ValidationError
import pytest

# Local SDK imports
from scm.models.identity.tls_service_profiles import (
    TlsServiceProfileCreateModel,
    TlsServiceProfileResponseModel,
    TlsServiceProfileUpdateModel,
    TlsProtocolSettings,
    TlsVersion,
)
from tests.factories.identity.tls_service_profile import (
    TlsServiceProfileCreateModelFactory,
    TlsServiceProfileUpdateModelFactory,
)

# -------------------- Test Classes for Pydantic Models --------------------


class TestTlsVersion:
    """Tests for the TlsVersion enumeration."""

    def test_tls_version_tls1_0(self):
        """Test TLS 1.0 enum value."""
        assert TlsVersion.tls1_0 == "tls1-0"

    def test_tls_version_tls1_1(self):
        """Test TLS 1.1 enum value."""
        assert TlsVersion.tls1_1 == "tls1-1"

    def test_tls_version_tls1_2(self):
        """Test TLS 1.2 enum value."""
        assert TlsVersion.tls1_2 == "tls1-2"

    def test_tls_version_tls1_3(self):
        """Test TLS 1.3 enum value."""
        assert TlsVersion.tls1_3 == "tls1-3"

    def test_tls_version_invalid(self):
        """Test that invalid TLS version raises ValueError."""
        with pytest.raises(ValueError):
            TlsVersion("tls2-0")


class TestTlsProtocolSettings:
    """Tests for TlsProtocolSettings component model."""

    def test_protocol_settings_valid(self):
        """Test valid protocol settings configuration."""
        model = TlsProtocolSettings(
            min_version=TlsVersion.tls1_2,
            max_version=TlsVersion.tls1_3,
            keyxchg_algo_ecdhe=True,
            enc_algo_aes_256_gcm=True,
            auth_algo_sha256=True,
        )
        assert model.min_version == TlsVersion.tls1_2
        assert model.max_version == TlsVersion.tls1_3
        assert model.keyxchg_algo_ecdhe is True
        assert model.enc_algo_aes_256_gcm is True
        assert model.auth_algo_sha256 is True

    def test_protocol_settings_empty(self):
        """Test that protocol settings can be empty."""
        model = TlsProtocolSettings()
        assert model.min_version is None
        assert model.max_version is None

    def test_protocol_settings_all_algorithms(self):
        """Test protocol settings with all algorithm options."""
        model = TlsProtocolSettings(
            keyxchg_algo_rsa=True,
            keyxchg_algo_dhe=True,
            keyxchg_algo_ecdhe=True,
            enc_algo_3des=False,
            enc_algo_rc4=False,
            enc_algo_aes_128_cbc=True,
            enc_algo_aes_256_cbc=True,
            enc_algo_aes_128_gcm=True,
            enc_algo_aes_256_gcm=True,
            auth_algo_sha1=False,
            auth_algo_sha256=True,
            auth_algo_sha384=True,
        )
        assert model.keyxchg_algo_rsa is True
        assert model.enc_algo_3des is False
        assert model.auth_algo_sha384 is True

    def test_protocol_settings_rejects_extra_fields(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TlsProtocolSettings(unknown_algo=True)
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestTlsServiceProfileCreateModel:
    """Tests for TlsServiceProfileCreateModel validation."""

    def test_create_model_valid(self):
        """Test validation with valid data."""
        data = TlsServiceProfileCreateModelFactory.build_valid()
        model = TlsServiceProfileCreateModel(**data)
        assert model.name == data["name"]
        assert model.folder == data["folder"]
        assert model.certificate == data["certificate"]

    def test_create_model_with_protocol_settings(self):
        """Test validation with protocol settings."""
        data = TlsServiceProfileCreateModelFactory.build_valid(
            protocol_settings={
                "min_version": "tls1-2",
                "max_version": "tls1-3",
            }
        )
        model = TlsServiceProfileCreateModel(**data)
        assert model.protocol_settings is not None
        assert isinstance(model.protocol_settings, TlsProtocolSettings)
        assert model.protocol_settings.min_version == TlsVersion.tls1_2

    def test_create_model_multiple_containers(self):
        """Test validation when multiple containers are provided."""
        data = TlsServiceProfileCreateModelFactory.build_with_multiple_containers()
        with pytest.raises(ValueError) as exc_info:
            TlsServiceProfileCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_create_model_no_container(self):
        """Test validation when no container is provided."""
        data = TlsServiceProfileCreateModelFactory.build_with_no_container()
        with pytest.raises(ValueError) as exc_info:
            TlsServiceProfileCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_create_model_name_too_long(self):
        """Test validation with name exceeding max length."""
        data = TlsServiceProfileCreateModelFactory.build_valid(name="a" * 128)
        with pytest.raises(ValidationError) as exc_info:
            TlsServiceProfileCreateModel(**data)
        assert "String should have at most 127 characters" in str(exc_info.value)

    def test_create_model_name_invalid_characters(self):
        """Test validation with invalid characters in name."""
        data = TlsServiceProfileCreateModelFactory.build_valid(name="invalid name!")
        with pytest.raises(ValidationError) as exc_info:
            TlsServiceProfileCreateModel(**data)
        assert "String should match pattern" in str(exc_info.value)


class TestTlsServiceProfileUpdateModel:
    """Tests for TlsServiceProfileUpdateModel validation."""

    def test_update_model_valid(self):
        """Test validation with valid update data."""
        data = TlsServiceProfileUpdateModelFactory.build_valid()
        model = TlsServiceProfileUpdateModel(**data)
        assert model.name == data["name"]
        assert str(model.id) == data["id"]

    def test_update_model_invalid_uuid(self):
        """Test validation with invalid UUID format."""
        data = TlsServiceProfileUpdateModelFactory.build_valid(id="invalid-uuid")
        with pytest.raises(ValidationError) as exc_info:
            TlsServiceProfileUpdateModel(**data)
        assert "Input should be a valid UUID" in str(exc_info.value)


class TestTlsServiceProfileResponseModel:
    """Tests for TlsServiceProfileResponseModel validation."""

    def test_response_model_valid(self):
        """Test validation with valid response data."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestProfile",
            "certificate": "test-cert",
            "folder": "Texas",
        }
        model = TlsServiceProfileResponseModel(**data)
        assert str(model.id) == data["id"]
        assert model.name == data["name"]
        assert model.folder == data["folder"]

    def test_response_model_invalid_uuid(self):
        """Test validation with invalid UUID format."""
        data = {
            "id": "invalid-uuid",
            "name": "TestProfile",
            "certificate": "test-cert",
            "folder": "Texas",
        }
        with pytest.raises(ValidationError) as exc_info:
            TlsServiceProfileResponseModel(**data)
        assert "Input should be a valid UUID" in str(exc_info.value)

    def test_response_model_ignores_extra_fields(self):
        """Test that extra fields are silently ignored in ResponseModel."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestProfile",
            "certificate": "test-cert",
            "folder": "Texas",
            "unknown_field": "should_be_ignored",
        }
        model = TlsServiceProfileResponseModel(**data)
        assert not hasattr(model, "unknown_field")


# -------------------- End of Test Classes --------------------
