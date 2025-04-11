"""Test models for IKE crypto profiles."""

from uuid import UUID

import pytest
from pydantic import ValidationError

from scm.models.network import (DHGroup, EncryptionAlgorithm, HashAlgorithm,
                                IKECryptoProfileCreateModel,
                                IKECryptoProfileResponseModel,
                                IKECryptoProfileUpdateModel)


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

        # Test description is excluded from model fields but still accessible
        assert profile.model_fields["description"].exclude is True

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

    def test_description_in_update_model(self):
        """Test description field in update model but not in response model."""
        # The update model should accept description field
        update_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-profile",
            "description": "This is a test description",
            "hash": ["sha1", "sha256"],
            "encryption": ["aes-128-cbc", "aes-256-cbc"],
            "dh_group": ["group2", "group5"],
            "folder": "test-folder",
        }
        # This should not raise an error - description should be accepted
        update_model = IKECryptoProfileUpdateModel(**update_data)
        assert update_model.description == "This is a test description"

        # Response model has description field, but it's excluded from serialization
        response_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-profile",
            "hash": ["sha1", "sha256"],
            "encryption": ["aes-128-cbc", "aes-256-cbc"],
            "dh_group": ["group2", "group5"],
            "folder": "test-folder",
        }
        response_model = IKECryptoProfileResponseModel(**response_data)
        assert hasattr(response_model, "description")
        assert response_model.description is None
        assert response_model.model_fields["description"].exclude is True
        # Ensure description is excluded when serializing to dict
        model_dict = response_model.model_dump()
        assert "description" not in model_dict
