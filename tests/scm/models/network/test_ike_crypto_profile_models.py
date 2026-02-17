"""Test models for IKE crypto profiles."""

from uuid import UUID

from pydantic import ValidationError
import pytest

from scm.models.network import (
    DHGroup,
    EncryptionAlgorithm,
    HashAlgorithm,
    IKECryptoProfileCreateModel,
    IKECryptoProfileResponseModel,
    IKECryptoProfileUpdateModel,
)


class TestIKECryptoProfileModels:
    """Test IKE crypto profile models."""

    def test_create_model_validation(self):
        """Test validation of IKECryptoProfileCreateModel."""
        # Test valid model
        valid_data = {
            "name": "test-profile",
            "hash": ["sha1", "sha256"],
            "encryption": ["aes-128-cbc", "aes-256-cbc"],
            "dh_group": ["group2", "group5"],
            "folder": "test-folder",
        }
        profile = IKECryptoProfileCreateModel(**valid_data)
        assert profile.name == "test-profile"
        assert HashAlgorithm.SHA1 in profile.hash
        assert HashAlgorithm.SHA256 in profile.hash
        assert EncryptionAlgorithm.AES_128_CBC in profile.encryption
        assert EncryptionAlgorithm.AES_256_CBC in profile.encryption
        assert DHGroup.GROUP2 in profile.dh_group
        assert DHGroup.GROUP5 in profile.dh_group
        assert profile.folder == "test-folder"

        # Test with seconds lifetime
        valid_with_seconds = valid_data.copy()
        valid_with_seconds["lifetime"] = {"seconds": 300}
        profile = IKECryptoProfileCreateModel(**valid_with_seconds)
        assert profile.lifetime.seconds == 300

        # Test with minutes lifetime
        valid_with_minutes = valid_data.copy()
        valid_with_minutes["lifetime"] = {"minutes": 10}
        profile = IKECryptoProfileCreateModel(**valid_with_minutes)
        assert profile.lifetime.minutes == 10

        # Test with hours lifetime
        valid_with_hours = valid_data.copy()
        valid_with_hours["lifetime"] = {"hours": 2}
        profile = IKECryptoProfileCreateModel(**valid_with_hours)
        assert profile.lifetime.hours == 2

        # Test with days lifetime
        valid_with_days = valid_data.copy()
        valid_with_days["lifetime"] = {"days": 30}
        profile = IKECryptoProfileCreateModel(**valid_with_days)
        assert profile.lifetime.days == 30

        # Test invalid seconds lifetime (below min)
        invalid_seconds = valid_data.copy()
        invalid_seconds["lifetime"] = {"seconds": 179}
        with pytest.raises(ValidationError):
            IKECryptoProfileCreateModel(**invalid_seconds)

        # Test invalid seconds lifetime (above max)
        invalid_seconds = valid_data.copy()
        invalid_seconds["lifetime"] = {"seconds": 65536}
        with pytest.raises(ValidationError):
            IKECryptoProfileCreateModel(**invalid_seconds)

        # Test invalid container (multiple containers)
        invalid_container = valid_data.copy()
        invalid_container["snippet"] = "test-snippet"
        with pytest.raises(ValidationError):
            IKECryptoProfileCreateModel(**invalid_container)

        # Test invalid container (no container)
        invalid_container = {
            "name": "test-profile",
            "hash": ["sha1", "sha256"],
            "encryption": ["aes-128-cbc", "aes-256-cbc"],
            "dh_group": ["group2", "group5"],
        }
        with pytest.raises(ValidationError):
            IKECryptoProfileCreateModel(**invalid_container)

        # Test invalid name (too long)
        invalid_name = valid_data.copy()
        invalid_name["name"] = "x" * 32
        with pytest.raises(ValidationError):
            IKECryptoProfileCreateModel(**invalid_name)

        # Test invalid name (invalid character)
        invalid_name = valid_data.copy()
        invalid_name["name"] = "test@profile"
        with pytest.raises(ValidationError):
            IKECryptoProfileCreateModel(**invalid_name)

        # Test invalid authentication_multiple
        invalid_auth = valid_data.copy()
        invalid_auth["authentication_multiple"] = 51
        with pytest.raises(ValidationError):
            IKECryptoProfileCreateModel(**invalid_auth)

    def test_update_model_validation(self):
        """Test validation of IKECryptoProfileUpdateModel."""
        # Test valid model
        valid_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-profile",
            "hash": ["sha1", "sha256"],
            "encryption": ["aes-128-cbc", "aes-256-cbc"],
            "dh_group": ["group2", "group5"],
            "folder": "test-folder",
        }
        profile = IKECryptoProfileUpdateModel(**valid_data)
        assert profile.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert profile.name == "test-profile"
        assert HashAlgorithm.SHA1 in profile.hash
        assert HashAlgorithm.SHA256 in profile.hash
        assert profile.folder == "test-folder"

        # Test invalid ID
        invalid_id = valid_data.copy()
        invalid_id["id"] = "not-a-uuid"
        with pytest.raises(ValidationError):
            IKECryptoProfileUpdateModel(**invalid_id)

    def test_response_model_validation(self):
        """Test validation of IKECryptoProfileResponseModel."""
        # Test valid model
        valid_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-profile",
            "hash": ["sha1", "sha256"],
            "encryption": ["aes-128-cbc", "aes-256-cbc"],
            "dh_group": ["group2", "group5"],
            "folder": "test-folder",
        }
        profile = IKECryptoProfileResponseModel(**valid_data)
        assert profile.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert profile.name == "test-profile"
        assert HashAlgorithm.SHA1 in profile.hash
        assert HashAlgorithm.SHA256 in profile.hash
        assert profile.folder == "test-folder"

        # Test missing required ID
        invalid_data = {
            "name": "test-profile",
            "hash": ["sha1", "sha256"],
            "encryption": ["aes-128-cbc", "aes-256-cbc"],
            "dh_group": ["group2", "group5"],
            "folder": "test-folder",
        }
        with pytest.raises(ValidationError):
            IKECryptoProfileResponseModel(**invalid_data)

    def test_create_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on CreateModel."""
        data = {
            "name": "test-profile",
            "hash": ["sha1"],
            "encryption": ["aes-128-cbc"],
            "dh_group": ["group2"],
            "folder": "test-folder",
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            IKECryptoProfileCreateModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_update_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on UpdateModel."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-profile",
            "hash": ["sha1"],
            "encryption": ["aes-128-cbc"],
            "dh_group": ["group2"],
            "folder": "test-folder",
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            IKECryptoProfileUpdateModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_response_model_extra_fields_ignored(self):
        """Test that extra fields are silently ignored on ResponseModel."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-profile",
            "hash": ["sha1"],
            "encryption": ["aes-128-cbc"],
            "dh_group": ["group2"],
            "folder": "test-folder",
            "unknown_field": "should_be_ignored",
        }
        model = IKECryptoProfileResponseModel(**data)
        assert not hasattr(model, "unknown_field")

    def test_non_auth_hash_algorithm(self):
        """Test that non-auth hash algorithm is supported."""
        data = {
            "name": "test-profile",
            "hash": ["non-auth"],
            "encryption": ["aes-128-cbc"],
            "dh_group": ["group2"],
            "folder": "test-folder",
        }
        profile = IKECryptoProfileCreateModel(**data)
        assert HashAlgorithm.NON_AUTH in profile.hash
